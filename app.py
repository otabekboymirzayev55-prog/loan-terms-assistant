import os
import gradio as gr

from agent import ask


def respond(message, history):
    try:
        return ask(message)
    except Exception:
        return "The document service is unavailable. Please try again later."


demo = gr.ChatInterface(
    fn=respond,
    title="Loan Terms Assistant (scoped & secure)",
    description=(
        "Ask only about this loan product's terms. Off-topic questions are refused."
    ),
    examples=[
        "What is the late-payment penalty?",
        "What is the interest rate?",
        "Write me a poem about the moon.",
    ],
)


if __name__ == "__main__":
    demo.queue()
    demo.launch(server_name=os.getenv("GRADIO_SERVER_NAME", "127.0.0.1"), server_port=int(os.getenv("PORT", os.getenv("GRADIO_SERVER_PORT", "7860"))))
