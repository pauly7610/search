import { useState, useEffect, useRef, useCallback } from 'react';

interface UseWebSocketOptions {
  autoConnect?: boolean;
  reconnection?: boolean;
  reconnectionAttempts?: number;
  reconnectionDelay?: number;
  heartbeatInterval?: number;
}

export const useWebSocket = (
  url: string = 'ws://localhost:8000/api/v1/chat/ws',
  options: UseWebSocketOptions = {}
) => {
  const {
    autoConnect = true,
    reconnection = true,
    reconnectionAttempts = 5,
    reconnectionDelay = 1000,
    heartbeatInterval = 30000
  } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [connectionError, setConnectionError] = useState<string | null>(null);
  const socketRef = useRef<WebSocket | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const heartbeatIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const clientIdRef = useRef<string>(generateClientId());

  // Generate unique client ID
  function generateClientId(): string {
    return `client_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  // Start heartbeat mechanism to keep connection alive
  const startHeartbeat = useCallback(() => {
    if (heartbeatIntervalRef.current) {
      clearInterval(heartbeatIntervalRef.current);
    }

    heartbeatIntervalRef.current = setInterval(() => {
      if (socketRef.current?.readyState === WebSocket.OPEN) {
        try {
          socketRef.current.send(JSON.stringify({ type: 'ping' }));
          console.log('Heartbeat ping sent');
        } catch (error) {
          console.error('Failed to send heartbeat ping:', error);
        }
      }
    }, heartbeatInterval);
  }, [heartbeatInterval]);

  // Stop heartbeat mechanism
  const stopHeartbeat = useCallback(() => {
    if (heartbeatIntervalRef.current) {
      clearInterval(heartbeatIntervalRef.current);
      heartbeatIntervalRef.current = null;
    }
  }, []);

  const connect = useCallback(() => {
    // Prevent multiple connection attempts
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      console.log('WebSocket already connected');
      return;
    }

    // Don't create new connection if one is already connecting
    if (socketRef.current?.readyState === WebSocket.CONNECTING) {
      console.log('WebSocket already connecting');
      return;
    }

    console.log(`Attempting to connect to WebSocket: ${url}`);
    
    try {
      const socket = new WebSocket(url);

      socket.onopen = () => {
        console.log('WebSocket connection opened');
        setIsConnected(true);
        setConnectionError(null);
        reconnectAttemptsRef.current = 0;
        startHeartbeat();
      };

      socket.onclose = (event) => {
        console.log('WebSocket connection closed:', event.code, event.reason);
        setIsConnected(false);
        stopHeartbeat();
        
        // Implement exponential backoff for reconnection
        if (reconnection && reconnectAttemptsRef.current < reconnectionAttempts) {
          const delay = reconnectionDelay * Math.pow(2, reconnectAttemptsRef.current);
          console.log(`Attempting to reconnect in ${delay}ms (attempt ${reconnectAttemptsRef.current + 1}/${reconnectionAttempts})`);
          
          setTimeout(() => {
            reconnectAttemptsRef.current += 1;
            connect();
          }, delay);
        } else if (reconnectAttemptsRef.current >= reconnectionAttempts) {
          console.error('Max reconnection attempts reached');
          setConnectionError('Failed to reconnect after multiple attempts');
        }
      };

      socket.onerror = (error) => {
        console.error('WebSocket error:', error);
        setConnectionError('WebSocket connection error occurred');
      };

      socketRef.current = socket;

    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      setConnectionError('Failed to create WebSocket connection');
    }
  }, [url, reconnection, reconnectionAttempts, reconnectionDelay, startHeartbeat, stopHeartbeat]);

  const disconnect = useCallback(() => {
    console.log('Manually disconnecting WebSocket');
    stopHeartbeat();
    
    if (socketRef.current) {
      // Prevent reconnection attempts for manual disconnects
      reconnectAttemptsRef.current = reconnectionAttempts;
      
      socketRef.current.close(1000, 'Manual disconnect');
      socketRef.current = null;
      setIsConnected(false);
    }
  }, [reconnectionAttempts, stopHeartbeat]);

  // Enhanced send method with connection state checking
  const send = useCallback((data: any) => {
    if (!socketRef.current) {
      console.error('Cannot send message: WebSocket not initialized');
      return false;
    }

    if (socketRef.current.readyState !== WebSocket.OPEN) {
      console.error('Cannot send message: WebSocket not in OPEN state:', socketRef.current.readyState);
      return false;
    }

    try {
      const message = typeof data === 'string' ? data : JSON.stringify(data);
      socketRef.current.send(message);
      console.log('Message sent successfully');
      return true;
    } catch (error) {
      console.error('Failed to send WebSocket message:', error);
      return false;
    }
  }, []);

  // Get connection state information
  const getConnectionState = useCallback(() => {
    if (!socketRef.current) return 'CLOSED';
    
    switch (socketRef.current.readyState) {
      case WebSocket.CONNECTING: return 'CONNECTING';
      case WebSocket.OPEN: return 'OPEN';
      case WebSocket.CLOSING: return 'CLOSING';
      case WebSocket.CLOSED: return 'CLOSED';
      default: return 'UNKNOWN';
    }
  }, []);

  useEffect(() => {
    if (autoConnect) {
      connect();
    }

    // Cleanup on unmount
    return () => {
      stopHeartbeat();
      if (socketRef.current) {
        socketRef.current.close(1000, 'Component unmounting');
      }
    };
  }, [autoConnect, connect, stopHeartbeat]);

  // Handle page visibility changes to manage connections
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.hidden) {
        console.log('Page hidden, maintaining WebSocket connection');
      } else {
        console.log('Page visible, checking WebSocket connection');
        if (!isConnected && autoConnect) {
          connect();
        }
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [isConnected, autoConnect, connect]);

  return {
    socket: socketRef.current,
    isConnected,
    connectionError,
    connect,
    disconnect,
    send,
    getConnectionState,
    clientId: clientIdRef.current,
    reconnectAttempts: reconnectAttemptsRef.current
  };
};
