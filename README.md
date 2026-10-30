---
title: Loan Terms Assistant
sdk: gradio
emoji: 💬
colorFrom: blue
colorTo: indigo
python_version: 3.11
---

# Loan Terms Assistant

This project is a scoped AI assistant that answers questions about one real bank loan PDF and refuses everything else.

## Setup

1. Create a `.env` file in the project root with the provider API key, or add `GOOGLE_API_KEY` as a Hugging Face secret:

```env
GOOGLE_API_KEY=your_key_here
```

2. Install dependencies:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

3. Make sure the chosen document is available at `docs/loan_terms.pdf`.

## Build the index

```powershell
.\.venv\Scripts\python.exe ingest.py
```

## Run the chat app

```powershell
.\.venv\Scripts\python.exe app.py
```

## Quick smoke test

```powershell
.\.venv\Scripts\python.exe agent.py
```

## Official Gemini migration

Follow [GEMINI_SETUP.md](GEMINI_SETUP.md). Rebuild the document index into its new Google collection before live use. Existing proxy embeddings are preserved and are not queried by the new setup.
