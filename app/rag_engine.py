"""
RAG & Vector Search Engine for GSU CampusIT Copilot.
"""

import re
from typing import List, Dict, Any, Tuple

from app.config import settings
from app.kb_data import GSU_KB_ARTICLES, get_article_by_id
from app.guardrails import evaluate_escalation

try:
    import chromadb
    from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False

try:
    from google import genai
    GENAI_AVAILABLE = True
except Exception:
    GENAI_AVAILABLE = False

# Only carry context for an explicit follow-up without a newly named service.
SERVICE_TOPIC = re.compile(
    r"\b(duo|mfa|2fa|password|passphrase|campus\s?id|mycampusid|wi-?fi|eduroam|"
    r"wireless|internet|panthermail|outlook|email|vpn|anyconnect|icollege|brightspace|paws)\b",
    re.IGNORECASE,
)
FOLLOW_UP = re.compile(
    r"\b(it|that|this|same|still|again|those|these)\b|"
    r"^(what next|what now|next step|didn['’]?t work|doesn['’]?t work)",
    re.IGNORECASE,
)
SMALL_TALK = re.compile(
    r"^(lol|lmao|haha|ha|hi|hello|hey|thanks|thank you|ok|okay|cool|great)[!.,?\s]*$",
    re.IGNORECASE,
)

def relevant_history(query, conversation_history):
    if SERVICE_TOPIC.search(query) or SMALL_TALK.fullmatch(query.strip()):
        return []
    return (conversation_history or []) if FOLLOW_UP.search(query) else []


class CampusITRAGEngine:
    def __init__(self) -> None:
        self.articles = GSU_KB_ARTICLES
        self.chroma_active = False
        self.collection = None
        self._init_chromadb()

    def _format_article_text(self, article: Dict[str, Any]) -> str:
        steps_str = "\n".join(article["steps"])
        kw_str = " ".join(article["keywords"])
        return f"{article['kb_id']} {article['title']}\nCategory: {article['category']}\nKeywords: {kw_str}\nSummary: {article['summary']}\nSteps:\n{steps_str}\nNotes: {article['notes']}"

    def _init_chromadb(self) -> None:
        if not CHROMA_AVAILABLE:
            raise RuntimeError(
                "ChromaDB is required for vector search. Install dependencies from requirements.txt."
            )
        try:
            client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
            self.collection = client.get_or_create_collection(
                name=settings.COLLECTION_NAME,
                embedding_function=DefaultEmbeddingFunction(),
                metadata={"hnsw:space": "cosine"},
            )
            ids = [a["kb_id"] for a in self.articles]
            docs = [self._format_article_text(a) for a in self.articles]
            metadatas = [{"kb_id": a["kb_id"], "title": a["title"], "category": a["category"], "url": a["url"]} for a in self.articles]
            self.collection.upsert(ids=ids, documents=docs, metadatas=metadatas)
            self.chroma_active = True
        except Exception as exc:
            raise RuntimeError(
                f"Could not initialize ChromaDB vector search at "
                f"{settings.CHROMA_PERSIST_DIR!r}: {exc}"
            ) from exc

    def retrieve(self, query: str, conversation_history: List[Dict[str, str]] | None = None, top_k: int = settings.TOP_K_RESULTS) -> List[Dict[str, Any]]:
        if top_k <= 0:
            return []
        if self.collection is None:
            raise RuntimeError("ChromaDB vector collection is not initialized.")
        effective_query = query
        if relevant_history(query, conversation_history):
            prior_user_msgs = [m["content"] for m in conversation_history[-2:] if m.get("role") == "user"]
            if prior_user_msgs:
                effective_query = f"{prior_user_msgs[-1]} {query}"
        results = self.collection.query(
            query_texts=[effective_query],
            n_results=min(top_k, len(self.articles)),
            include=["distances"],
        )
        article_by_id = {article["kb_id"]: article for article in self.articles}
        result_ids = results["ids"][0]
        distances = results["distances"][0]
        scored_results = []
        for kb_id, distance in zip(result_ids, distances):
            article = article_by_id.get(kb_id)
            if article is None:
                continue
            scored_results.append({
                "kb_id": article["kb_id"],
                "title": article["title"],
                "category": article["category"],
                "url": article["url"],
                "updated": article["updated"],
                "summary": article["summary"],
                "steps": article["steps"],
                "notes": article["notes"],
                "similarity_score": round(max(0.0, 1.0 - distance), 3),
            })
        return scored_results

    def _synthesize_grounded_response(self, user_query: str, retrieved_docs: List[Dict[str, Any]], escalation: Dict[str, Any], conversation_history: List[Dict[str, str]] | None = None) -> Tuple[str, str]:
        primary = retrieved_docs[0] if retrieved_docs else None
        secondary = retrieved_docs[1] if len(retrieved_docs) > 1 and retrieved_docs[1]["similarity_score"] >= 0.30 else None

        if settings.GEMINI_API_KEY and GENAI_AVAILABLE and primary:
            try:
                client = genai.Client(api_key=settings.GEMINI_API_KEY)
                context_blocks = []
                for doc in retrieved_docs[:2]:
                    steps_joined = "\n".join(doc["steps"])
                    context_blocks.append(f"[{doc['kb_id']}] {doc['title']} ({doc['url']})\nSummary: {doc['summary']}\nSteps:\n{steps_joined}\nNotes: {doc['notes']}")
                context_str = "\n\n---\n\n".join(context_blocks)
                prompt = f"You are GSU CampusIT Copilot. Answer using ONLY the provided GSU KB articles. Always cite KB IDs in brackets like [KB0010101].\n\nCONTEXT:\n{context_str}\n\nQUESTION: {user_query}"
                resp = client.models.generate_content(model=settings.GEMINI_MODEL, contents=prompt)
                if resp and resp.text:
                    text = resp.text.strip()
                    if f"[{primary['kb_id']}]" not in text:
                        text += f"\n\n**Source Citation:** [{primary['kb_id']}] — *{primary['title']}*"
                    return text, f"gemini-rag ({settings.GEMINI_MODEL})"
            except Exception:
                pass

        if escalation["should_escalate"]:
            ticket = escalation["ticket"]
            kb_ref = primary["kb_id"] if (primary and primary["similarity_score"] >= 0.22) else "KB0010715"
            kb_obj = get_article_by_id(kb_ref) or get_article_by_id("KB0010715")
            lines = [
                f"### ⚠️ Human IT Support Escalation Required (`{ticket['priority']}`)",
                f"Based on GSU Security guidelines **[{kb_obj['kb_id']}]**, this issue requires **live technician verification**.",
                "",
                f"**Why this was escalated:** {ticket['reason']}",
                "",
                "#### Immediate Recommended Steps:",
                f"1. **Call GSU IIT Technology Service Desk:** Dial **{settings.GSU_HELPDESK_PHONE}**.",
                f"2. **Submit ServiceNow Ticket:** Open [{settings.GSU_PORTAL_URL}]({settings.GSU_PORTAL_URL}) referencing **`{ticket['ticket_id']}`**."
            ]
            return "\n".join(lines), "grounded-rag-synthesizer"

        lines = [
            f"Here are the steps from the bundled support article **[{primary['kb_id']}]** (*{primary['title']}*):",
            "",
            f"**Overview:** {primary['summary']}",
            "",
            "#### Step-by-Step Resolution:"
        ]
        for step in primary["steps"]:
            lines.append(step if re.match(r"^\d+\.\s", step) else f"- {step}")
        lines.extend([
            "",
            f"💡 **Important Note [{primary['kb_id']}]:** {primary['notes']}",
            "",
            f"🔗 **Support portal:** [GSU Technology Support]({settings.GSU_PORTAL_URL})"
        ])
        return "\n".join(lines), "grounded-rag-synthesizer"

    def answer_query(self, user_query: str, conversation_history: List[Dict[str, str]] | None = None) -> Dict[str, Any]:
        if SMALL_TALK.fullmatch(user_query.strip()):
            return {
                "query": user_query,
                "answer": "I can help with GSU IT questions. What issue are you having with Duo, passwords, Wi-Fi, email, VPN, or iCollege?",
                "citations": [], "retrieved_chunks": [], "top_similarity": 0.0,
                "escalated": False, "escalation_details": None,
                "escalation_rule": None, "engine_mode": "conversation-helper",
                "chroma_active": self.chroma_active,
            }
        conversation_history = relevant_history(user_query, conversation_history)
        retrieved = self.retrieve(user_query, conversation_history=conversation_history)
        top_score = retrieved[0]["similarity_score"] if retrieved else 0.0
        escalation = evaluate_escalation(user_query=user_query, top_similarity_score=top_score, conversation_history=conversation_history)
        if escalation["should_escalate"]:
            esc_kb = get_article_by_id("KB0010715")
            if esc_kb and not any(d["kb_id"] == "KB0010715" for d in retrieved):
                retrieved.insert(0, {
                    "kb_id": esc_kb["kb_id"], "title": esc_kb["title"], "category": esc_kb["category"],
                    "url": esc_kb["url"], "updated": esc_kb["updated"], "summary": esc_kb["summary"],
                    "steps": esc_kb["steps"], "notes": esc_kb["notes"], "similarity_score": max(top_score, 0.85)
                })
                retrieved = retrieved[:settings.TOP_K_RESULTS]
        answer_markdown, mode = self._synthesize_grounded_response(user_query=user_query, retrieved_docs=retrieved, escalation=escalation, conversation_history=conversation_history)
        cited_ids = sorted(list(set(re.findall(r"\[(KB\d+)\]", answer_markdown))))
        return {
            "query": user_query,
            "answer": answer_markdown,
            "citations": cited_ids,
            "retrieved_chunks": retrieved,
            "top_similarity": top_score,
            "escalated": escalation["should_escalate"],
            "escalation_details": escalation["ticket"] if escalation["should_escalate"] else None,
            "escalation_rule": escalation["rule_id"],
            "engine_mode": mode,
            "chroma_active": self.chroma_active
        }

rag_engine = CampusITRAGEngine()
