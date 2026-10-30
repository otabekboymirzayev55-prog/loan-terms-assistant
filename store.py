"""One Qdrant connection policy shared by ingestion and retrieval."""
import os
from qdrant_client import QdrantClient
import config

def make_client():
    mode = os.getenv('QDRANT_STORAGE', 'auto')
    if mode not in {'auto', 'local', 'cloud'}:
        raise ValueError('QDRANT_STORAGE must be auto, local or cloud')
    url = getattr(config, 'QDRANT_URL', None) if mode != 'local' else None
    if mode == 'cloud' and not url:
        raise RuntimeError('QDRANT_URL is required for cloud storage')
    if url:
        return QdrantClient(url=url, api_key=getattr(config, 'QDRANT_API_KEY', None), timeout=15)
    return QdrantClient(path=str(config.QDRANT_PATH))
