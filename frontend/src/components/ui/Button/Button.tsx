import React from 'react';
import { motion } from 'framer-motion';
import { clsx } from 'clsx';
import styles from './Button.module.css';

interface ButtonProps extends React.ComponentProps<typeof motion.button> {
  variant?: 'primary' | 'secondary' | 'destructive' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export const Button: React.FC<Omit<ButtonProps, 'children'> & { children?: React.ReactNode }> = ({
  children,
  variant = 'primary',
  size = 'md',
  isLoading = false,
  leftIcon,
  rightIcon,
  className,
  disabled,
  ...props
}) => {
  return (
    <motion.button
      className={clsx(
        styles.button,
        styles[variant],
        styles[size],
        isLoading && styles.loading,
        className
      )}
      disabled={disabled || isLoading}
      whileHover={{ scale: disabled || isLoading ? 1 : 1.02 }}
      whileTap={{ scale: disabled || isLoading ? 1 : 0.98 }}
      transition={{ duration: 0.15 }}
      {...props}
    >
      {leftIcon && <span className={styles.leftIcon}>{leftIcon}</span>}
      
      <span className={styles.content}>
        {isLoading ? (
          <div className={styles.spinner}>
            <div className={styles.spinnerDot} />
            <div className={styles.spinnerDot} />
            <div className={styles.spinnerDot} />
          </div>
        ) : (
          children
        )}
      </span>
      
      {rightIcon && <span className={styles.rightIcon}>{rightIcon}</span>}
    </motion.button>
  );
};
