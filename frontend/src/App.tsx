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
  const { isMobile } = useResponsive()

  return (
    <Layout>
      <Routes>
        <Route path="/" element={<ChatInterface />} />
        <Route path="/analytics" element={<Dashboard />} />
        <Route path="/knowledge" element={<KnowledgeBasePage />} />
        <Route path="/help" element={<HelpPage />} />
        <Route path="/settings" element={<SettingsPage />} />
        <Route path="/profile" element={<ProfilePage />} />
      </Routes>
    </Layout>
  )
}

export default App 