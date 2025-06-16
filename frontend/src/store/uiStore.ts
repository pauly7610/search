import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

interface UIState {
  // Theme
  isDarkMode: boolean;
  theme: 'light' | 'dark' | 'system';
  
  // Layout
  sidebarCollapsed: boolean;
  isMobileMenuOpen: boolean;
  
  // Modals and overlays
  activeModal: string | null;
  isLoading: boolean;
  
  // Notifications
  notifications: Array<{
    id: string;
    type: 'success' | 'error' | 'warning' | 'info';
    message: string;
    timestamp: string;
  }>;
}

interface UIStore extends UIState {
  // Theme actions
  setTheme: (theme: 'light' | 'dark' | 'system') => void;
  toggleDarkMode: () => void;
  
  // Layout actions
  toggleSidebar: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  toggleMobileMenu: () => void;
  setMobileMenuOpen: (open: boolean) => void;
  
  // Modal actions
  openModal: (modalId: string) => void;
  closeModal: () => void;
  setLoading: (loading: boolean) => void;
  
  // Notification actions
  addNotification: (notification: Omit<UIState['notifications'][0], 'id' | 'timestamp'>) => void;
  removeNotification: (id: string) => void;
  clearNotifications: () => void;
}

export const useUIStore = create<UIStore>()(
  devtools(
    (set, get) => ({
      // Initial state
      isDarkMode: false,
      theme: 'system',
      sidebarCollapsed: false,
      isMobileMenuOpen: false,
      activeModal: null,
      isLoading: false,
      notifications: [],

      // Theme actions
      setTheme: (theme) => {
        const isDarkMode = theme === 'dark' || 
          (theme === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches);
        
        set({ theme, isDarkMode });
        
        // Update document class for CSS
        document.documentElement.classList.toggle('dark', isDarkMode);
      },

      toggleDarkMode: () => {
        const newDarkMode = !get().isDarkMode;
        set({ 
          isDarkMode: newDarkMode,
          theme: newDarkMode ? 'dark' : 'light'
        });
        document.documentElement.classList.toggle('dark', newDarkMode);
      },

      // Layout actions
      toggleSidebar: () => set((state) => ({ 
        sidebarCollapsed: !state.sidebarCollapsed 
      })),

      setSidebarCollapsed: (collapsed) => set({ sidebarCollapsed: collapsed }),

      toggleMobileMenu: () => set((state) => ({ 
        isMobileMenuOpen: !state.isMobileMenuOpen 
      })),

      setMobileMenuOpen: (open) => set({ isMobileMenuOpen: open }),

      // Modal actions
      openModal: (modalId) => set({ activeModal: modalId }),
      closeModal: () => set({ activeModal: null }),
      setLoading: (loading) => set({ isLoading: loading }),

      // Notification actions
      addNotification: (notification) => 
        set((state) => ({
          notifications: [
            ...state.notifications,
            {
              ...notification,
              id: Date.now().toString(),
              timestamp: new Date().toISOString(),
            },
          ],
        })),

      removeNotification: (id) =>
        set((state) => ({
          notifications: state.notifications.filter(n => n.id !== id),
        })),

      clearNotifications: () => set({ notifications: [] }),
    }),
    { name: 'UIStore' }
  )
);
