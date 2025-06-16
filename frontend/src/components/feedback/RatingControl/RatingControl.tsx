import React from 'react';
import styles from './RatingControl.module.css';

interface RatingControlProps {
  value: number;
  onChange: (value: number) => void;
  size?: 'sm' | 'md' | 'lg';
}

export const RatingControl: React.FC<RatingControlProps> = ({
  value,
  onChange,
  size = 'md'
}) => {
  return (
    <div className={`${styles.ratingControl} ${styles[size]}`}>
      {[1, 2, 3, 4, 5].map((rating) => (
        <button
          key={rating}
          className={`${styles.ratingButton} ${value >= rating ? styles.active : ''}`}
          onClick={() => onChange(rating)}
        >
          ★
        </button>
      ))}
    </div>
  );
};
