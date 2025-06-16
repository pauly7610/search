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
      const message: Message = JSON.parse(event.data);
      setMessages((prev) => [...prev, message]);
      setIsTyping(false);
    };

    socket.onclose = () => {
      setIsTyping(false);
    };

    return () => {
      socket.onmessage = null;
      socket.onclose = null;
    };
  }, [socket]);

  const sendMessage = useCallback(
    (content: string) => {
      if (!socket || !content.trim()) return;

      const message: Message = {
        id: Date.now().toString(),
        content: content.trim(),
        role: "user",
        timestamp: new Date().toISOString(),
        status: "sent",
      };

      setMessages((prev) => [...prev, message]);
      socket.send(JSON.stringify({ content: content.trim() }));
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