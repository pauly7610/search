import { useState, useEffect, useRef, useCallback } from 'react';

interface UseWebSocketOptions {
  autoConnect?: boolean;
  reconnection?: boolean;
  reconnectionAttempts?: number;
  reconnectionDelay?: number;
  heartbeatInterval?: number;
}

export const useWebSocket = (
  url: string = import.meta.env.VITE_WS_URL || 'ws://127.0.0.1:8000/api/v1/chat/ws',
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
  const heartbeatIntervalRef = useRef<number | null>(null);
  const clientIdRef = useRef<string>(generateClientId());
  const lastPongRef = useRef<Date>(new Date());

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
          
          // Check if we've received a pong recently
          const now = new Date();
          const timeSinceLastPong = now.getTime() - lastPongRef.current.getTime();
          
          // If no pong received for 2x the heartbeat interval, consider connection dead
          if (timeSinceLastPong > heartbeatInterval * 2) {
            console.warn(`No heartbeat response for ${timeSinceLastPong}ms, reconnecting...`);
            // Force close and reconnect
            socketRef.current.close(1000, 'Heartbeat timeout');
          }
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

    // Close any existing socket that might be in CLOSING state
    if (socketRef.current) {
      try {
        socketRef.current.close();
      } catch (e) {
        console.error('Error closing existing socket:', e);
      }
    }

    // Determine if we should use a client ID in the URL
    const fullUrl = clientIdRef.current ? 
      `${url}/${clientIdRef.current}` : 
      url;
      
    console.log(`Attempting to connect to WebSocket: ${fullUrl}`);
    
    try {
      const socket = new WebSocket(fullUrl);

      socket.onopen = () => {
        console.log('WebSocket connection opened');
        setIsConnected(true);
        setConnectionError(null);
        reconnectAttemptsRef.current = 0;
        lastPongRef.current = new Date(); // Reset last pong time
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
      
      // Don't set onmessage here - let useChat handle all messages
      // socket.onmessage will be set by useChat

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
