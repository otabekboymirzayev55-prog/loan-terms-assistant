from gem import chat
import config


GUARD_PROMPT = """You are a strict topic gate for a bank Loan-Terms assistant.
The assistant may ONLY answer questions about: {scope}.

Decide if the user's question is INSIDE that topic.
Reply with exactly one word: ALLOW or REFUSE.

Rules:
- Advice or opinions ("should I take this loan?") -> REFUSE.
- General knowledge, jokes, coding, other companies -> REFUSE.
- Only factual questions about THIS product's terms -> ALLOW.

User question: {q}
Answer (ALLOW or REFUSE):"""


def is_in_scope(question: str) -> bool:
    output = chat(GUARD_PROMPT.format(scope=config.SCOPE, q=question)).strip().upper()
    return output == "ALLOW"
