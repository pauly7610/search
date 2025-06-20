import { useState, useEffect, useCallback } from "react";
import { useWebSocket } from "./useWebSocket";
import { Message, ChatState } from "../types/chat";

export const useChat = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [agentStatus, setAgentStatus] = useState("available");

  const { socket, isConnected, send, getConnectionState, clientId } = useWebSocket("ws://localhost:8000/api/v1/chat/ws");

  useEffect(() => {
    if (!socket) return;

    const handleMessage = (event: MessageEvent) => {
      try {
        const data = JSON.parse(event.data);
        console.log('Received WebSocket message:', data);
        
        // Handle heartbeat pong messages
        if (data.type === 'pong') {
          console.log('Heartbeat pong received');
          return;
        }
        
        // Handle ping messages (respond with pong)
        if (data.type === 'ping') {
          console.log('Heartbeat ping received, sending pong');
          send({ type: 'pong' });
          return;
        }
        
        // Handle chat messages
        if (data.role && data.content) {
          const message: Message = data as Message;
          console.log('Processing chat message:', message);
          setMessages((prev) => [...prev, message]);
          setIsTyping(false);
          setAgentStatus("available");
        } else {
          console.log('Received non-chat message:', data);
        }
        
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
        setIsTyping(false);
        setAgentStatus("error");
      }
    };

    const handleClose = (event: CloseEvent) => {
      console.log('WebSocket connection closed in useChat:', event.code, event.reason);
      setIsTyping(false);
      setAgentStatus("disconnected");
    };

    const handleError = (error: Event) => {
      console.error('WebSocket error in useChat:', error);
      setIsTyping(false);
      setAgentStatus("error");
    };

    const handleOpen = () => {
      console.log('WebSocket connection opened in useChat');
      setAgentStatus("available");
    };

    // Add event listeners
    socket.addEventListener('message', handleMessage);
    socket.addEventListener('close', handleClose);
    socket.addEventListener('error', handleError);
    socket.addEventListener('open', handleOpen);

    return () => {
      // Clean up event listeners
      socket.removeEventListener('message', handleMessage);
      socket.removeEventListener('close', handleClose);
      socket.removeEventListener('error', handleError);
      socket.removeEventListener('open', handleOpen);
    };
  }, [socket, send]);

  // Update agent status based on connection state
  useEffect(() => {
    if (isConnected) {
      setAgentStatus("available");
    } else {
      setAgentStatus("disconnected");
    }
  }, [isConnected]);

  const sendMessage = useCallback(
    (content: string) => {
      if (!content.trim()) {
        console.log('Cannot send empty message');
        return;
      }

      if (!isConnected) {
        console.log('Cannot send message - not connected');
        setAgentStatus("disconnected");
        return;
      }

      const connectionState = getConnectionState();
      if (connectionState !== 'OPEN') {
        console.log('WebSocket not in OPEN state:', connectionState);
        return;
      }

      const message: Message = {
        id: Date.now().toString(),
        content: content.trim(),
        role: "user",
        timestamp: new Date().toISOString(),
        status: "sent",
      };

      console.log('Sending message:', content);
      setMessages((prev) => [...prev, message]);
      setIsTyping(true);
      setAgentStatus("processing");
      
      // Use the enhanced send method from useWebSocket
      const success = send({ content: content.trim() });
      
      if (!success) {
        console.error('Failed to send message through WebSocket');
        setIsTyping(false);
        setAgentStatus("error");
        
        // Add error message to chat
        const errorMessage: Message = {
          id: (Date.now() + 1).toString(),
          content: "Sorry, I'm having trouble connecting right now. Please try again in a moment.",
          role: "assistant",
          timestamp: new Date().toISOString(),
          status: "error",
        };
        setMessages((prev) => [...prev, errorMessage]);
      }
    },
    [isConnected, send, getConnectionState]
  );

  return {
    messages,
    isTyping,
    sendMessage,
    isConnected,
    agentStatus,
    clientId,
    connectionState: getConnectionState(),
  };
};