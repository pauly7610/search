/**
 * Main Chat Interface Component for Real-time Customer Support
 * 
 * This component provides the primary interface for customer interactions with
 * the AI support system. It handles real-time messaging, displays conversation
 * history, manages user feedback, and provides visual indicators for system status.
 * 
 * Key Features:
 * - Real-time messaging with WebSocket communication
 * - Animated message display with smooth transitions
 * - Typing indicators and status updates
 * - Feedback collection system for continuous improvement
 * - Error handling and recovery mechanisms
 * - Intent classification display for transparency
 * - Responsive design for all device types
 * 
 * The component follows React best practices with hooks for state management
 * and custom hooks for complex logic separation.
 */

import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAIChat } from '../../../hooks/useAIChat';
import { MessageBubble } from '../MessageBubble/MessageBubble';
import { MessageInput } from '../MessageInput/MessageInput';
import { TypingIndicator } from '../TypingIndicator/TypingIndicator';
import { FeedbackButton } from '../../feedback/FeedbackButton/FeedbackButton';
import { Message, FeedbackData, IntentData } from '../../../types/chat';
import styles from './ChatInterface.module.css';

export const ChatInterface: React.FC = () => {
  /**
   * Main chat interface component managing conversation flow and user interactions.
   * 
   * This component orchestrates the complete chat experience by:
   * 1. Managing message state and conversation history
   * 2. Handling user input and AI responses
   * 3. Providing visual feedback and status indicators
   * 4. Managing feedback collection for system improvement
   * 5. Ensuring smooth animations and transitions
   * 6. Handling errors gracefully with user-friendly messages
   * 
   * State Management:
   * - Message history maintained through custom hook
   * - Feedback modal state for user ratings
   * - Error state for handling and displaying failures
   * - Typing indicators for real-time communication feel
   * 
   * The component uses advanced React patterns including:
   * - Custom hooks for business logic separation
   * - Refs for DOM manipulation (auto-scroll)
   * - Effects for side effects (scrolling, cleanup)
   * - State lifting for component communication
   */

  // Custom hook for AI chat functionality including WebSocket communication
  // This hook manages the complex logic of message sending, receiving, and state
  const {
    messages,        // Array of conversation messages
    isTyping,       // Boolean indicating if AI is processing
    sendMessage,    // Function to send user messages
    intentData,     // Intent classification data for transparency
    getConversationContext  // Function to retrieve conversation context
  } = useAIChat();

  // Ref for automatic scrolling to the latest message
  // This ensures users always see the newest content without manual scrolling
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // State for managing feedback modal visibility
  // Tracks which message is being rated for targeted feedback collection
  const [showFeedback, setShowFeedback] = useState<string | null>(null);
  
  // State for error handling and user notification
  // Provides user-friendly error messages when operations fail
  const [error, setError] = useState<string | null>(null);

  // Utility function for smooth scrolling to the bottom of the chat
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Effect to automatically scroll to new messages
  // Ensures the chat always shows the latest content as it arrives
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Enhanced message sending with error handling and user feedback
  const handleSendMessage = async (text: string) => {
    try {
      // Clear any previous errors before attempting to send
      setError(null);
      
      // Send message through the AI chat system
      await sendMessage(text);
    } catch (err) {
      // Handle errors gracefully with user-friendly messaging
      setError('Failed to send message. Please try again.');
      console.error('Error sending message:', err);
    }
  };

  // Feedback submission handler for continuous system improvement
  const handleFeedback = async (messageId: string, rating: number, comment?: string) => {
    try {
      // Construct feedback data with complete metadata
      const feedbackData: FeedbackData = {
        messageId,
        rating,
        comment,
        timestamp: new Date().toISOString()
      };
      
      // Submit feedback to the backend for analysis and learning
      await fetch('/api/v1/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(feedbackData)
      });
      
      // Close feedback modal after successful submission
      setShowFeedback(null);
    } catch (err) {
      console.error('Error submitting feedback:', err);
    }
  };

  return (
    <div className={styles.chatInterface}>
      {/* Header section with status and intent information */}
      <header className={styles.header}>
        <div className={styles.statusIndicator}>
          <span className={styles.statusText}>
            AI Assistant
          </span>
        </div>
        
        {/* Intent classification display for user transparency */}
        {intentData && (
          <div className={styles.intentInfo}>
            <span className={styles.intentLabel}>Intent:</span>
            <span className={styles.intentValue}>{intentData.intent}</span>
            <span className={styles.confidenceValue}>
              ({Math.round(intentData.confidence * 100)}% confidence)
            </span>
          </div>
        )}
      </header>

      {/* Main messages container with animated message display */}
      <div className={styles.messagesContainer}>
        <AnimatePresence>
          {messages.map((message: Message) => (
            <MessageBubble
              key={message.id}
              message={message}
              onFeedbackClick={() => setShowFeedback(message.id)}
            />
          ))}
        </AnimatePresence>

        {/* Typing indicator for real-time communication feel */}
        {isTyping && (
          <TypingIndicator />
        )}

        {/* Error message display for user notification */}
        {error && (
          <div className={styles.errorMessage}>
            {error}
          </div>
        )}

        {/* Invisible element for auto-scrolling reference */}
        <div ref={messagesEndRef} />
      </div>

      {/* Message input section with send functionality */}
      <div className={styles.inputContainer}>
        <MessageInput
          onSendMessage={handleSendMessage}
          disabled={isTyping}
          placeholder={isTyping ? "AI is thinking..." : "Type your message..."}
        />
      </div>

      {/* Feedback modal for user rating and comments */}
      <AnimatePresence>
        {showFeedback && (
          <motion.div
            className={styles.modalOverlay}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setShowFeedback(null)}
          >
            <motion.div
              className={styles.modalContent}
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e: React.MouseEvent) => e.stopPropagation()}
            >
              <FeedbackButton
                messageId={showFeedback}
                onSubmit={handleFeedback}
                onCancel={() => setShowFeedback(null)}
              />
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};