from app.rag_engine import rag_engine


def test_chroma_vector_search_retrieves_wifi_article_for_paraphrase():
    results = rag_engine.retrieve(
        "My laptop won't connect to campus internet after my password change."
    )

    assert rag_engine.chroma_active
    assert results[0]["kb_id"] == "KB0010312"
    assert 0.0 <= results[0]["similarity_score"] <= 1.0


def test_retrieve_returns_no_results_for_non_positive_top_k():
    assert rag_engine.retrieve("eduroam connection", top_k=0) == []
