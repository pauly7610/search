import React from 'react';
import { NavLink, NavLinkProps } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  ChatBubbleLeftIcon,
  ChartBarIcon,
  Cog6ToothIcon,
  UserIcon
} from '@heroicons/react/24/outline';
import styles from './Navigation.module.css';

interface Tab {
  path: string;
  icon: React.ComponentType<React.SVGProps<SVGSVGElement>>;
  label: string;
}

const tabs: Tab[] = [
  { path: '/', icon: ChatBubbleLeftIcon, label: 'Chat' },
  { path: '/analytics', icon: ChartBarIcon, label: 'Analytics' },
  { path: '/settings', icon: Cog6ToothIcon, label: 'Settings' },
  { path: '/profile', icon: UserIcon, label: 'Profile' },
];

export const TabBar: React.FC = () => {
  return (
    <nav className={styles.tabBar}>
      {tabs.map((tab) => (
        <NavLink
          key={tab.path}
          to={tab.path}
          className={({ isActive }: { isActive: boolean }) =>
            `${styles.tab} ${isActive ? styles.active : ''}`
          }
        >
          {({ isActive }: { isActive: boolean }) => (
            <motion.div
              className={styles.tabContent}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <tab.icon className={styles.tabIcon} />
              <span className={styles.tabLabel}>{tab.label}</span>
              {isActive && (
                <motion.div
                  className={styles.activeIndicator}
                  layoutId="activeTab"
                  transition={{ type: "spring", stiffness: 300, damping: 30 }}
                />
              )}
            </motion.div>
          )}
        </NavLink>
      ))}
    </nav>
  );
};