from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
import os
import json

router = APIRouter()

# Path to the knowledge base JSON file
KB_PATH = os.path.join(os.path.dirname(__file__), '../xfinity_knowledge_base.json')

def load_knowledge_base():
    with open(KB_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get('knowledge_base', {}).get('agents', {})

@router.get("/", response_class=JSONResponse)
def get_knowledge_base(q: str = Query(None, description="Search query")):
    kb = load_knowledge_base()
    articles = []
    for agent, agent_data in kb.items():
        for category, cat_data in agent_data.get('categories', {}).items():
            for resp in cat_data.get('responses', []):
                article = {
                    "agent": agent,
                    "agent_name": agent_data.get('name'),
                    "category": category,
                    "title": cat_data.get('title', category),
                    "content": resp.get('content'),
                    "keywords": resp.get('keywords', []),
                    "type": resp.get('type', ''),
                }
                articles.append(article)
    if q:
        q_lower = q.lower()
        articles = [a for a in articles if q_lower in a['content'].lower() or any(q_lower in kw.lower() for kw in a['keywords'])]
    return {"articles": articles} 