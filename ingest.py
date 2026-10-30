from pathlib import Path

from pypdf import PdfReader
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

import config
from gem import embed
from store import make_client


def load_chunks(pdf_path: Path, size: int = 900, overlap: int = 150):
    """Read the PDF and cut each page into small overlapping pieces."""
    if size <= 0 or overlap < 0 or overlap >= size:
        raise ValueError("Require size > overlap >= 0")
    reader = PdfReader(str(pdf_path))
    chunks = []
    for page_no, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        if not text:
            continue
        start = 0
        while start < len(text):
            piece = text[start : start + size]
            chunks.append({"text": piece, "page": page_no})
            start += size - overlap
    return chunks


def resolve_pdf_path() -> Path:
    candidates = [config.PDF_PATH, config.ROOT_PDF_PATH, config.DOCS_DIR]
    for candidate in candidates:
        if candidate.is_file():
            return candidate

    raise FileNotFoundError(
        "Missing PDF. Add the chosen loan document as docs/loan_terms.pdf "
        "or as loan_terms.pdf in the repo root."
    )


def main():
    pdf_path = resolve_pdf_path()
    chunks = load_chunks(pdf_path)
    print(f"Loaded {len(chunks)} chunks from {pdf_path}")

    if not chunks:
        raise ValueError("The PDF contains no extractable text")
    dim = len(embed("dimension probe"))
    print(f"Embedding size = {dim}")

    client = make_client()
    try:
        client.recreate_collection(
            collection_name=config.COLLECTION,
            vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
        )

        points = []
        for i, chunk in enumerate(chunks):
            points.append(
                PointStruct(
                    id=i,
                    vector=embed(chunk["text"]),
                    payload={
                        "text": chunk["text"],
                        "page": chunk["page"],
                        "chunk": i,
                    },
                )
            )

        client.upsert(collection_name=config.COLLECTION, points=points)
        print(f"Stored {len(points)} clauses in Qdrant. The document is ready.")
    finally:
        client.close()


if __name__ == "__main__":
    main()
