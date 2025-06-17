import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { MagnifyingGlassIcon, BellIcon, UserCircleIcon, SunIcon, MoonIcon } from '@heroicons/react/24/outline';
import styles from './Header.module.css';

export const Header: React.FC = () => {
  const [lightMode, setLightMode] = useState(false);

  useEffect(() => {
    if (lightMode) {
      document.body.classList.add('light');
    } else {
      document.body.classList.remove('light');
    }
  }, [lightMode]);

  return (
    <header className={`${styles.header} liquid-glass`}>
      <div className={styles.headerContent}>
        <div className={styles.logo}>
          <h1 className={styles.logoText}>Support Agent</h1>
        </div>
        
        <div className={styles.searchContainer}>
          <MagnifyingGlassIcon className={styles.searchIcon} />
          <input 
            type="text" 
            placeholder="Search conversations..."
            className={styles.searchInput}
          />
        </div>
        
        <div className={styles.headerActions}>
          <motion.button 
            className={styles.actionButton}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <BellIcon className={styles.actionIcon} />
          </motion.button>
          
          <motion.button 
            className={styles.actionButton}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <UserCircleIcon className={styles.actionIcon} />
          </motion.button>
        </div>
      </div>
      <div className={styles.themeToggle}>
        <button
          aria-label={lightMode ? 'Switch to dark mode' : 'Switch to light mode'}
          onClick={() => setLightMode((v) => !v)}
          className={styles.themeToggleBtn}
        >
          {lightMode ? (
            <SunIcon className={styles.themeIcon} />
          ) : (
            <MoonIcon className={styles.themeIcon} />
          )}
        </button>
      </div>
    </header>
  );
};
