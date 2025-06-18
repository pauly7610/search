import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from rapidfuzz import fuzz

KB_PATH = os.path.join(os.path.dirname(__file__), '../xfinity_knowledge_base.json')

class SemanticKnowledgeBase:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
        self.responses = []
        self.embeddings = None
        self.kb_metadata = []
        self._load_and_embed()
        self._build_faiss_index()

    def _load_and_embed(self):
        with open(KB_PATH, 'r', encoding='utf-8') as f:
            kb = json.load(f)['knowledge_base']['agents']
        texts = []
        for agent, agent_data in kb.items():
            for category, cat_data in agent_data.get('categories', {}).items():
                for resp in cat_data.get('responses', []):
                    combined_text = f"{resp.get('content', '')} {' '.join(resp.get('keywords', []))}"
                    texts.append(combined_text)
                    self.responses.append({
                        'agent': agent,
                        'category': category,
                        'content': resp.get('content', ''),
                        'keywords': resp.get('keywords', []),
                        'type': resp.get('type', ''),
                        'id': resp.get('id', ''),
                        'title': cat_data.get('title', category),
                        # Add more metadata fields as needed
                    })
        self.embeddings = self.model.encode(texts, show_progress_bar=True)

    def _build_faiss_index(self):
        dim = self.embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dim)
        faiss.normalize_L2(self.embeddings)
        self.index.add(self.embeddings.astype('float32'))

    def semantic_search(self, query, top_k=5):
        query_emb = self.model.encode([query])
        faiss.normalize_L2(query_emb)
        scores, indices = self.index.search(query_emb.astype('float32'), top_k)
        results = []
        for score, idx in zip(scores[0], indices[0]):
            results.append({
                'response': self.responses[idx],
                'semantic_score': float(score)
            })
        return results

    def keyword_score(self, query, response):
        # Use rapidfuzz for fuzzy keyword matching
        max_score = 0
        for kw in response['keywords']:
            score = fuzz.token_set_ratio(query, kw)
            if score > max_score:
                max_score = score
        # Also check content
        content_score = fuzz.token_set_ratio(query, response['content'])
        return max(max_score, content_score) / 100.0  # Normalize to 0-1

    def hybrid_search(self, query, top_k=5, alpha=0.7, filters=None, ranking_boosts=None):
        """
        filters: dict, e.g. {"difficulty_level": "beginner", "intent_tags": ["modem"]}
        ranking_boosts: dict, e.g. {"popularity_score": 1.2, "success_rate": 1.1}
        """
        sem_results = self.semantic_search(query, top_k=top_k*4)  # get more for reranking/filtering
        filtered_results = []
        for r in sem_results:
            resp = r['response']
            # Filtering
            if filters:
                passed = True
                for key, val in filters.items():
                    if key not in resp:
                        passed = False
                        break
                    if isinstance(val, list):
                        # For tags, require at least one match
                        if not any(tag in resp.get(key, []) for tag in val):
                            passed = False
                            break
                    else:
                        if resp.get(key) != val:
                            passed = False
                            break
                if not passed:
                    continue
            r['keyword_score'] = self.keyword_score(query, resp)
            r['hybrid_score'] = alpha * r['semantic_score'] + (1 - alpha) * r['keyword_score']
            # Ranking boosts/penalties
            if ranking_boosts:
                for meta_key, boost in ranking_boosts.items():
                    meta_val = resp.get(meta_key)
                    if isinstance(meta_val, (int, float)):
                        r['hybrid_score'] *= (1 + (meta_val * (boost - 1)))
            filtered_results.append(r)
        # Sort by hybrid score
        filtered_results.sort(key=lambda x: x['hybrid_score'], reverse=True)
        return filtered_results[:top_k] 