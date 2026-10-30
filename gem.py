"""Bounded calls to the configured OpenAI-compatible model proxy."""
import time
import requests
import config

def _post_with_retry(url, headers, body, retries=2):
    for attempt in range(retries):
        response = requests.post(url, headers=headers, json=body, timeout=(5, 25))
        if response.status_code in {429, 502, 503, 504} and attempt + 1 < retries:
            time.sleep(1)
            continue
        response.raise_for_status()
        return response
    raise RuntimeError('Model provider unavailable')

def _request(endpoint, body):
    headers = {"Authorization": f"Bearer {config.GEMINI_API_KEY}", "Content-Type": "application/json"}
    return _post_with_retry(f"{config.PROXY_BASE}/{endpoint}", headers, body).json()

def chat(prompt):
    return _request('chat/completions', {"model": config.CHAT_MODEL, "messages": [{"role":"user", "content":prompt}]})['choices'][0]['message']['content'].strip()

def embed(text):
    return _request('embeddings', {"model": config.EMBED_MODEL, "input": text})['data'][0]['embedding']
