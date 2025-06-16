import React from 'react';
import { useResponsive } from '../../hooks/useResponsive';
import { TabBar } from './Navigation/TabBar';
import { SideBar } from './Navigation/SideBar';
import { Header } from './Header/Header';
import styles from './Layout.module.css';

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { isMobile, isTablet } = useResponsive();

  return (
    <div className={styles.layout}>
      {!isMobile && <Header />}
      
      <div className={styles.content}>
        {!isMobile && !isTablet && (
          <aside className={styles.sidebar}>
            <SideBar />
          </aside>
        )}
        
        <main className={styles.main}>
          {children}
        </main>
      </div>
      
      {isMobile && (
        <nav className={styles.mobileNav}>
          <TabBar />
        </nav>
      )}
    </div>
  );
};
