export interface Message {
    id: string;
    content: string;
    role: 'user' | 'assistant';
    timestamp: string;
    status?: 'pending' | 'sent' | 'delivered' | 'read' | 'failed';
    agent?: string;
    agent_type?: string;
    answer_type?: string;
    intent?: string;
    intent_data?: Record<string, any>;
    conversation_flow?: 'standard' | 'follow_up_adaptive' | 'empathetic_support';
    is_follow_up?: boolean;
}
  
export interface Conversation {
    id: string;
    userId: string;
    sessionId: string;
    title?: string;
    messages: Message[];
    createdAt: string;
    updatedAt: string;
    isActive: boolean;
    frustration_level?: number;
    attempt_count?: number;
    tone_used?: string;
}
  
export interface ChatState {
    conversations: Conversation[];
    currentConversation: Conversation | null;
    isTyping: boolean;
    agentStatus: 'available' | 'busy' | 'away';
    connectionStatus: 'connected' | 'disconnected' | 'connecting';
    conversationMetrics?: ConversationMetrics;
}

export interface ConversationMetrics {
    processing_time_ms: number;
    is_follow_up: boolean;
    attempt_count: number;
    frustration_level: number;
    conversation_state: string;
    tone_used: string;
}
  
export interface FeedbackData {
    messageId: string;
    rating: number;
    comment?: string;
    timestamp: string;
}
  
export interface IntentData {
    intent: string;
    confidence: number;
    keywords: string[];
}
  
export interface AgentResponse {
    message: string;
    confidence: number;
    sources: string[];
    escalationNeeded: boolean;
    conversation_flow?: string;
    solution_summary?: string;
    conversation_metrics?: ConversationMetrics;
}
  