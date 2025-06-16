import React, { forwardRef } from 'react';
import { clsx } from 'clsx';
import { ExclamationCircleIcon } from '@heroicons/react/24/outline';
import styles from './Input.module.css';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helper?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(({
  label,
  error,
  helper,
  leftIcon,
  rightIcon,
  className,
  ...props
}, ref) => {
  return (
    <div className={styles.inputGroup}>
      {label && (
        <label className={styles.label} htmlFor={props.id}>
          {label}
        </label>
      )}
      
      <div className={styles.inputWrapper}>
        {leftIcon && (
          <div className={styles.leftIcon}>
            {leftIcon}
          </div>
        )}
        
        <input
          ref={ref}
          className={clsx(
            styles.input,
            leftIcon && styles.hasLeftIcon,
            rightIcon && styles.hasRightIcon,
            error && styles.error,
            className
          )}
          {...props}
        />
        
        {rightIcon && !error && (
          <div className={styles.rightIcon}>
            {rightIcon}
          </div>
        )}
        
        {error && (
          <div className={styles.errorIcon}>
            <ExclamationCircleIcon />
          </div>
        )}
      </div>
      
      {(error || helper) && (
        <div className={clsx(
          styles.helperText,
          error && styles.errorText
        )}>
          {error || helper}
        </div>
      )}
    </div>
  );
});

Input.displayName = 'Input';
