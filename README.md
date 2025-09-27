# 🎥 Lecture Navigator — Jump-to-Timestamp Agent

> Long lectures slow down doubt resolution; this project ingests video transcripts, embeds them, and lets you **search and jump directly to relevant timestamps** with a brief AI-generated answer.

---

## 🚀 Features
- Transcript ingestion (YouTube/SubRip/VTT or Whisper fallback).
- Segment into overlapping chunks with timestamps.
- Semantic search + reranking → top-3 timestamps.
- AI answer generation using OpenAI (fallback to local embeddings).
- React frontend with YouTube mini-player.

---

## 📂 Project Structure
- **backend/** → FastAPI app with LangChain, vector store, embeddings.
- **frontend/** → React + Vite app for UI, player, and search.
- **docs/** → Architecture diagram, Postman collection.

---

## ⚙️ Setup Instructions

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
