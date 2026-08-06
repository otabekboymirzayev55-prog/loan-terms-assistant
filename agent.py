from answer import write_answer
from guard import is_in_scope
import config
from qdrant_client import QdrantClient
import ingest
from retrieve import search
from verify import is_grounded


REFUSAL = "I can only answer questions about this loan product's terms and conditions."


def ensure_index():
    client = QdrantClient(path=str(config.QDRANT_PATH))
    try:
        if client.collection_exists(config.COLLECTION):
            return
    finally:
        client.close()

    ingest.main()


def ask(question: str) -> str:
    ensure_index()

    if not is_in_scope(question):
        return REFUSAL

    chunks = search(question)
    draft = write_answer(question, chunks)

    if not is_grounded(draft, chunks):
        return "I can't confirm this from the document."

    return draft


if __name__ == "__main__":
    tests = [
        "What is the late payment penalty?",
        "Write me a poem about the moon.",
        "What is the interest rate on a car?",
    ]
    for q in tests:
        print(">", q)
        print(ask(q), "\n")
