// API endpoints
export const API_ENDPOINTS = {
    CHAT: '/api/chat',
    FEEDBACK: '/api/feedback',
    ANALYTICS: '/api/analytics',
    USER: '/api/user',
  } as const;
  
  // WebSocket events
  export const WS_EVENTS = {
    CONNECT: 'connect',
    DISCONNECT: 'disconnect',
    MESSAGE: 'message',
    TYPING: 'typing',
    STOP_TYPING: 'stop_typing',
    AGENT_STATUS: 'agent_status',
    USER_JOINED: 'user_joined',
    USER_LEFT: 'user_left',
  } as const;
  
  // Local storage keys
  export const STORAGE_KEYS = {
    AUTH_TOKEN: 'authToken',
    USER_PREFERENCES: 'userPreferences',
    CHAT_HISTORY: 'chatHistory',
    THEME: 'theme',
  } as const;
  
  // Message types
  export const MESSAGE_TYPES = {
    TEXT: 'text',
    IMAGE: 'image',
    FILE: 'file',
    SYSTEM: 'system',
  } as const;
  
  // Agent status types
  export const AGENT_STATUS = {
    AVAILABLE: 'available',
    BUSY: 'busy',
    AWAY: 'away',
  } as const;
  
  // Responsive breakpoints (matching Tailwind)
  export const BREAKPOINTS = {
    SM: 640,
    MD: 768,
    LG: 1024,
    XL: 1280,
    '2XL': 1536,
  } as const;
  
  // Animation durations
  export const ANIMATION_DURATION = {
    FAST: 150,
    NORMAL: 300,
    SLOW: 500,
  } as const;
  
  // Toast notification settings
  export const TOAST_CONFIG = {
    DURATION: 4000,
    MAX_VISIBLE: 5,
    POSITION: {
      MOBILE: 'top-center',
      DESKTOP: 'bottom-right',
    },
  } as const;
  
  // File upload limits
  export const FILE_LIMITS = {
    MAX_SIZE: 10 * 1024 * 1024, // 10MB
    ALLOWED_TYPES: [
      'image/jpeg',
      'image/png',
      'image/gif',
      'application/pdf',
      'text/plain',
    ],
  } as const;
  
  // Feedback rating scale
  export const RATING_SCALE = {
    MIN: 1,
    MAX: 5,
    LABELS: {
      1: 'Very Poor',
      2: 'Poor',
      3: 'Average',
      4: 'Good',
      5: 'Excellent',
    },
  } as const;
  