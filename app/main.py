"""
FastAPI Backend Server for GSU CampusIT Copilot.
"""

import time
from collections import deque
from pathlib import Path
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.config import settings
from app.kb_data import GSU_KB_ARTICLES
from app.rag_engine import rag_engine
from eval.generate_dataset import build_evaluation_dataset
from eval.run_eval import evaluate_dataset

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

TELEMETRY_LOG = deque(maxlen=200)
LATEST_EVAL_SUMMARY = {}

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=2, max_length=1000)
    history: Optional[List[ChatMessage]] = Field(default_factory=list)

class EvalRunRequest(BaseModel):
    sample_size: int = Field(default=120, ge=10, le=200)

@app.get("/api/health")
def health_check() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "chroma_vector_db_active": rag_engine.chroma_active,
        "kb_article_count": len(GSU_KB_ARTICLES)
    }

@app.get("/api/kb")
def list_kb_articles() -> Dict[str, Any]:
    return {"portal_url": settings.GSU_PORTAL_URL, "count": len(GSU_KB_ARTICLES), "articles": GSU_KB_ARTICLES}

@app.post("/api/chat")
def chat_endpoint(req: ChatRequest) -> Dict[str, Any]:
    start_ts = time.perf_counter()
    history_dicts = [{"role": m.role, "content": m.content} for m in (req.history or [])]
    result = rag_engine.answer_query(user_query=req.message, conversation_history=history_dicts)
    latency_ms = round((time.perf_counter() - start_ts) * 1000, 1)
    result["latency_ms"] = latency_ms
    TELEMETRY_LOG.appendleft({
        "timestamp": time.strftime("%H:%M:%S"),
        "query": req.message,
        "top_kb": result["retrieved_chunks"][0]["kb_id"] if result["retrieved_chunks"] else "NONE",
        "similarity": result["top_similarity"],
        "escalated": result["escalated"],
        "escalation_rule": result["escalation_rule"],
        "citations": result["citations"],
        "latency_ms": latency_ms
    })
    return result

@app.post("/api/eval/run")
def run_evaluation_endpoint(req: EvalRunRequest) -> Dict[str, Any]:
    global LATEST_EVAL_SUMMARY
    dataset = build_evaluation_dataset()[:req.sample_size]
    report = evaluate_dataset(dataset)
    LATEST_EVAL_SUMMARY = report
    return report

@app.get("/api/telemetry")
def get_telemetry() -> Dict[str, Any]:
    global LATEST_EVAL_SUMMARY
    if not LATEST_EVAL_SUMMARY:
        dataset = build_evaluation_dataset()
        LATEST_EVAL_SUMMARY = evaluate_dataset(dataset)
    total_queries = len(TELEMETRY_LOG)
    escalated_count = sum(1 for item in TELEMETRY_LOG if item["escalated"])
    avg_sim = round(sum(item["similarity"] for item in TELEMETRY_LOG) / total_queries, 3) if total_queries > 0 else 0.0
    return {
        "total_live_queries": total_queries,
        "live_escalation_rate": round((escalated_count / total_queries) * 100, 1) if total_queries else 0.0,
        "avg_similarity_score": avg_sim,
        "recent_events": list(TELEMETRY_LOG)[:25],
        "benchmark_report": LATEST_EVAL_SUMMARY
    }

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
def serve_spa() -> FileResponse:
    index_path = STATIC_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="Frontend index.html not found.")
    return FileResponse(str(index_path))
