---
title: GSU CampusIT Copilot
emoji: 🐾
colorFrom: blue
colorTo: red
sdk: docker
app_port: 7860
pinned: true
---

# 🐾 GSU CampusIT Copilot — AI Technical Support Assistant

Production RAG IT Support Copilot for Georgia State University (`gsutech.service-now.com/sp`).
Built with Python, FastAPI, ChromaDB Vector Search, Grounded Citations, and Safety Guardrails.

## Retrieval
The seven bundled support articles are embedded with ChromaDB's default `all-MiniLM-L6-v2`
embedding function and indexed in a persistent cosine-similarity collection. User questions
are embedded with the same function and queried against that collection; the closest three
articles are used as grounded answer context. ChromaDB stores its data in `chroma_db/` by
default. Set `CHROMA_PERSIST_DIR` to change the storage location. The embedding model is
downloaded the first time the collection is initialized.

## Quickstart
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 7860
```
