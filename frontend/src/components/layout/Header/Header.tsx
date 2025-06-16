import React from 'react';
import { motion } from 'framer-motion';
import { MagnifyingGlassIcon, BellIcon, UserCircleIcon } from '@heroicons/react/24/outline';
import styles from './Header.module.css';

export const Header: React.FC = () => {
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
    </header>
  );
};
