import React from 'react';
import { motion } from 'framer-motion';
import { formatDistanceToNow } from 'date-fns';
import { Message } from '../../../types/chat';
import styles from './MessageBubble.module.css';

interface MessageBubbleProps {
  message: Message;
  onFeedbackClick: () => void;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({ message, onFeedbackClick }) => {
  const isUser = message.role === 'user';

  return (
    <motion.div
      className={`${styles.messageBubble} ${isUser ? styles.user : styles.assistant}`}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3 }}
      role="article"
      aria-label={`${message.role} message`}
    >
      <div className={styles.content}>{message.content}</div>
      {!isUser && (
        <div className={styles.metadata}>
          {message.agent && <div className={styles.agent}>Agent: {message.agent}</div>}
          {message.agent_type && <div className={styles.agentType}>Type: {message.agent_type}</div>}
          {message.answer_type && <div className={styles.answerType}>Answer: {message.answer_type}</div>}
          {message.intent && <div className={styles.intent}>Intent: {message.intent}</div>}
          {message.intent_data && (
            <div className={styles.intentData}>
              <pre>{JSON.stringify(message.intent_data, null, 2)}</pre>
            </div>
          )}
          <button className={styles.feedbackButton} onClick={onFeedbackClick}>
            Feedback
          </button>
        </div>
      )}

      <div className={styles.messageMeta}>
        <time 
          className={styles.timestamp}
          dateTime={message.timestamp}
        >
          {formatDistanceToNow(new Date(message.timestamp), { addSuffix: true })}
        </time>

        {message.status && (
          <span 
            className={styles.status}
            aria-label={`Message status: ${message.status}`}
          >
            {message.status === 'sent' && '✓'}
            {message.status === 'delivered' && '✓✓'}
            {message.status === 'read' && '✓✓'}
          </span>
        )}
      </div>
    </motion.div>
  );
};