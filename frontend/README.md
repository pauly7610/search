# Frontend - Xfinity Agentic AI

A modern, responsive frontend for the AI-powered customer support platform. Built with React, TypeScript, and Tailwind CSS, featuring **enterprise-grade WebSocket communication**, a beautiful dark theme interface, real-time chat capabilities, and comprehensive analytics dashboard.

## ✨ Features

### **🔌 Enterprise-Grade WebSocket Communication**

- **Robust Connection Management**: Automatic reconnection with exponential backoff strategy
- **Heartbeat Keep-Alive**: Ping/pong mechanism prevents connection timeouts
- **Client Identification**: Unique client IDs for connection tracking and analytics
- **Connection State Monitoring**: Real-time feedback on connection health and status
- **Error Recovery**: Graceful handling of network issues without breaking chat flow

### **🎨 Modern UI/UX**

- **Dark/Light Theme Toggle**: Professional dark theme with seamless light mode switching
- **Advanced Analytics Dashboard**: Interactive Recharts visualizations with gradients and animations
- **Connection Status Indicators**: Visual feedback for WebSocket connection health
- **Responsive Design**: Mobile-first approach with adaptive layouts for all screen sizes
- **Modern Components**: Clean, accessible UI components with consistent design system

### **💬 Enhanced Real-time Chat**

- **Reliable WebSocket Integration**: Enterprise-grade messaging with comprehensive error handling
- **Agent Visualization**: Clear display of AI agent type, intent classification, and response source
- **Enhanced Message Bubbles**: Rich metadata display with agent information and confidence scores
- **Typing Indicators**: Real-time feedback with improved reliability
- **Chat History**: Persistent conversation management with pagination and state recovery

### **📊 Analytics & Insights**

- **Interactive Dashboards**: Real-time metrics with hover effects and detailed tooltips
- **WebSocket Metrics**: Connection analytics, message throughput, and error tracking
- **Visual Charts**: Gradient-filled area charts, radial progress indicators, and trend lines
- **Performance Metrics**: Chat volume, response times, satisfaction scores, and intent distribution
- **Connection Analytics**: Real-time WebSocket performance monitoring

### **🛠️ Developer Experience**

- **TypeScript**: Full type safety with comprehensive type definitions for WebSocket events
- **Modern Tooling**: Vite for fast development, ESLint for code quality, Prettier for formatting
- **Enhanced Hook Architecture**: Robust WebSocket and chat hooks with error handling
- **State Management**: Zustand for lightweight, predictable state management
- **Connection Debugging**: Comprehensive logging and debugging tools

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ and npm/yarn
- Backend API running on http://localhost:8000

### 1. Install Dependencies

```bash
# Using npm
npm install

# Using yarn (recommended)
yarn install
```

### 2. Environment Setup

Create a `.env` file in the `frontend/` directory:

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
VITE_SENTRY_DSN=your-sentry-dsn
VITE_ENVIRONMENT=development

# WebSocket Configuration
VITE_WS_HEARTBEAT_INTERVAL=30000
VITE_WS_RECONNECT_ATTEMPTS=5
VITE_WS_RECONNECT_DELAY=1000
```

### 3. Development Server

```bash
# Start development server with hot reload
npm run dev
# or
yarn dev
```

### 4. Build for Production

```bash
# Create optimized production build
npm run build
# or
yarn build

# Preview production build locally
npm run preview
# or
yarn preview
```

## 🏗️ Project Structure

```
frontend/
├── src/
│   ├── components/               # Reusable UI components
│   │   ├── analytics/           # Analytics dashboard components
│   │   │   ├── Dashboard/       # Main analytics dashboard with WebSocket metrics
│   │   │   └── MetricsCard/     # Individual metric displays
│   │   ├── chat/               # Enhanced chat interface components
│   │   │   ├── ChatInterface/   # Main chat container with connection status
│   │   │   ├── MessageBubble/   # Rich message display with metadata
│   │   │   ├── MessageInput/    # Message input with connection validation
│   │   │   └── TypingIndicator/ # Reliable typing feedback
│   │   ├── feedback/           # User feedback components
│   │   │   ├── FeedbackButton/  # Feedback submission
│   │   │   └── RatingControl/   # Star rating component
│   │   ├── layout/             # Layout and navigation
│   │   │   ├── Header/         # App header with connection status
│   │   │   ├── Layout.tsx      # Main layout wrapper
│   │   │   └── Navigation/     # Sidebar and tab navigation
│   │   ├── ui/                 # Base UI components
│   │   │   ├── Button/         # Styled button component
│   │   │   ├── Card/           # Card container component
│   │   │   └── Input/          # Form input component
│   │   └── pages/              # Page-level components
│   │       ├── help/           # Help and documentation
│   │       ├── knowledge/      # Knowledge base interface
│   │       ├── profile/        # User profile management
│   │       └── settings/       # Application settings
│   ├── hooks/                  # Enhanced React hooks
│   │   ├── useAIChat.ts       # AI chat integration with error handling
│   │   ├── useAnalytics.ts    # Analytics data fetching
│   │   ├── useChat.ts         # Enhanced chat state management
│   │   ├── useResponsive.ts   # Responsive design utilities
│   │   └── useWebSocket.ts    # Robust WebSocket connection management
│   ├── services/              # External service integrations
│   │   ├── api.ts            # REST API client
│   │   ├── websocket.ts      # Enhanced WebSocket client
│   │   └── index.ts          # Service exports
│   ├── store/                # State management
│   │   ├── chatStore.ts      # Chat state with connection tracking
│   │   ├── uiStore.ts        # UI state (theme, navigation, connection status)
│   │   └── index.ts          # Store exports
│   ├── styles/               # Global styles and themes
│   │   ├── animations.css    # CSS animations and transitions
│   │   ├── apple-theme.css   # Apple-inspired design system
│   │   ├── components.css    # Component-specific styles
│   │   └── globals.css       # Global CSS variables and resets
│   ├── types/                # TypeScript type definitions
│   │   ├── api.ts           # API response types
│   │   ├── chat.ts          # Enhanced chat-related types
│   │   ├── css.d.ts         # CSS module type declarations
│   │   └── index.ts         # Type exports
│   └── utils/               # Utility functions
│       ├── animations.ts    # Animation helpers
│       ├── constants.ts     # App constants including WebSocket config
│       └── formatters.ts    # Data formatting utilities
├── public/                  # Static assets
│   ├── assets/             # Images, icons, and media
│   └── favicon.ico         # App favicon
├── package.json            # Dependencies and scripts
├── tailwind.config.js      # Tailwind CSS configuration
├── vite.config.ts         # Vite build configuration
└── tsconfig.json          # TypeScript configuration
```

## 🔌 Enhanced WebSocket Architecture

### **Robust Connection Management**

```typescript
// Enhanced WebSocket hook with enterprise features
export const useWebSocket = (
  url: string,
  options: UseWebSocketOptions = {}
) => {
  const {
    autoConnect = true,
    reconnection = true,
    reconnectionAttempts = 5,
    reconnectionDelay = 1000,
    heartbeatInterval = 30000,
  } = options;

  // Connection state management
  const [isConnected, setIsConnected] = useState(false);
  const [connectionError, setConnectionError] = useState<string | null>(null);

  // Unique client identification
  const clientIdRef = useRef<string>(generateClientId());

  // Automatic reconnection with exponential backoff
  // Heartbeat mechanism for connection health
  // Comprehensive error handling and logging
};
```

### **Enhanced Chat Hook**

```typescript
// Enhanced chat hook with robust error handling
export const useChat = () => {
  const { socket, isConnected, send, getConnectionState, clientId } =
    useWebSocket("ws://localhost:8000/api/v1/chat/ws");

  // Message handling with proper error recovery
  const handleMessage = (event: MessageEvent) => {
    try {
      const data = JSON.parse(event.data);

      // Handle heartbeat messages
      if (data.type === "pong" || data.type === "ping") {
        // Process heartbeat
        return;
      }

      // Process chat messages with metadata
      if (data.role && data.content) {
        const message: Message = data as Message;
        setMessages((prev) => [...prev, message]);
        setIsTyping(false);
        setAgentStatus("available");
      }
    } catch (error) {
      console.error("Error parsing WebSocket message:", error);
      setIsTyping(false);
      setAgentStatus("error");
    }
  };
};
```

### **Connection Features**

- **Client Tracking**: Unique client IDs for session management
- **Health Monitoring**: Real-time connection state tracking
- **Error Recovery**: Graceful handling of network issues
- **Message Reliability**: Delivery confirmation and retry logic
- **Performance Monitoring**: Connection metrics and analytics

## 🎨 Theme System

### **CSS Variables Architecture**

The application uses a comprehensive CSS variables system for easy theming:

```css
:root {
  /* Color Palette */
  --color-primary: #3b82f6;
  --color-primary-dark: #1d4ed8;
  --color-secondary: #10b981;

  /* Background Colors */
  --color-background: #0f172a;
  --color-surface: #1e293b;
  --color-surface-hover: #334155;

  /* Text Colors */
  --color-text: #f8fafc;
  --color-text-muted: #94a3b8;
  --color-text-inverse: #0f172a;

  /* Connection Status Colors */
  --color-connected: #10b981;
  --color-connecting: #f59e0b;
  --color-disconnected: #ef4444;

  /* Border and Shadow */
  --color-border: #334155;
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

[data-theme="light"] {
  --color-background: #ffffff;
  --color-surface: #f8fafc;
  --color-text: #0f172a;
  /* ... light theme overrides */
}
```

### **Enhanced Theme Toggle Implementation**

```typescript
// Theme management with connection status
interface UIStore {
  theme: "light" | "dark";
  connectionStatus: "connected" | "connecting" | "disconnected";
  toggleTheme: () => void;
  setConnectionStatus: (status: string) => void;
}

const useUIStore = create<UIStore>((set) => ({
  theme: "dark",
  connectionStatus: "disconnected",
  toggleTheme: () =>
    set((state) => ({
      theme: state.theme === "dark" ? "light" : "dark",
    })),
  setConnectionStatus: (status) => set({ connectionStatus: status }),
}));
```

## 📊 Enhanced Analytics

### **WebSocket Metrics Dashboard**

```typescript
// Analytics hook with WebSocket metrics
export const useAnalytics = () => {
  const [metrics, setMetrics] = useState({
    chatVolume: 0,
    responseTime: 0,
    satisfactionScore: 0,
    intentDistribution: {},
    websocketMetrics: {
      activeConnections: 0,
      messagesThroughput: 0,
      connectionErrors: 0,
      averageConnectionDuration: 0,
    },
  });

  // Fetch enhanced analytics including WebSocket data
  const fetchAnalytics = async () => {
    const response = await api.get("/analytics/overview");
    setMetrics(response.data);
  };
};
```

### **Real-time Connection Monitoring**

```typescript
// Connection status component
const ConnectionStatus: React.FC = () => {
  const { isConnected, connectionError, clientId, reconnectAttempts } = useWebSocket();

  return (
    <div className="connection-status">
      <div className={`status-indicator ${isConnected ? 'connected' : 'disconnected'}`}>
        {isConnected ? 'Connected' : 'Disconnected'}
      </div>
      <div className="client-id">Client: {clientId}</div>
      {reconnectAttempts > 0 && (
        <div className="reconnect-info">Reconnect attempts: {reconnectAttempts}</div>
      )}
    </div>
  );
};
```

## 🚀 Recent Enhancements

### **WebSocket Reliability Improvements**

- ✅ Fixed critical event handler conflicts between hooks
- ✅ Implemented robust connection management with client tracking
- ✅ Added comprehensive error handling and recovery mechanisms
- ✅ Introduced heartbeat keep-alive with ping/pong
- ✅ Enhanced reconnection strategies with exponential backoff

### **Chat Experience Enhancements**

- ✅ Improved message handling with proper type detection
- ✅ Enhanced typing indicators with connection state awareness
- ✅ Added connection status indicators in the UI
- ✅ Implemented graceful error recovery that doesn't break chat flow
- ✅ Added detailed logging and debugging capabilities

### **UI/UX Improvements**

- ✅ Enhanced message bubbles with rich metadata display
- ✅ Added connection health indicators in the header
- ✅ Improved error messaging and user feedback
- ✅ Enhanced analytics dashboard with WebSocket metrics
- ✅ Better responsive design for connection status elements

## 🧪 Testing

### **Component Testing**

```bash
# Run all tests
npm test
# or
yarn test

# Run tests in watch mode
npm run test:watch
# or
yarn test:watch

# Run tests with coverage
npm run test:coverage
# or
yarn test:coverage
```

### **WebSocket Testing**

```typescript
// Example WebSocket hook test
import { renderHook, act } from "@testing-library/react";
import { useWebSocket } from "../hooks/useWebSocket";

test("should connect and handle messages", async () => {
  const { result } = renderHook(() =>
    useWebSocket("ws://localhost:8000/api/v1/chat/ws")
  );

  // Test connection establishment
  await act(async () => {
    result.current.connect();
  });

  expect(result.current.isConnected).toBe(true);
  expect(result.current.clientId).toBeDefined();
});
```

### **Chat Integration Testing**

```typescript
// Example chat flow test
test("should send message and receive response", async () => {
  const { result } = renderHook(() => useChat());

  await act(async () => {
    result.current.sendMessage("internet is down");
  });

  expect(result.current.isTyping).toBe(true);

  // Mock WebSocket response
  await act(async () => {
    // Simulate response
  });

  expect(result.current.messages).toHaveLength(2); // User + Assistant
  expect(result.current.isTyping).toBe(false);
});
```

## 🔧 Configuration

### **WebSocket Configuration**

```typescript
// WebSocket configuration options
interface WebSocketConfig {
  autoConnect: boolean;
  reconnection: boolean;
  reconnectionAttempts: number;
  reconnectionDelay: number;
  heartbeatInterval: number;
}

const defaultConfig: WebSocketConfig = {
  autoConnect: true,
  reconnection: true,
  reconnectionAttempts: 5,
  reconnectionDelay: 1000,
  heartbeatInterval: 30000,
};
```

### **Environment Variables**

```env
# WebSocket Configuration
VITE_WS_URL=ws://localhost:8000
VITE_WS_HEARTBEAT_INTERVAL=30000
VITE_WS_RECONNECT_ATTEMPTS=5
VITE_WS_RECONNECT_DELAY=1000

# API Configuration
VITE_API_URL=http://localhost:8000
VITE_API_TIMEOUT=10000

# Development
VITE_ENVIRONMENT=development
VITE_DEBUG_WEBSOCKET=true
```

## 📚 Component Documentation

### **Enhanced Chat Components**

#### **ChatInterface**

```typescript
interface ChatInterfaceProps {
  className?: string;
  showConnectionStatus?: boolean;
  enableTypingIndicators?: boolean;
}

// Enhanced chat interface with connection monitoring
const ChatInterface: React.FC<ChatInterfaceProps> = ({
  showConnectionStatus = true,
  enableTypingIndicators = true
}) => {
  const { messages, isTyping, sendMessage, isConnected, clientId } = useChat();

  return (
    <div className="chat-interface">
      {showConnectionStatus && <ConnectionStatus />}
      <MessageList messages={messages} />
      {enableTypingIndicators && isTyping && <TypingIndicator />}
      <MessageInput onSend={sendMessage} disabled={!isConnected} />
    </div>
  );
};
```

#### **Enhanced MessageBubble**

```typescript
interface MessageBubbleProps {
  message: Message;
  showMetadata?: boolean;
  showAgentInfo?: boolean;
}

// Rich message display with agent information
const MessageBubble: React.FC<MessageBubbleProps> = ({
  message,
  showMetadata = true,
  showAgentInfo = true
}) => {
  return (
    <div className={`message-bubble ${message.role}`}>
      <div className="message-content">{message.content}</div>
      {showAgentInfo && message.agent && (
        <div className="agent-info">
          <span className="agent-name">{message.agent}</span>
          <span className="agent-type">{message.agent_type}</span>
        </div>
      )}
      {showMetadata && (
        <div className="message-metadata">
          <span className="timestamp">{formatTime(message.timestamp)}</span>
          {message.intent_data?.confidence && (
            <span className="confidence">
              Confidence: {(message.intent_data.confidence * 100).toFixed(1)}%
            </span>
          )}
        </div>
      )}
    </div>
  );
};
```

## 🎯 Performance Optimization

### **WebSocket Optimization**

- **Connection Pooling**: Reuse connections across components
- **Message Batching**: Batch multiple messages for efficiency
- **Memory Management**: Proper cleanup of event listeners
- **Error Boundaries**: React error boundaries for WebSocket errors

### **Rendering Optimization**

- **React.memo**: Memoized components for expensive renders
- **useMemo/useCallback**: Optimized hooks for complex computations
- **Virtual Scrolling**: Efficient rendering of large message lists
- **Code Splitting**: Lazy loading of route components

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/websocket-enhancement`)
3. Make your changes with tests
4. Run the test suite (`npm test`)
5. Commit your changes (`git commit -m 'Add WebSocket enhancement'`)
6. Push to the branch (`git push origin feature/websocket-enhancement`)
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

---

**Built with React, TypeScript, Tailwind CSS, and enterprise-grade WebSocket reliability.**
