"""
Semantic Knowledge Base Search Service

This module implements advanced semantic search capabilities for the customer support
knowledge base using sentence transformers and FAISS vector indexing. It provides
both pure semantic search and hybrid search combining semantic similarity with
keyword matching for optimal retrieval performance.

Key Features:
- Sentence transformer embeddings for semantic understanding
- FAISS vector indexing for fast similarity search
- Hybrid search combining semantic and keyword scoring
- Configurable filters and ranking boosts
- Fuzzy string matching with RapidFuzz
- Normalized L2 embeddings for cosine similarity

Architecture:
The service loads the knowledge base, generates embeddings for all content,
builds a FAISS index for fast retrieval, and provides multiple search modes
optimized for different use cases and query types.
"""

import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from rapidfuzz import fuzz

# Path to the knowledge base JSON file
KB_PATH = os.path.join(os.path.dirname(__file__), '../xfinity_knowledge_base.json')

class SemanticKnowledgeBase:
    """
    Advanced semantic search implementation for customer support knowledge base.
    
    This class provides sophisticated search capabilities that go beyond simple
    keyword matching by understanding the semantic meaning of queries and responses.
    It combines state-of-the-art NLP models with efficient vector search to deliver
    relevant results even when exact keyword matches aren't available.
    
    The system supports:
    - Pure semantic search using sentence transformers
    - Keyword-based fuzzy matching with RapidFuzz
    - Hybrid search combining both approaches
    - Advanced filtering and ranking features
    - Fast vector similarity search via FAISS
    """
    
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        """
        Initialize the semantic knowledge base with embeddings and search index.
        
        This constructor loads the knowledge base, generates sentence embeddings
        for all content, and builds a FAISS index for efficient similarity search.
        The initialization process may take some time for large knowledge bases
        as it involves encoding all text content.
        
        Args:
            model_name: Sentence transformer model to use for embeddings
                       'all-MiniLM-L6-v2' provides a good balance of speed and quality
        """
        # Initialize the sentence transformer model for embedding generation
        # This model converts text into high-dimensional vectors that capture semantic meaning
        self.model = SentenceTransformer(model_name)
        
        # Storage for processed responses and their metadata
        self.responses = []  # List of response dictionaries with full metadata
        self.embeddings = None  # NumPy array of embeddings corresponding to responses
        self.kb_metadata = []  # Additional metadata for advanced filtering
        
        # Load knowledge base and generate embeddings
        self._load_and_embed()
        
        # Build FAISS index for fast similarity search
        self._build_faiss_index()

    def _load_and_embed(self):
        """
        Load knowledge base from JSON and generate embeddings for all content.
        
        This method processes the structured knowledge base, extracts text content
        from each response (including keywords), and generates sentence embeddings
        using the transformer model. The embeddings capture semantic relationships
        that enable similarity-based search.
        
        The method combines response content with keywords to create rich text
        representations that improve search accuracy and recall.
        """
        # Load structured knowledge base from JSON file
        with open(KB_PATH, 'r', encoding='utf-8') as f:
            kb = json.load(f)['knowledge_base']['agents']
        
        texts = []  # List to store text content for embedding
        
        # Process each agent's knowledge base
        for agent, agent_data in kb.items():
            # Process each category within the agent's knowledge base
            for category, cat_data in agent_data.get('categories', {}).items():
                # Process each response within the category
                for resp in cat_data.get('responses', []):
                    # Combine response content with keywords for richer semantic representation
                    # This improves matching by including both natural language and key terms
                    combined_text = f"{resp.get('content', '')} {' '.join(resp.get('keywords', []))}"
                    texts.append(combined_text)
                    
                    # Store response with comprehensive metadata for retrieval and filtering
                    self.responses.append({
                        'agent': agent,                              # Support agent type
                        'category': category,                        # Response category
                        'content': resp.get('content', ''),          # Main response text
                        'keywords': resp.get('keywords', []),        # Associated keywords
                        'type': resp.get('type', ''),               # Response type
                        'id': resp.get('id', ''),                   # Unique identifier
                        'title': cat_data.get('title', category),   # Human-readable title
                        # Add more metadata fields as needed for advanced features
                        # Examples: difficulty_level, popularity_score, success_rate
                    })
        
        # Generate embeddings for all text content
        # show_progress_bar=True provides feedback during the potentially slow embedding process
        self.embeddings = self.model.encode(texts, show_progress_bar=True)

    def _build_faiss_index(self):
        """
        Build FAISS index for efficient vector similarity search.
        
        FAISS (Facebook AI Similarity Search) provides optimized algorithms
        for similarity search in high-dimensional spaces. This method creates
        an index that enables fast retrieval of the most similar responses
        to a given query embedding.
        
        The method uses inner product similarity with L2-normalized vectors,
        which is equivalent to cosine similarity and works well for sentence
        embeddings from transformer models.
        """
        # Get embedding dimensionality from the generated embeddings
        dim = self.embeddings.shape[1]
        
        # Create FAISS index for inner product similarity
        # IndexFlatIP performs exact search with inner product similarity
        self.index = faiss.IndexFlatIP(dim)
        
        # Normalize embeddings to unit length for cosine similarity
        # This converts inner product to cosine similarity, which is more
        # intuitive and stable for sentence transformer embeddings
        faiss.normalize_L2(self.embeddings)
        
        # Add normalized embeddings to the FAISS index
        self.index.add(self.embeddings.astype('float32'))

    def semantic_search(self, query, top_k=5):
        """
        Perform pure semantic search using sentence embeddings.
        
        This method finds the most semantically similar responses to a query
        by comparing embedding vectors in high-dimensional space. It captures
        conceptual similarity even when exact words don't match.
        
        Args:
            query: User's search query as natural language text
            top_k: Number of top results to return
            
        Returns:
            List[Dict]: Results with response data and semantic similarity scores
        """
        # Generate embedding for the query using the same model
        query_emb = self.model.encode([query])
        
        # Normalize query embedding for consistent similarity calculation
        faiss.normalize_L2(query_emb)
        
        # Search the FAISS index for most similar responses
        scores, indices = self.index.search(query_emb.astype('float32'), top_k)
        
        # Format results with response data and similarity scores
        results = []
        for score, idx in zip(scores[0], indices[0]):
            results.append({
                'response': self.responses[idx],
                'semantic_score': float(score)  # Cosine similarity score [0,1]
            })
        
        return results

    def keyword_score(self, query, response):
        """
        Calculate keyword-based similarity score using fuzzy string matching.
        
        This method complements semantic search by providing exact and fuzzy
        keyword matching capabilities. It uses RapidFuzz for efficient fuzzy
        string matching that handles typos and variations in terminology.
        
        Args:
            query: User's search query
            response: Response dictionary with keywords and content
            
        Returns:
            float: Keyword similarity score normalized to [0,1]
        """
        # Check fuzzy similarity against all keywords associated with the response
        max_score = 0
        for kw in response['keywords']:
            # Use token set ratio for flexible matching that handles word order
            score = fuzz.token_set_ratio(query, kw)
            if score > max_score:
                max_score = score
        
        # Also check similarity against the main response content
        content_score = fuzz.token_set_ratio(query, response['content'])
        
        # Return the highest score normalized to [0,1] range
        return max(max_score, content_score) / 100.0

    def hybrid_search(self, query, top_k=5, alpha=0.7, filters=None, ranking_boosts=None):
        """
        Perform hybrid search combining semantic and keyword-based approaches.
        
        This advanced search method combines the strengths of both semantic
        understanding and keyword matching. It also supports filtering by
        metadata attributes and ranking boosts based on response quality metrics.
        
        The hybrid approach ensures that:
        - Semantically similar responses are found even without keyword matches
        - Exact keyword matches are weighted appropriately
        - Results can be filtered by metadata (difficulty, tags, etc.)
        - Response quality metrics can influence ranking
        
        Args:
            query: User's search query
            top_k: Number of results to return
            alpha: Weight for semantic vs keyword scoring (0.7 = 70% semantic, 30% keyword)
            filters: Optional dict for metadata filtering
                    e.g., {"difficulty_level": "beginner", "intent_tags": ["modem"]}
            ranking_boosts: Optional dict for quality-based ranking boosts
                           e.g., {"popularity_score": 1.2, "success_rate": 1.1}
            
        Returns:
            List[Dict]: Ranked results with hybrid scores and metadata
        """
        # Start with semantic search to get candidate responses
        # Retrieve more candidates than needed to allow for filtering and reranking
        sem_results = self.semantic_search(query, top_k=top_k*4)
        
        filtered_results = []
        
        for r in sem_results:
            resp = r['response']
            
            # Apply metadata filters if specified
            if filters:
                passed = True
                for key, val in filters.items():
                    if key not in resp:
                        passed = False
                        break
                    
                    if isinstance(val, list):
                        # For list filters (tags), require at least one match
                        if not any(tag in resp.get(key, []) for tag in val):
                            passed = False
                            break
                    else:
                        # For exact value filters
                        if resp.get(key) != val:
                            passed = False
                            break
                
                # Skip responses that don't pass the filters
                if not passed:
                    continue
            
            # Calculate keyword-based similarity score
            r['keyword_score'] = self.keyword_score(query, resp)
            
            # Combine semantic and keyword scores using weighted average
            r['hybrid_score'] = alpha * r['semantic_score'] + (1 - alpha) * r['keyword_score']
            
            # Apply ranking boosts based on response quality metrics
            if ranking_boosts:
                for meta_key, boost in ranking_boosts.items():
                    meta_val = resp.get(meta_key)
                    # Apply boost if the metadata value is numeric
                    if isinstance(meta_val, (int, float)):
                        r['hybrid_score'] *= (1 + (meta_val * (boost - 1)))
            
            filtered_results.append(r)
        
        # Sort results by hybrid score in descending order
        filtered_results.sort(key=lambda x: x['hybrid_score'], reverse=True)
        
        # Return top-k results
        return filtered_results[:top_k] 