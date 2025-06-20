/**
 * Main Application Component for Customer Support Chat Interface
 * 
 * This is the root component that sets up the application structure,
 * routing configuration, and global layout. It serves as the entry point
 * for the React-powered customer support interface.
 * 
 * Key Features:
 * - React Router for client-side navigation
 * - Responsive layout with mobile optimization
 * - Modular component architecture
 * - Clean separation of concerns between views
 * 
 * The application follows a single-page application (SPA) pattern
 * with multiple views accessible through client-side routing.
 */

import React from 'react'
import { Routes, Route } from 'react-router-dom'
import { Layout } from './components/layout/Layout'
import { ChatInterface } from './components/chat/ChatInterface/ChatInterface'
import { Dashboard } from './components/analytics/Dashboard/Dashboard'
import { useResponsive } from './hooks/useResponsive'
import { KnowledgeBasePage } from './components/knowledge/KnowledgeBasePage'
import { HelpPage } from './components/help/HelpPage'
import { SettingsPage } from './components/settings/SettingsPage'
import { ProfilePage } from './components/profile/ProfilePage'

function App() {
  /**
   * Main application component with routing and responsive design.
   * 
   * This component orchestrates the entire application by:
   * 1. Setting up responsive design hooks for mobile optimization
   * 2. Configuring client-side routing with React Router
   * 3. Wrapping all routes in a consistent layout component
   * 4. Defining the navigation structure for the application
   * 
   * The routing structure follows a logical hierarchy:
   * - / (Home): Main chat interface for customer interactions
   * - /analytics: Performance dashboard and metrics
   * - /knowledge: Knowledge base management and browsing
   * - /help: User help and documentation
   * - /settings: Application configuration
   * - /profile: User profile management
   * 
   * The responsive design ensures optimal user experience across
   * desktop, tablet, and mobile devices.
   */
  
  // Hook for responsive design detection and mobile optimization
  // This enables conditional rendering and styling based on screen size
  const { isMobile } = useResponsive()

  return (
    // Layout wrapper provides consistent structure across all routes
    // including navigation, header, and content areas
    <Layout>
      {/* React Router configuration for client-side navigation */}
      <Routes>
        {/* Main chat interface - primary user interaction point */}
        <Route path="/" element={<ChatInterface />} />
        
        {/* Analytics dashboard for performance monitoring and insights */}
        <Route path="/analytics" element={<Dashboard />} />
        
        {/* Knowledge base management and browsing interface */}
        <Route path="/knowledge" element={<KnowledgeBasePage />} />
        
        {/* Help and documentation section for user assistance */}
        <Route path="/help" element={<HelpPage />} />
        
        {/* Application settings and configuration panel */}
        <Route path="/settings" element={<SettingsPage />} />
        
        {/* User profile management and customization */}
        <Route path="/profile" element={<ProfilePage />} />
      </Routes>
    </Layout>
  )
}

export default App 