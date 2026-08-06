from pathlib import Path

from pypdf import PdfReader
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

import config
from gem import embed


def load_chunks(pdf_path: Path, size: int = 900, overlap: int = 150):
    """Read the PDF and cut each page into small overlapping pieces."""
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


def main():
    if not config.PDF_PATH.exists():
        raise FileNotFoundError(
            f"Missing PDF: {config.PDF_PATH}. Put the chosen loan document there first."
        )

    chunks = load_chunks(config.PDF_PATH)
    print(f"Loaded {len(chunks)} chunks from {config.PDF_PATH}")

    dim = len(embed("dimension probe"))
    print(f"Embedding size = {dim}")

    client = QdrantClient(path=str(config.QDRANT_PATH))
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
