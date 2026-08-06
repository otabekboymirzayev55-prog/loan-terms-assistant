from gem import chat


ANSWER_PROMPT = """You answer questions about a bank loan's Terms & Conditions.
Use ONLY the context below. Do not use outside knowledge.

If the answer is NOT clearly in the context, reply exactly:
"Not stated in the terms."

When you do answer, quote the exact number / fee / rule and add the page, e.g. (p. 3).

Context:
{context}

Question: {q}
Answer:"""


def write_answer(question, chunks):
    if not chunks:
        return "Not stated in the terms."

    context = "\n\n".join(f"[p. {c['page']}] {c['text']}" for c in chunks)
    answer = chat(ANSWER_PROMPT.format(context=context, q=question)).strip()
    if not answer:
        return "Not stated in the terms."
    if answer.lower().startswith("not stated"):
        return "Not stated in the terms."
    return answer
