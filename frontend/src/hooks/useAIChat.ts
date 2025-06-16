import { useState, useCallback } from 'react';
import { useChat } from './useChat';
import { Message } from '../types/chat';

interface IntentData {
  intent: string;
  confidence: number;
  keywords: string[];
}

export const useAIChat = () => {
  const { messages, sendMessage: baseSendMessage, isTyping } = useChat();

  const sendMessage = useCallback(async (text: string) => {
    try {
      await baseSendMessage(text);
    } catch (error) {
      console.error('Error in AI chat:', error);
      throw error;
    }
  }, [baseSendMessage]);

  const getConversationContext = useCallback(() => {
    return messages.slice(-5).map(msg => ({
      role: msg.role,
      content: msg.content
    }));
  }, [messages]);

  return {
    messages,
    sendMessage,
    isTyping,
    getConversationContext
  };
}; 