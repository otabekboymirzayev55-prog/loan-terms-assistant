# gem.py - talks to the class proxy using direct HTTP calls
import requests
import config


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
    r = requests.post(url, headers=headers, json=body)
    r.raise_for_status()
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
    r = requests.post(url, headers=headers, json=body)
    r.raise_for_status()
    return r.json()["data"][0]["embedding"]
