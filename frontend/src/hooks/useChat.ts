import { useState, useEffect, useCallback } from "react";
import { useWebSocket } from "./useWebSocket";
import { Message, ChatState } from "../types/chat";

export const useChat = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [agentStatus, setAgentStatus] = useState("available");

  const { socket, isConnected } = useWebSocket("ws://localhost:8000/api/v1/chat/ws");

  useEffect(() => {
    if (!socket) return;

    socket.onmessage = (event) => {
      try {
        const message: Message = JSON.parse(event.data);
        console.log('Received message:', message);
        setMessages((prev) => [...prev, message]);
        setIsTyping(false);
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
        setIsTyping(false);
      }
    };

    socket.onclose = () => {
      console.log('WebSocket connection closed');
      setIsTyping(false);
    };

    socket.onerror = (error) => {
      console.error('WebSocket error in useChat:', error);
      setIsTyping(false);
    };

    return () => {
      socket.onmessage = null;
      socket.onclose = null;
      socket.onerror = null;
    };
  }, [socket]);

  const sendMessage = useCallback(
    (content: string) => {
      if (!socket || !content.trim()) {
        console.log('Cannot send message - socket not available or content empty');
        return;
      }

      if (socket.readyState !== WebSocket.OPEN) {
        console.log('WebSocket not in OPEN state:', socket.readyState);
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
      
      try {
        socket.send(JSON.stringify({ content: content.trim() }));
      } catch (error) {
        console.error('Error sending WebSocket message:', error);
        setIsTyping(false);
      }
    },
    [socket]
  );

  return {
    messages,
    isTyping,
    sendMessage,
    isConnected,
    agentStatus,
  };
};