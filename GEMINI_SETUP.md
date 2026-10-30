# Direct Gemini setup

This project now calls Google's official Gemini API, not the former class proxy.

1. Create a Gemini API key in https://aistudio.google.com/api-keys and put it in the local `.env` or your host's secret settings as `GOOGLE_API_KEY`.
2. Do not reuse the former `GEMINI_API_KEY` proxy token. Old `PROXY_BASE_URL`, `CHAT_MODEL` and proxy model variables are ignored. Optional overrides are `GOOGLE_CHAT_MODEL` and `GOOGLE_EMBED_MODEL`.
3. Default chat: `gemini-3.5-flash-lite`; text embeddings: `gemini-embedding-001`. See https://ai.google.dev/gemini-api/docs/openai.
4. Run `python ingest.py` once after adding the key. Indexing sends the selected loan document's extracted text to Google. The new collection is named with the Google embedding model and index version; the previous collection is not deleted or reused.
5. Then run `python app.py` and ask one in-scope question. For new document versions, change `GOOGLE_INDEX_VERSION` before indexing. Never mix embeddings from different models.

Without the direct Google key, offline tests still run but live model requests cannot complete. A successful test using mocks does not prove provider credentials, quota or live model availability.
