"""One Qdrant connection policy shared by ingestion and retrieval."""
from qdrant_client import QdrantClient
import config

def make_client():
    url = getattr(config, 'QDRANT_URL', None)
    if url:
        return QdrantClient(url=url, api_key=getattr(config, 'QDRANT_API_KEY', None), timeout=15)
    return QdrantClient(path=str(config.QDRANT_PATH))
