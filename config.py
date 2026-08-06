from pathlib import Path
import os

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    GEMINI_API_KEY = os.getenv("HF_SECRET_GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is missing. Add it as a secret or in .env.")

IS_SPACE = bool(os.getenv("SPACE_ID") or os.getenv("SPACE_REPOSITORY"))

# All model calls go through the class proxy.
PROXY_BASE = "https://saidazam-litellm-proxy.hf.space/gemini"

# The proxy only allows these two models.
CHAT_MODEL  = "gemini-flash-lite"
EMBED_MODEL = "gemini-embedding"

# Local storage.
QDRANT_PATH = BASE_DIR / "qdrant_data"
COLLECTION = "loan_terms"

# The chosen bank document.
DOCS_DIR = BASE_DIR / "docs"
PDF_PATH = DOCS_DIR / "loan_terms.pdf"
ROOT_PDF_PATH = BASE_DIR / "loan_terms.pdf"


# Retrieval settings.
TOP_K = 5

# The only topic this assistant may answer about.
SCOPE = (
    "the terms and conditions of this specific bank loan / credit product: "
    "interest rate, fees, repayment schedule, penalties, eligibility, and "
    "what the contract does or does not include"
)
