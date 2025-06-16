import React from 'react';
import { motion } from 'framer-motion';
import { clsx } from 'clsx';
import styles from './Card.module.css';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  variant?: 'default' | 'elevated' | 'outlined';
  hoverable?: boolean;
  onClick?: () => void;
}

export const Card: React.FC<CardProps> = ({
  children,
  className,
  variant = 'default',
  hoverable = false,
  onClick
}) => {
  const Component = onClick ? motion.button : motion.div;
  
  return (
    <Component
      className={clsx(
        styles.card,
        styles[variant],
        hoverable && styles.hoverable,
        onClick && styles.clickable,
        'liquid-glass',
        className
      )}
      onClick={onClick}
      whileHover={hoverable ? { y: -2, scale: 1.02 } : undefined}
      whileTap={onClick ? { scale: 0.98 } : undefined}
      transition={{ duration: 0.2 }}
    >
      {children}
    </Component>
  );
};

export const CardHeader: React.FC<{ children: React.ReactNode; className?: string }> = ({
  children,
  className
}) => (
  <div className={clsx(styles.cardHeader, className)}>
    {children}
  </div>
);

export const CardContent: React.FC<{ children: React.ReactNode; className?: string }> = ({
  children,
  className
}) => (
  <div className={clsx(styles.cardContent, className)}>
    {children}
  </div>
);

export const CardFooter: React.FC<{ children: React.ReactNode; className?: string }> = ({
  children,
  className
}) => (
  <div className={clsx(styles.cardFooter, className)}>
    {children}
  </div>
);
