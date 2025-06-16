import { useState, useEffect, useRef, useCallback } from 'react';

interface UseWebSocketOptions {
  autoConnect?: boolean;
  reconnection?: boolean;
  reconnectionAttempts?: number;
  reconnectionDelay?: number;
}

export const useWebSocket = (
  url: string = 'ws://localhost:8000/api/v1/chat/ws',
  options: UseWebSocketOptions = {}
) => {
  const {
    autoConnect = true,
    reconnection = true,
    reconnectionAttempts = 5,
    reconnectionDelay = 1000
  } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [connectionError, setConnectionError] = useState<string | null>(null);
  const socketRef = useRef<WebSocket | null>(null);
  const reconnectAttemptsRef = useRef(0);

  const connect = useCallback(() => {
    if (socketRef.current?.readyState === WebSocket.OPEN) return;

    const socket = new WebSocket(url);

    socket.onopen = () => {
      setIsConnected(true);
      setConnectionError(null);
      reconnectAttemptsRef.current = 0;
    };

    socket.onclose = () => {
      setIsConnected(false);
      if (reconnection && reconnectAttemptsRef.current < reconnectionAttempts) {
        setTimeout(() => {
          reconnectAttemptsRef.current += 1;
          connect();
        }, reconnectionDelay);
      }
    };

    socket.onerror = (error) => {
      setConnectionError('WebSocket error occurred');
      console.error('WebSocket error:', error);
    };

    socketRef.current = socket;
  }, [url, reconnection, reconnectionAttempts, reconnectionDelay]);

  const disconnect = useCallback(() => {
    if (socketRef.current) {
      socketRef.current.close();
      socketRef.current = null;
      setIsConnected(false);
    }
  }, []);

  useEffect(() => {
    if (autoConnect) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [autoConnect, connect, disconnect]);

  return {
    socket: socketRef.current,
    isConnected,
    connectionError,
    connect,
    disconnect
  };
};
