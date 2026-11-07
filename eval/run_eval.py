"""
Automated Evaluation Harness for GSU CampusIT Copilot.
"""

import json
import sys
import time
from pathlib import Path
from typing import List, Dict, Any

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.rag_engine import rag_engine
from eval.generate_dataset import build_evaluation_dataset

def evaluate_dataset(dataset: List[Dict[str, Any]]) -> Dict[str, Any]:
    start_time = time.perf_counter()
    total = len(dataset)
    retrieval_hits_top1, retrieval_hits_top3, citation_hits = 0, 0, 0
    tp_esc, tn_esc, fp_esc, fn_esc = 0, 0, 0, 0
    category_breakdown = {}
    sample_results = []

    for item in dataset:
        cat = item["category"]
        if cat not in category_breakdown:
            category_breakdown[cat] = {"total": 0, "retrieval_hits": 0, "citation_hits": 0, "escalation_correct": 0}
        category_breakdown[cat]["total"] += 1

        res = rag_engine.answer_query(item["question"])
        retrieved_ids = [chunk["kb_id"] for chunk in res["retrieved_chunks"]]
        expected_kb = item["expected_kb"]

        hit_top1 = len(retrieved_ids) > 0 and retrieved_ids[0] == expected_kb
        hit_top3 = expected_kb in retrieved_ids
        cited_correctly = expected_kb in res["citations"]

        if hit_top1: retrieval_hits_top1 += 1
        if hit_top3:
            retrieval_hits_top3 += 1
            category_breakdown[cat]["retrieval_hits"] += 1
        if cited_correctly:
            citation_hits += 1
            category_breakdown[cat]["citation_hits"] += 1

        expect_esc, actual_esc = item["expect_escalation"], res["escalated"]
        if expect_esc and actual_esc:
            tp_esc += 1
            category_breakdown[cat]["escalation_correct"] += 1
        elif not expect_esc and not actual_esc:
            tn_esc += 1
            category_breakdown[cat]["escalation_correct"] += 1
        elif not expect_esc and actual_esc:
            fp_esc += 1
        elif expect_esc and not actual_esc:
            fn_esc += 1

        if len(sample_results) < 25:
            sample_results.append({
                "id": item["id"], "category": cat, "question": item["question"],
                "expected_kb": expected_kb, "retrieved_top1": retrieved_ids[0] if retrieved_ids else "NONE",
                "expect_escalation": expect_esc, "actual_escalation": actual_esc,
                "passed": hit_top3 and cited_correctly and (expect_esc == actual_esc)
            })

    elapsed_sec = round(time.perf_counter() - start_time, 2)
    esc_precision = (tp_esc / (tp_esc + fp_esc)) if (tp_esc + fp_esc) > 0 else 1.0
    esc_recall = (tp_esc / (tp_esc + fn_esc)) if (tp_esc + fn_esc) > 0 else 1.0
    esc_accuracy = (tp_esc + tn_esc) / total if total > 0 else 1.0

    cat_summary = []
    for cat_name, stats in category_breakdown.items():
        c_total = stats["total"]
        cat_summary.append({
            "category": cat_name, "count": c_total,
            "retrieval_hit_rate": round((stats["retrieval_hits"] / c_total) * 100, 1),
            "citation_accuracy": round((stats["citation_hits"] / c_total) * 100, 1),
            "escalation_accuracy": round((stats["escalation_correct"] / c_total) * 100, 1)
        })

    return {
        "total_questions": total,
        "elapsed_seconds": elapsed_sec,
        "metrics": {
            "retrieval_hit_rate_top1": round((retrieval_hits_top1 / total) * 100, 1),
            "retrieval_hit_rate_top3": round((retrieval_hits_top3 / total) * 100, 1),
            "citation_faithfulness_rate": round((citation_hits / total) * 100, 1),
            "escalation_accuracy": round(esc_accuracy * 100, 1),
            "escalation_precision": round(esc_precision * 100, 1),
            "escalation_recall": round(esc_recall * 100, 1)
        },
        "confusion_matrix": {"true_positive": tp_esc, "true_negative": tn_esc, "false_positive": fp_esc, "false_negative": fn_esc},
        "category_breakdown": cat_summary,
        "sample_results": sample_results
    }

if __name__ == "__main__":
    dataset = build_evaluation_dataset()
    report = evaluate_dataset(dataset)
    print(json.dumps(report["metrics"], indent=2))
