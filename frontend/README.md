# Frontend - Xfinity Agentic AI

A modern, responsive frontend for the AI-powered customer support platform. Built with React, TypeScript, and Tailwind CSS, featuring a beautiful dark theme interface, real-time chat capabilities, and comprehensive analytics dashboard.

## ✨ Features

### **🎨 Modern UI/UX**

- **Dark/Light Theme Toggle**: Professional dark theme with seamless light mode switching
- **Advanced Analytics Dashboard**: Interactive Recharts visualizations with gradients and animations
- **Responsive Design**: Mobile-first approach with adaptive layouts for all screen sizes
- **Modern Components**: Clean, accessible UI components with consistent design system

### **💬 Real-time Chat**

- **WebSocket Integration**: Instant messaging with typing indicators and real-time responses
- **Agent Visualization**: Clear display of AI agent type, intent classification, and response source
- **Message Bubbles**: Distinct styling for user and assistant messages with timestamps
- **Chat History**: Persistent conversation management with pagination

### **📊 Analytics & Insights**

- **Interactive Dashboards**: Real-time metrics with hover effects and detailed tooltips
- **Visual Charts**: Gradient-filled area charts, radial progress indicators, and trend lines
- **Performance Metrics**: Chat volume, response times, satisfaction scores, and intent distribution
- **Data Export**: Export capabilities for analytics data (coming soon)

### **🛠️ Developer Experience**

- **TypeScript**: Full type safety with comprehensive type definitions
- **Modern Tooling**: Vite for fast development, ESLint for code quality, Prettier for formatting
- **Component Architecture**: Modular, reusable components with clear separation of concerns
- **State Management**: Zustand for lightweight, predictable state management

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
│   │   │   ├── Dashboard/       # Main analytics dashboard
│   │   │   └── MetricsCard/     # Individual metric displays
│   │   ├── chat/               # Chat interface components
│   │   │   ├── ChatInterface/   # Main chat container
│   │   │   ├── MessageBubble/   # Individual message display
│   │   │   ├── MessageInput/    # Message input with send button
│   │   │   └── TypingIndicator/ # Real-time typing feedback
│   │   ├── feedback/           # User feedback components
│   │   │   ├── FeedbackButton/  # Feedback submission
│   │   │   └── RatingControl/   # Star rating component
│   │   ├── layout/             # Layout and navigation
│   │   │   ├── Header/         # App header with theme toggle
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
│   ├── hooks/                  # Custom React hooks
│   │   ├── useAIChat.ts       # AI chat integration
│   │   ├── useAnalytics.ts    # Analytics data fetching
│   │   ├── useChat.ts         # Chat state management
│   │   ├── useResponsive.ts   # Responsive design utilities
│   │   └── useWebSocket.ts    # WebSocket connection management
│   ├── services/              # External service integrations
│   │   ├── api.ts            # REST API client
│   │   ├── websocket.ts      # WebSocket client
│   │   └── index.ts          # Service exports
│   ├── store/                # State management
│   │   ├── chatStore.ts      # Chat state (Zustand)
│   │   ├── uiStore.ts        # UI state (theme, navigation)
│   │   └── index.ts          # Store exports
│   ├── styles/               # Global styles and themes
│   │   ├── animations.css    # CSS animations and transitions
│   │   ├── apple-theme.css   # Apple-inspired design system
│   │   ├── components.css    # Component-specific styles
│   │   └── globals.css       # Global CSS variables and resets
│   ├── types/                # TypeScript type definitions
│   │   ├── api.ts           # API response types
│   │   ├── chat.ts          # Chat-related types
│   │   ├── css.d.ts         # CSS module type declarations
│   │   └── index.ts         # Type exports
│   └── utils/               # Utility functions
│       ├── animations.ts    # Animation helpers
│       ├── constants.ts     # App constants
│       └── formatters.ts    # Data formatting utilities
├── public/                  # Static assets
│   ├── assets/             # Images, icons, and media
│   └── favicon.ico         # App favicon
├── package.json            # Dependencies and scripts
├── tailwind.config.js      # Tailwind CSS configuration
├── vite.config.ts         # Vite build configuration
└── tsconfig.json          # TypeScript configuration
```

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

### **Theme Toggle Implementation**

```typescript
// Theme management with Zustand
interface UIStore {
  theme: "light" | "dark";
  toggleTheme: () => void;
}

const useUIStore = create<UIStore>((set) => ({
  theme: "dark",
  toggleTheme: () =>
    set((state) => ({
      theme: state.theme === "dark" ? "light" : "dark",
    })),
}));
```

## 📊 Analytics Dashboard

### **Advanced Visualizations**

The analytics dashboard features sophisticated charts built with Recharts:

```typescript
// Gradient-filled area chart example
<AreaChart data={chatVolumeData}>
  <defs>
    <linearGradient id="chatGradient" x1="0" y1="0" x2="0" y2="1">
      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8}/>
      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.1}/>
    </linearGradient>
  </defs>
  <Area
    type="monotone"
    dataKey="messages"
    stroke="#3b82f6"
    fillOpacity={1}
    fill="url(#chatGradient)"
  />
</AreaChart>
```

### **Metric Cards**

Interactive metric displays with hover effects and trend indicators:

```typescript
interface MetricCardProps {
  title: string;
  value: number;
  trend: "up" | "down" | "neutral";
  trendValue: number;
  icon: React.ComponentType;
}
```

## 🔌 WebSocket Integration

### **Real-time Communication**

```typescript
// WebSocket hook for chat functionality
const useWebSocket = (url: string) => {
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);

  useEffect(() => {
    const ws = new WebSocket(url);

    ws.onopen = () => setIsConnected(true);
    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      setMessages((prev) => [...prev, message]);
    };
    ws.onclose = () => setIsConnected(false);

    setSocket(ws);
    return () => ws.close();
  }, [url]);

  const sendMessage = useCallback(
    (message: Message) => {
      if (socket && isConnected) {
        socket.send(JSON.stringify(message));
      }
    },
    [socket, isConnected]
  );

  return { socket, isConnected, messages, sendMessage };
};
```

## 🧪 Testing

### **Available Scripts**

```bash
# Run all tests
npm test
# or
yarn test

# Run tests in watch mode
npm run test:watch

# Generate coverage report
npm run test:coverage

# Run linting
npm run lint

# Format code
npm run format
```

### **Testing Stack**

- **Vitest**: Fast unit and integration testing
- **React Testing Library**: Component testing utilities
- **MSW**: API mocking for integration tests
- **Playwright**: End-to-end testing (coming soon)

## 🎯 Component Development

### **Component Structure**

Each component follows a consistent structure:

```
ComponentName/
├── index.ts              # Export barrel
├── ComponentName.tsx     # Main component
├── ComponentName.module.css # Styles
└── ComponentName.test.tsx # Tests (optional)
```

### **Example Component**

```typescript
// Button/Button.tsx
interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  children: React.ReactNode;
  onClick?: () => void;
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  loading = false,
  children,
  onClick
}) => {
  return (
    <button
      className={cn(
        styles.button,
        styles[variant],
        styles[size],
        { [styles.loading]: loading }
      )}
      onClick={onClick}
      disabled={loading}
    >
      {loading ? <Spinner /> : children}
    </button>
  );
};
```

## 🚀 Performance Optimization

### **Code Splitting**

```typescript
// Lazy loading for route components
const Dashboard = lazy(() => import('./components/analytics/Dashboard'));
const ChatInterface = lazy(() => import('./components/chat/ChatInterface'));

// Usage with Suspense
<Suspense fallback={<LoadingSpinner />}>
  <Dashboard />
</Suspense>
```

### **Image Optimization**

```typescript
// Optimized image component with lazy loading
const OptimizedImage: React.FC<ImageProps> = ({ src, alt, ...props }) => {
  const [isLoaded, setIsLoaded] = useState(false);

  return (
    <div className={styles.imageContainer}>
      {!isLoaded && <Skeleton />}
      <img
        src={src}
        alt={alt}
        loading="lazy"
        onLoad={() => setIsLoaded(true)}
        className={cn(styles.image, { [styles.loaded]: isLoaded })}
        {...props}
      />
    </div>
  );
};
```

## 🔧 Configuration

### **Vite Configuration**

```typescript
// vite.config.ts
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
      "@components": path.resolve(__dirname, "./src/components"),
      "@hooks": path.resolve(__dirname, "./src/hooks"),
      "@services": path.resolve(__dirname, "./src/services"),
      "@store": path.resolve(__dirname, "./src/store"),
      "@types": path.resolve(__dirname, "./src/types"),
      "@utils": path.resolve(__dirname, "./src/utils"),
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ["react", "react-dom"],
          charts: ["recharts"],
          utils: ["date-fns", "clsx"],
        },
      },
    },
  },
});
```

### **Tailwind Configuration**

```javascript
// tailwind.config.js
module.exports = {
  content: ["./src/**/*.{js,ts,jsx,tsx}"],
  darkMode: ["class", '[data-theme="dark"]'],
  theme: {
    extend: {
      colors: {
        primary: "var(--color-primary)",
        background: "var(--color-background)",
        surface: "var(--color-surface)",
        text: "var(--color-text)",
      },
      animation: {
        "fade-in": "fadeIn 0.5s ease-in-out",
        "slide-up": "slideUp 0.3s ease-out",
        "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
      },
    },
  },
};
```

## 🌐 Deployment

### **Build Optimization**

```bash
# Production build with optimization
npm run build

# Analyze bundle size
npm run build -- --analyze

# Build with environment variables
VITE_API_URL=https://api.production.com npm run build
```

### **Docker Deployment**

```dockerfile
# Multi-stage build for optimized production image
FROM node:18-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## 🤝 Contributing

### **Development Workflow**

1. Create feature branch: `git checkout -b feature/new-feature`
2. Make changes and add tests
3. Run quality checks: `npm run lint && npm test`
4. Commit with conventional format: `feat: add new component`
5. Push and create pull request

### **Code Standards**

- **TypeScript**: Strict mode enabled, full type coverage
- **ESLint**: Enforced code quality and consistency
- **Prettier**: Automated code formatting
- **Conventional Commits**: Standardized commit messages

---

For more detailed information, see the [main documentation](../docs/README.md) and explore the component library in `src/components/`.
