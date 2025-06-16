import React, { useState } from 'react';
import styles from './FeedbackButton.module.css';

interface FeedbackButtonProps {
  messageId: string;
  onSubmit: (messageId: string, rating: number, comment?: string) => void;
  onCancel: () => void;
}

export const FeedbackButton: React.FC<FeedbackButtonProps> = ({
  messageId,
  onSubmit,
  onCancel
}) => {
  const [rating, setRating] = useState<number>(0);
  const [comment, setComment] = useState<string>('');

  const handleSubmit = () => {
    onSubmit(messageId, rating, comment);
  };

  return (
    <div className={styles.feedbackContainer}>
      <h3>Provide Feedback</h3>
      <div className={styles.ratingContainer}>
        {[1, 2, 3, 4, 5].map((value) => (
          <button
            key={value}
            className={`${styles.ratingButton} ${rating === value ? styles.active : ''}`}
            onClick={() => setRating(value)}
          >
            {value}
          </button>
        ))}
      </div>
      <textarea
        value={comment}
        onChange={(e) => setComment(e.target.value)}
        placeholder="Add a comment (optional)"
        className={styles.commentInput}
      />
      <div className={styles.buttonContainer}>
        <button onClick={onCancel} className={styles.cancelButton}>
          Cancel
        </button>
        <button
          onClick={handleSubmit}
          disabled={rating === 0}
          className={styles.submitButton}
        >
          Submit
        </button>
      </div>
    </div>
  );
};
