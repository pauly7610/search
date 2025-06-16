import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  ChatBubbleLeftIcon,
  ChartBarIcon,
  Cog6ToothIcon,
  UserIcon,
  BookOpenIcon,
  QuestionMarkCircleIcon
} from '@heroicons/react/24/outline';
import styles from './Navigation.module.css';

const sidebarItems = [
  { path: '/', icon: ChatBubbleLeftIcon, label: 'Chat', category: 'main' },
  { path: '/analytics', icon: ChartBarIcon, label: 'Analytics', category: 'main' },
  { path: '/knowledge', icon: BookOpenIcon, label: 'Knowledge Base', category: 'main' },
  { path: '/help', icon: QuestionMarkCircleIcon, label: 'Help', category: 'secondary' },
  { path: '/settings', icon: Cog6ToothIcon, label: 'Settings', category: 'secondary' },
  { path: '/profile', icon: UserIcon, label: 'Profile', category: 'secondary' },
];

export const SideBar: React.FC = () => {
  const location = useLocation();
  
  const mainItems = sidebarItems.filter(item => item.category === 'main');
  const secondaryItems = sidebarItems.filter(item => item.category === 'secondary');

  return (
    <nav className={`${styles.sidebar} liquid-glass`}>
      <div className={styles.sidebarContent}>
        <div className={styles.sidebarSection}>
          {mainItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) => 
                `${styles.sidebarItem} ${isActive ? styles.active : ''}`
              }
            >
              <motion.div
                className={styles.sidebarItemContent}
                whileHover={{ x: 4 }}
                transition={{ duration: 0.2 }}
              >
                <item.icon className={styles.sidebarIcon} />
                <span className={styles.sidebarLabel}>{item.label}</span>
              </motion.div>
            </NavLink>
          ))}
        </div>
        
        <div className={styles.sidebarDivider} />
        
        <div className={styles.sidebarSection}>
          {secondaryItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) => 
                `${styles.sidebarItem} ${isActive ? styles.active : ''}`
              }
            >
              <motion.div
                className={styles.sidebarItemContent}
                whileHover={{ x: 4 }}
                transition={{ duration: 0.2 }}
              >
                <item.icon className={styles.sidebarIcon} />
                <span className={styles.sidebarLabel}>{item.label}</span>
              </motion.div>
            </NavLink>
          ))}
        </div>
      </div>
    </nav>
  );
};
