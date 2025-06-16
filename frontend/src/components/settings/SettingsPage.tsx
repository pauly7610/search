import React from 'react';
import styles from './SettingsPage.module.css';

export const SettingsPage: React.FC = () => {
  return (
    <div className={styles.settingsPage}>
      <header className={styles.header}>
        <h1>Settings</h1>
      </header>
      <section className={styles.settingsSection}>
        <div className={styles.placeholder}>
          <p>User settings (theme, notifications, etc.) coming soon.</p>
        </div>
      </section>
    </div>
  );
}; 