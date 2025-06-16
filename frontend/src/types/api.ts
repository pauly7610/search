export interface ApiResponse<T = any> {
    data: T;
    message: string;
    success: boolean;
    timestamp: string;
  }
  
  export interface ApiError {
    message: string;
    code: string;
    details?: Record<string, any>;
  }
  
  export interface PaginatedResponse<T> {
    data: T[];
    pagination: {
      page: number;
      limit: number;
      total: number;
      totalPages: number;
    };
  }
  
  export interface ChatRequest {
    message: string;
    conversationId?: string;
    metadata?: Record<string, any>;
  }
  
  export interface FeedbackRequest {
    messageId: string;
    rating: number;
    comment?: string;
  }
  
  export interface AnalyticsData {
    totalConversations: number;
    averageResponseTime: string;
    satisfactionRate: string;
    activeUsers: number;
    conversationVolume: Array<{
      date: string;
      conversations: number;
    }>;
    responseTimeTrend: Array<{
      date: string;
      responseTime: number;
    }>;
    satisfactionTrend: Array<{
      date: string;
      satisfaction: number;
    }>;
    intentDistribution: Record<string, number>;
  }
  
  export interface Message {
    id: string;
    content: string;
    role: 'user' | 'assistant';
    timestamp: string;
    agent?: string;
    agent_type?: string;
    answer_type?: string;
    intent?: string;
    intent_data?: Record<string, any>;
  }
  