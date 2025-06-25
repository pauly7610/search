/**
 * AI Chat Hook for Enhanced Message Handling and Context Management
 * 
 * This custom React hook provides an enhanced interface for AI-powered chat
 * functionality. It builds upon the basic chat hook to add AI-specific features
 * such as intelligent error handling, conversation context management, and
 * intent data processing.
 * 
 * Key Features:
 * - Enhanced error handling with user-friendly messaging
 * - Conversation context extraction for AI continuity
 * - Intent data management for transparency
 * - Seamless integration with base chat functionality
 * - Type-safe interfaces for all data structures
 * 
 * This hook serves as the bridge between the UI components and the underlying
 * chat infrastructure, providing a clean API for AI interactions.
 */

import { useState, useCallback } from 'react';
import { useChat } from './useChat';
import { Message, IntentData } from '../types/chat';

interface UseAIChatReturn {
  messages: Message[];
  sendMessage: (text: string) => Promise<void>;
  isTyping: boolean;
  intentData: IntentData | null;
  getConversationContext: () => { role: "user" | "assistant"; content: string; }[];
}

export const useAIChat = (): UseAIChatReturn => {
  /**
   * Enhanced AI chat hook with intelligent message handling and context management.
   * 
   * This hook extends the basic chat functionality with AI-specific enhancements:
   * 
   * 1. Error Handling: Wraps message sending with try-catch for graceful failures
   * 2. Context Management: Extracts relevant conversation history for AI continuity
   * 3. Intent Processing: Manages intent classification data for user transparency
   * 4. Type Safety: Ensures all interactions are type-safe with TypeScript
   * 
   * The hook follows React best practices with useCallback for performance
   * optimization and consistent API design patterns.
   * 
   * Returns:
   * - messages: Array of conversation messages with full metadata
   * - sendMessage: Enhanced message sending function with error handling
   * - isTyping: Boolean indicating AI processing status
   * - getConversationContext: Function to extract recent context for AI
   */
  
  // Destructure base chat functionality from the core chat hook
  // This provides the fundamental messaging capabilities that we enhance
  const { messages, sendMessage: baseSendMessage, isTyping } = useChat();

  // State for managing intent classification data
  const [intentData, setIntentData] = useState<IntentData | null>(null);

  // Enhanced message sending with comprehensive error handling
  const sendMessage = useCallback(async (text: string) => {
    /**
     * Send a message through the AI system with enhanced error handling.
     * 
     * This wrapper function provides additional error handling and logging
     * around the base message sending functionality. It ensures that any
     * errors are properly caught, logged, and re-thrown for UI handling.
     * 
     * Args:
     *   text: The message content to send
     * 
     * Throws:
     *   Error: Re-throws any errors from the base send function for UI handling
     */
    try {
      // Attempt to send the message through the base chat system
      await baseSendMessage(text);
    } catch (error) {
      // Log the error for debugging and monitoring purposes
      console.error('Error in AI chat:', error);
      
      // Re-throw the error so UI components can handle it appropriately
      // This allows for user-friendly error messages and recovery options
      throw error;
    }
  }, [baseSendMessage]);

  // Extract conversation context for AI continuity and coherence
  const getConversationContext = useCallback(() => {
    /**
     * Extract recent conversation context for AI processing.
     * 
     * This function provides the AI system with relevant conversation history
     * to maintain context and coherence across multiple message exchanges.
     * It returns the last 5 messages in a simplified format suitable for
     * AI processing while preserving essential role and content information.
     * 
     * The context is limited to recent messages to:
     * - Maintain relevance to the current conversation topic
     * - Optimize AI processing performance
     * - Reduce token usage in API calls
     * - Focus on immediately relevant context
     * 
     * Returns:
     *   Array of simplified message objects with role and content
     */
    return messages.slice(-5).map(msg => ({
      role: msg.role,        // Message sender (user/assistant)
      content: msg.content   // Message text content
    }));
  }, [messages]);

  // Return enhanced chat interface with all capabilities
  return {
    messages,                    // Complete message history with metadata
    sendMessage,                 // Enhanced message sending with error handling
    isTyping,                   // AI processing status indicator
    intentData,                 // Intent classification data for transparency
    getConversationContext      // Context extraction for AI continuity
  };
}; 