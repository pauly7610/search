import axios, { AxiosResponse, AxiosError } from 'axios';
import { ApiResponse, ApiError, ChatRequest, FeedbackRequest, AnalyticsData } from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for authentication
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: AxiosError<ApiError>) => {
    const apiError: ApiError = {
      message: error.response?.data?.message || error.message,
      code: error.response?.data?.code || 'UNKNOWN_ERROR',
      details: error.response?.data?.details,
    };
    
    return Promise.reject(apiError);
  }
);

// API methods
export const api = {
  // Chat endpoints
  chat: {
    sendMessage: (data: ChatRequest): Promise<ApiResponse> =>
      apiClient.post('/api/chat/message', data).then(res => res.data),
    
    getConversations: (): Promise<ApiResponse> =>
      apiClient.get('/api/chat/conversations').then(res => res.data),
    
    getConversation: (id: string): Promise<ApiResponse> =>
      apiClient.get(`/api/chat/conversations/${id}`).then(res => res.data),
    
    deleteConversation: (id: string): Promise<ApiResponse> =>
      apiClient.delete(`/api/chat/conversations/${id}`).then(res => res.data),
  },

  // Feedback endpoints
  feedback: {
    submitFeedback: (data: FeedbackRequest): Promise<ApiResponse> =>
      apiClient.post('/api/feedback', data).then(res => res.data),
    
    getFeedback: (messageId: string): Promise<ApiResponse> =>
      apiClient.get(`/api/feedback/${messageId}`).then(res => res.data),
  },

  // Analytics endpoints
  analytics: {
    getOverview: async (): Promise<ApiResponse<AnalyticsData>> => {
      const res = await fetch('/api/v1/analytics/overview');
      if (!res.ok) throw new Error('Failed to fetch analytics overview');
      const data = await res.json();
      return {
        data,
        message: '',
        success: true,
        timestamp: new Date().toISOString(),
      };
    },
  },

  // User endpoints
  user: {
    getProfile: (): Promise<ApiResponse> =>
      apiClient.get('/api/user/profile').then(res => res.data),
    
    updateProfile: (data: any): Promise<ApiResponse> =>
      apiClient.put('/api/user/profile', data).then(res => res.data),
  },
};

export default api;
