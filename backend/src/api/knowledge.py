from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse
import os
import json
from src.services.semantic_search import SemanticKnowledgeBase

router = APIRouter()

# Global instance of the hybrid search engine
semantic_kb = SemanticKnowledgeBase()

# Path to the knowledge base JSON file
KB_PATH = os.path.join(os.path.dirname(__file__), "../xfinity_knowledge_base.json")


def load_knowledge_base():
    with open(KB_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("knowledge_base", {}).get("agents", {})


@router.get("/", response_class=JSONResponse)
def get_knowledge_base(
    q: str = Query(None, description="Search query"),
    top_k: int = 5,
    filters: str = Query(None, description="JSON dict of metadata filters"),
    ranking_boosts: str = Query(None, description="JSON dict of ranking boosts"),
):
    if not q:
        # Return all articles (as before, but with new structure)
        articles = [resp for resp in semantic_kb.responses]
        return {"articles": articles}
    # Parse filters and ranking_boosts if provided
    filters_dict = json.loads(filters) if filters else None
    ranking_boosts_dict = json.loads(ranking_boosts) if ranking_boosts else None
    # Hybrid search with filtering/ranking
    results = semantic_kb.hybrid_search(
        q, top_k=top_k, filters=filters_dict, ranking_boosts=ranking_boosts_dict
    )
    # Return results with scores and metadata
    return {
        "results": [
            {
                "response": r["response"],
                "hybrid_score": r["hybrid_score"],
                "semantic_score": r["semantic_score"],
                "keyword_score": r["keyword_score"],
            }
            for r in results
        ]
    }
