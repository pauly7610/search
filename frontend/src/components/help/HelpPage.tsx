import React from 'react';
import styles from './HelpPage.module.css';

export const HelpPage: React.FC = () => {
  return (
    <div className={styles.helpPage}>
      <header className={styles.header}>
        <h1>Help & Support</h1>
      </header>
      <section className={styles.faqSection}>
        <h2>Frequently Asked Questions</h2>
        <ul>
          <li>How do I reset my password?</li>
          <li>How can I contact support?</li>
          <li>Where can I find my billing information?</li>
        </ul>
      </section>
      <section className={styles.contactSection}>
        <h2>Contact Us</h2>
        <div className={styles.placeholder}>
          <p>Contact form coming soon.</p>
        </div>
      </section>
    </div>
  );
}; 