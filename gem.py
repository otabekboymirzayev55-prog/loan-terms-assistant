# gem.py - the ONE place that talks to the class proxy.
from google import genai
import requests
import config

# --- Chat (uses the SDK) ---
_chat_client = genai.Client(
    api_key=config.GEMINI_API_KEY,
    http_options={"base_url": config.PROXY_BASE},
)

def chat(prompt: str) -> str:
    r = _chat_client.models.generate_content(model=config.CHAT_MODEL, contents=prompt)
    return (r.text or "").strip()


# --- Embed (calls the proxy directly to avoid SDK routing issues) ---
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