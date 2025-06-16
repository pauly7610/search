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
  const {
    messages,
    isTyping,
    sendMessage,
    intentData,
    getConversationContext
  } = useAIChat();

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [showFeedback, setShowFeedback] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (text: string) => {
    try {
      setError(null);
      await sendMessage(text);
    } catch (err) {
      setError('Failed to send message. Please try again.');
      console.error('Error sending message:', err);
    }
  };

  const handleFeedback = async (messageId: string, rating: number, comment?: string) => {
    try {
      const feedbackData: FeedbackData = {
        messageId,
        rating,
        comment,
        timestamp: new Date().toISOString()
      };
      await fetch('/api/v1/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(feedbackData)
      });
      setShowFeedback(null);
    } catch (err) {
      console.error('Error submitting feedback:', err);
    }
  };

  return (
    <div className={styles.chatInterface}>
      {/* Header */}
      <header className={styles.header}>
        <div className={styles.statusIndicator}>
          <span className={styles.statusText}>
            AI Assistant
          </span>
        </div>
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

      {/* Messages */}
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

        {isTyping && (
          <TypingIndicator />
        )}

        {error && (
          <div className={styles.errorMessage}>
            {error}
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className={styles.inputContainer}>
        <MessageInput
          onSendMessage={handleSendMessage}
          disabled={isTyping}
          placeholder={isTyping ? "AI is thinking..." : "Type your message..."}
        />
      </div>

      {/* Feedback Modal */}
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