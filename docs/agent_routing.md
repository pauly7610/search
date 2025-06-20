# Agent Routing & Enhanced Intent Classification

## Overview

The **Xfinity Agentic AI Platform** features a sophisticated multi-agent routing system with **enhanced intent classification**, confidence scoring, and local intent service with cloud fallback. The system automatically routes user queries to specialized AI agents based on advanced natural language understanding.

## Enhanced Multi-Agent Architecture

### **Specialized Agents**

#### **🔧 Tech Support Agent**

- **Specialization**: Hardware troubleshooting, connectivity issues, equipment setup
- **Confidence Threshold**: 0.8+ for direct routing
- **Primary Patterns**: Internet, WiFi, modem, router, speed, outage
- **Advanced Capabilities**: Multi-step troubleshooting, device diagnostics

#### **💰 Billing Agent**

- **Specialization**: Account management, billing inquiries, plan changes
- **Confidence Threshold**: 0.85+ for direct routing
- **Primary Patterns**: Bill, payment, charge, plan, upgrade, account
- **Advanced Capabilities**: Account analysis, plan recommendations

#### **ℹ️ General Agent**

- **Specialization**: Company information, policies, general inquiries
- **Confidence Threshold**: 0.7+ for direct routing
- **Primary Patterns**: Hours, location, contact, policy, information
- **Advanced Capabilities**: Policy interpretation, general guidance

## Enhanced Intent Classification System

### **Local Intent Service**

The platform now includes a high-performance local intent classification service with cloud fallback:

```python
class LocalIntentService:
    """
    Local intent classification service with enhanced pattern matching.

    Features:
    - Multi-pattern matching with confidence scoring
    - Keyword normalization and preprocessing
    - Fallback to cloud services
    - Performance optimization
    - Real-time confidence tracking
    """

    def __init__(self):
        self.billing_patterns = [
            {"pattern": r"\b(bill|billing|charge|cost|expensive|payment)\b", "weight": 0.9},
            {"pattern": r"\b(cancel|disconnect|service)\b", "weight": 0.7},
            {"pattern": r"\b(refund|credit|discount|promotion)\b", "weight": 0.8},
            {"pattern": r"\b(upgrade|downgrade|plan|package)\b", "weight": 0.85}
        ]

        self.technical_patterns = [
            {"pattern": r"\b(internet|wifi|connection|slow|down|outage)\b", "weight": 0.9},
            {"pattern": r"\b(router|modem|equipment|device|cable)\b", "weight": 0.8},
            {"pattern": r"\b(speed|performance|lag|buffering|streaming)\b", "weight": 0.7},
            {"pattern": r"\b(setup|install|configure|troubleshoot)\b", "weight": 0.75}
        ]

        self.general_patterns = [
            {"pattern": r"\b(hours|location|contact|help|support)\b", "weight": 0.8},
            {"pattern": r"\b(policy|terms|conditions|privacy)\b", "weight": 0.7},
            {"pattern": r"\b(store|office|appointment|visit)\b", "weight": 0.75}
        ]

    def classify_intent(self, query: str) -> Dict[str, Any]:
        """
        Classify intent with comprehensive confidence scoring.

        Returns:
        - intent: Classified category (billing, technical, general)
        - confidence: Confidence score (0-1)
        - matched_patterns: Patterns that matched
        - agent_type: Recommended agent
        - scores: All category scores for transparency
        """
        normalized_query = self._preprocess_query(query)

        # Calculate weighted scores for each category
        billing_score = self._calculate_pattern_score(normalized_query, self.billing_patterns)
        technical_score = self._calculate_pattern_score(normalized_query, self.technical_patterns)
        general_score = self._calculate_pattern_score(normalized_query, self.general_patterns)

        # Determine best match
        scores = {
            "billing": billing_score,
            "technical": technical_score,
            "general": general_score
        }

        best_intent = max(scores, key=scores.get)
        confidence = scores[best_intent]

        # Apply confidence boost for multiple pattern matches
        matched_patterns = self._get_matched_patterns(normalized_query, best_intent)
        if len(matched_patterns) > 1:
            confidence = min(1.0, confidence * 1.1)  # 10% boost for multiple matches

        # Map intent to agent type
        agent_mapping = {
            "billing": "billing",
            "technical": "tech_support",
            "general": "general"
        }

        return {
            "intent": best_intent,
            "confidence": round(confidence, 3),
            "agent_type": agent_mapping[best_intent],
            "matched_patterns": matched_patterns,
            "scores": {k: round(v, 3) for k, v in scores.items()},
            "query": query,
            "processing_method": "local_service"
        }

    def _calculate_pattern_score(self, query: str, patterns: List[Dict]) -> float:
        """Calculate weighted score for pattern matches with enhanced logic"""
        total_score = 0.0
        pattern_matches = 0

        for pattern_data in patterns:
            if re.search(pattern_data["pattern"], query, re.IGNORECASE):
                total_score += pattern_data["weight"]
                pattern_matches += 1

        # Apply diminishing returns for multiple patterns
        if pattern_matches > 1:
            total_score = total_score * (1 + (pattern_matches - 1) * 0.1)

        # Normalize to 0-1 range
        return min(1.0, total_score)

    def _preprocess_query(self, query: str) -> str:
        """Enhanced query preprocessing for better pattern matching"""
        # Convert to lowercase and normalize whitespace
        normalized = re.sub(r'\s+', ' ', query.lower().strip())

        # Handle common contractions and variations
        normalized = re.sub(r"can't|cannot", "can not", normalized)
        normalized = re.sub(r"won't", "will not", normalized)
        normalized = re.sub(r"isn't", "is not", normalized)
        normalized = re.sub(r"doesn't", "does not", normalized)

        return normalized
```

### **Enhanced Routing Logic**

```python
async def enhanced_route_message(message: str, client_id: str = None) -> Dict[str, Any]:
    """
    Enhanced message routing with confidence-based agent selection.

    Process:
    1. Local intent classification with confidence scoring
    2. Agent selection based on confidence thresholds
    3. Knowledge base search with agent-specific filtering
    4. Response generation with metadata enrichment
    5. Analytics logging and performance tracking
    """

    # Step 1: Enhanced intent classification
    intent_result = local_intent_service.classify_intent(message)

    # Step 2: Confidence-based routing
    if intent_result["confidence"] >= 0.8:
        # High confidence - direct agent routing
        selected_agent = intent_result["agent_type"]
        routing_method = "direct_routing"
    elif intent_result["confidence"] >= 0.6:
        # Medium confidence - agent routing with validation
        selected_agent = intent_result["agent_type"]
        routing_method = "validated_routing"
    else:
        # Low confidence - general agent with fallback
        selected_agent = "general"
        routing_method = "fallback_routing"

    # Step 3: Agent-specific knowledge base search
    kb_result = await enhanced_knowledge_search(
        query=message,
        agent_filter=selected_agent,
        confidence_threshold=0.7
    )

    # Step 4: Response generation
    if kb_result and kb_result["confidence"] >= 0.7:
        response = create_kb_response(kb_result, intent_result)
        response_source = "knowledge_base"
    else:
        # Fallback to LLM
        response = await llm_fallback(message, intent_result, selected_agent)
        response_source = "llm_fallback"

    # Step 5: Response enrichment
    enriched_response = {
        "content": response["content"],
        "agent": get_agent_name(selected_agent),
        "agent_type": selected_agent,
        "intent": intent_result["intent"],
        "intent_data": intent_result,
        "source": response_source,
        "routing_method": routing_method,
        "confidence": intent_result["confidence"],
        "processing_time": response.get("processing_time", 0),
        "client_id": client_id
    }

    # Step 6: Analytics logging
    await log_routing_analytics(enriched_response, intent_result)

    return enriched_response
```

## Confidence Scoring & Thresholds

### **Confidence Levels**

- **High Confidence (0.8+)**: Direct routing to specialized agent
- **Medium Confidence (0.6-0.79)**: Routing with validation and monitoring
- **Low Confidence (0.4-0.59)**: General agent with enhanced monitoring
- **Very Low Confidence (<0.4)**: LLM fallback with human escalation option

### **Dynamic Threshold Adjustment**

```python
class ConfidenceThresholdManager:
    """
    Dynamic confidence threshold management based on performance metrics.
    """

    def __init__(self):
        self.base_thresholds = {
            "billing": 0.85,
            "technical": 0.8,
            "general": 0.7
        }
        self.performance_history = {}

    def adjust_thresholds(self, agent_type: str, accuracy_metrics: Dict):
        """
        Adjust confidence thresholds based on agent performance.

        If an agent consistently performs well at lower confidence scores,
        we can lower the threshold. If performance degrades, raise it.
        """
        current_accuracy = accuracy_metrics.get("accuracy", 0.0)
        current_threshold = self.base_thresholds[agent_type]

        if current_accuracy > 0.95 and current_threshold > 0.6:
            # High accuracy - can lower threshold
            new_threshold = max(0.6, current_threshold - 0.05)
        elif current_accuracy < 0.85 and current_threshold < 0.9:
            # Low accuracy - raise threshold
            new_threshold = min(0.9, current_threshold + 0.05)
        else:
            new_threshold = current_threshold

        self.base_thresholds[agent_type] = new_threshold
        return new_threshold
```

## Enhanced Pattern Matching

### **Multi-Layer Pattern Recognition**

```python
def enhanced_pattern_matching(query: str, patterns: List[Dict]) -> Dict[str, Any]:
    """
    Multi-layer pattern matching with contextual understanding.
    """

    # Layer 1: Exact pattern matching
    exact_matches = []
    for pattern in patterns:
        if re.search(pattern["pattern"], query, re.IGNORECASE):
            exact_matches.append({
                "pattern": pattern["pattern"],
                "weight": pattern["weight"],
                "match_type": "exact"
            })

    # Layer 2: Semantic similarity (if enabled)
    semantic_matches = []
    if ENABLE_SEMANTIC_MATCHING:
        semantic_matches = find_semantic_matches(query, patterns)

    # Layer 3: Contextual boosting
    context_boost = calculate_context_boost(query, exact_matches)

    # Combine all layers
    total_score = sum(match["weight"] for match in exact_matches)
    total_score += sum(match["weight"] * 0.7 for match in semantic_matches)  # Lower weight for semantic
    total_score *= (1 + context_boost)

    return {
        "score": min(1.0, total_score),
        "exact_matches": exact_matches,
        "semantic_matches": semantic_matches,
        "context_boost": context_boost
    }

def calculate_context_boost(query: str, matches: List[Dict]) -> float:
    """
    Calculate context boost based on query characteristics.
    """
    boost = 0.0

    # Boost for question words
    if re.search(r'\b(how|what|why|when|where|can|could|would)\b', query, re.IGNORECASE):
        boost += 0.1

    # Boost for urgency indicators
    if re.search(r'\b(urgent|emergency|asap|immediately|help)\b', query, re.IGNORECASE):
        boost += 0.15

    # Boost for multiple relevant keywords
    if len(matches) > 1:
        boost += 0.1 * (len(matches) - 1)

    return min(0.3, boost)  # Cap at 30% boost
```

## Real-time Analytics & Monitoring

### **Intent Classification Metrics**

```python
# Prometheus metrics for intent classification
intent_classification_confidence = Histogram(
    'intent_classification_confidence',
    'Intent classification confidence scores',
    ['intent_type', 'routing_method']
)

intent_classification_accuracy = Gauge(
    'intent_classification_accuracy',
    'Intent classification accuracy by agent',
    ['agent_type']
)

routing_decisions_total = Counter(
    'routing_decisions_total',
    'Total routing decisions',
    ['agent_type', 'confidence_level', 'routing_method']
)

pattern_match_effectiveness = Histogram(
    'pattern_match_effectiveness',
    'Pattern matching effectiveness scores',
    ['pattern_type', 'agent']
)
```

### **Performance Monitoring Dashboard**

```python
async def get_routing_analytics() -> Dict[str, Any]:
    """
    Get comprehensive routing and intent classification analytics.
    """
    return {
        "intent_distribution": {
            "technical": await get_intent_percentage("technical"),
            "billing": await get_intent_percentage("billing"),
            "general": await get_intent_percentage("general")
        },
        "confidence_metrics": {
            "average_confidence": await get_average_confidence(),
            "high_confidence_rate": await get_confidence_rate("high"),
            "low_confidence_rate": await get_confidence_rate("low")
        },
        "routing_effectiveness": {
            "direct_routing_success": await get_routing_success("direct"),
            "fallback_rate": await get_fallback_rate(),
            "escalation_rate": await get_escalation_rate()
        },
        "agent_performance": {
            "tech_support": await get_agent_metrics("tech_support"),
            "billing": await get_agent_metrics("billing"),
            "general": await get_agent_metrics("general")
        },
        "pattern_analysis": {
            "most_effective_patterns": await get_top_patterns(),
            "pattern_coverage": await get_pattern_coverage(),
            "new_pattern_suggestions": await suggest_new_patterns()
        }
    }
```

## Recent Enhancements

### **✅ Enhanced Intent Classification**

- Advanced pattern matching with confidence scoring
- Local intent service with cloud fallback
- Multi-layer pattern recognition
- Dynamic threshold adjustment
- Real-time performance monitoring

### **✅ Improved Routing Logic**

- Confidence-based agent selection
- Validation routing for medium confidence
- Enhanced fallback strategies
- Context-aware boosting
- Performance-based optimization

### **✅ Analytics & Monitoring**

- Comprehensive intent classification metrics
- Real-time confidence tracking
- Pattern effectiveness analysis
- Agent performance monitoring
- Automated threshold adjustment

## Configuration

### **Intent Service Configuration**

```python
INTENT_CONFIG = {
    "confidence_threshold": 0.7,
    "use_local_service": True,
    "fallback_to_cloud": True,
    "enable_semantic_matching": False,
    "cache_results": True,
    "cache_ttl": 3600,
    "dynamic_thresholds": True,
    "pattern_learning": True
}
```

### **Agent Configuration**

```python
AGENT_CONFIG = {
    "tech_support": {
        "confidence_threshold": 0.8,
        "fallback_threshold": 0.6,
        "escalation_threshold": 0.4
    },
    "billing": {
        "confidence_threshold": 0.85,
        "fallback_threshold": 0.65,
        "escalation_threshold": 0.45
    },
    "general": {
        "confidence_threshold": 0.7,
        "fallback_threshold": 0.5,
        "escalation_threshold": 0.3
    }
}
```

---

This enhanced agent routing system provides sophisticated intent classification with confidence scoring, enabling more accurate and reliable agent selection while maintaining comprehensive monitoring and analytics capabilities.
