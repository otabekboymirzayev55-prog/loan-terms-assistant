"""Offline regressions: no provider calls and no production index writes."""
import os
os.environ.setdefault('GOOGLE_API_KEY', 'offline-test-placeholder')
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
import store

class LoanTests(unittest.TestCase):
    def test_failed_embedding_does_not_create_empty_index(self):
        client = Mock()
        client.collection_exists.return_value = False
        with patch.object(ingest, 'resolve_pdf_path', return_value=Path('test.pdf')), patch.object(ingest, 'load_chunks', return_value=[{'text':'clause', 'page':1}]), patch.object(ingest, 'make_client', return_value=client), patch.object(ingest, 'embed', side_effect=RuntimeError('provider unavailable')):
            with self.assertRaises(RuntimeError): ingest.main()
        client.create_collection.assert_not_called()
        client.upsert.assert_not_called()
        client.close.assert_called_once()

    def test_explicit_local_storage_does_not_contact_cloud(self):
        with patch.dict(os.environ, {'QDRANT_STORAGE':'local'}), patch.object(config, 'QDRANT_URL', 'https://example.invalid'), patch.object(store, 'QdrantClient') as client:
            store.make_client()
            client.assert_called_once_with(path=str(config.QDRANT_PATH))

    def test_only_direct_key_and_official_endpoint(self):
        with patch.object(config, 'GOOGLE_API_KEY', None), patch.object(gem.requests, 'post') as post:
            with self.assertRaises(RuntimeError): gem.chat('test')
            post.assert_not_called()
        response = Mock()
        response.json.return_value = {'choices':[{'message':{'content':'OK'}}]}
        with patch.object(config, 'GOOGLE_API_KEY', 'test-google-key'), patch.object(gem, '_post_with_retry', return_value=response) as post:
            self.assertEqual(gem.chat('test'), 'OK')
            url, headers, body = post.call_args.args
            self.assertEqual(url, 'https://generativelanguage.googleapis.com/v1beta/openai/chat/completions')
            self.assertEqual(headers['Authorization'], 'Bearer test-google-key')
            self.assertEqual(body['model'], 'gemini-3.5-flash-lite')

    def test_embedding_contract_and_separate_collection(self):
        response = Mock()
        response.json.return_value = {'data':[{'embedding':[0.1,0.2]}]}
        with patch.object(config, 'GOOGLE_API_KEY', 'test-google-key'), patch.object(gem, '_post_with_retry', return_value=response) as post:
            self.assertEqual(gem.embed('text'), [0.1,0.2])
            url, headers, body = post.call_args.args
            self.assertTrue(url.endswith('/openai/embeddings'))
            self.assertEqual(body['model'], 'gemini-embedding-001')
            self.assertEqual(body['input'], 'text')
        self.assertTrue(config.COLLECTION.startswith('loan_terms_google_'))

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
