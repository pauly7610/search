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
}
  
export interface ChatState {
    conversations: Conversation[];
    currentConversation: Conversation | null;
    isTyping: boolean;
    agentStatus: 'available' | 'busy' | 'away';
    connectionStatus: 'connected' | 'disconnected' | 'connecting';
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
}
  