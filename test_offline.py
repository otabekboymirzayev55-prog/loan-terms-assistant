"""Offline regressions: no provider calls and no production index writes."""
import os
os.environ.setdefault('GEMINI_API_KEY', 'offline-test-placeholder')
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch, Mock
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
import config
import retrieve
import verify
import gem
import ingest
import agent

class LoanTests(unittest.TestCase):
    def test_refusal_does_not_touch_index(self):
        with patch.object(agent, 'is_in_scope', return_value=False), patch.object(agent, 'ensure_index') as ensure:
            self.assertEqual(agent.ask('Write a poem'), agent.REFUSAL)
            ensure.assert_not_called()

    def test_missing_index_never_triggers_ingestion(self):
        client=Mock()
        client.collection_exists.return_value=False
        with patch.object(agent, 'make_client', return_value=client), patch.object(agent.ingest, 'main') as ingest_main:
            with self.assertRaises(RuntimeError): agent.ensure_index()
            ingest_main.assert_not_called()

    def test_grounding_fails_closed(self):
        for verdict, expected in [('GROUNDED', True), ('NOT_GROUNDED', False), ('maybe', False), ('', False)]:
            with patch.object(verify, 'chat', return_value=verdict):
                self.assertEqual(verify.is_grounded('Some answer', [{'text':'clause'}]), expected)

    def test_modern_qdrant_retrieval(self):
        with tempfile.TemporaryDirectory() as folder:
            client = QdrantClient(path=folder)
            client.create_collection(config.COLLECTION, vectors_config=VectorParams(size=2, distance=Distance.COSINE))
            client.upsert(config.COLLECTION, points=[PointStruct(id=1, vector=[1.0,0.0], payload={'text':'Test clause', 'page':3})])
            client.close()
            with patch.object(retrieve, '_client', side_effect=lambda: QdrantClient(path=folder)), patch.object(retrieve, 'embed', return_value=[1.0,0.0]):
                self.assertEqual(retrieve.search('test')[0]['page'], 3)

    def test_pdf_chunk_parameters(self):
        with self.assertRaises(ValueError):
            ingest.load_chunks(Path('unused.pdf'), size=10, overlap=10)

    def test_request_has_timeout(self):
        response = Mock(status_code=200)
        with patch.object(gem.requests, 'post', return_value=response) as post:
            gem._post_with_retry('https://example.invalid', {}, {})
            self.assertEqual(post.call_args.kwargs['timeout'], (5,25))

if __name__ == '__main__': unittest.main()
