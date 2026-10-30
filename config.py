from pathlib import Path
import os

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# A direct Google AI Studio key. Old proxy credentials are deliberately ignored.
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
CHAT_MODEL = os.getenv("GOOGLE_CHAT_MODEL", "gemini-3.5-flash-lite")
EMBED_MODEL = os.getenv("GOOGLE_EMBED_MODEL", "gemini-embedding-001")
INDEX_VERSION = os.getenv("GOOGLE_INDEX_VERSION", "v1")
IS_SPACE = bool(os.getenv("SPACE_ID") or os.getenv("SPACE_REPOSITORY"))

def require_google_key():
    if not GOOGLE_API_KEY:
        raise RuntimeError("GOOGLE_API_KEY is missing. Add a Google AI Studio key to the server environment.")
    return GOOGLE_API_KEY

# Local storage.
QDRANT_PATH = BASE_DIR / "qdrant_data"
COLLECTION = "loan_terms_google_" + EMBED_MODEL.replace("-", "_") + "_" + INDEX_VERSION
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

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
