from qdrant_client import QdrantClient

import config
from gem import embed
from store import make_client


def _client():
    return make_client()


def search(question: str, k: int = config.TOP_K):
    client = _client()
    try:
        if not client.collection_exists(config.COLLECTION):
            raise RuntimeError(
                "Qdrant collection not found. Run `python ingest.py` before starting the app."
            )

        vector = embed(question)
        response = client.query_points(
            collection_name=config.COLLECTION,
            query=vector,
            limit=k,
        )
        results = []
        for hit in response.points or []:
            payload = hit.payload or {}
            results.append(
                {
                    "text": payload.get("text", ""),
                    "page": payload.get("page", "?"),
                    "score": hit.score,
                }
            )
        return results
    finally:
        client.close()
