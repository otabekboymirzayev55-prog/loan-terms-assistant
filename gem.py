# gem.py - talks to the class proxy with retry on rate limit
import time
import requests
import config


def _post_with_retry(url, headers, body, retries=5):
    """Retry up to 5 times if we hit a rate limit (429)."""
    for attempt in range(retries):
        r = requests.post(url, headers=headers, json=body)
        if r.status_code == 429:
            wait = 10 * (attempt + 1)  # wait 10s, 20s, 30s ...
            print(f"Rate limited. Waiting {wait}s before retry {attempt + 1}/{retries}...")
            time.sleep(wait)
            continue
        r.raise_for_status()
        return r
    raise RuntimeError("Too many retries — proxy is busy. Try again in a minute.")


def chat(prompt: str) -> str:
    url = "https://saidazam-litellm-proxy.hf.space/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {config.GEMINI_API_KEY}",
        "Content-Type": "application/json",
    }
    body = {
        "model": "gemini-flash-lite",
        "messages": [{"role": "user", "content": prompt}],
    }
    r = _post_with_retry(url, headers, body)
    return r.json()["choices"][0]["message"]["content"].strip()


def embed(text: str):
    url = "https://saidazam-litellm-proxy.hf.space/v1/embeddings"
    headers = {
        "Authorization": f"Bearer {config.GEMINI_API_KEY}",
        "Content-Type": "application/json",
    }
    body = {
        "model": "gemini-embedding",
        "input": text,
    }
    time.sleep(0.5)  # small pause between every embed call
    r = _post_with_retry(url, headers, body)
    return r.json()["data"][0]["embedding"]
