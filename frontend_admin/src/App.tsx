import { Routes, Route, Navigate } from 'react-router-dom'
import { Layout } from './components/layout/Layout'
import { Dashboard } from './pages/Dashboard'
import { DatabaseManagement } from './pages/DatabaseManagement'
import { GraphManagement } from './pages/GraphManagement'
import { UserManagement } from './pages/UserManagement'
import { FileUpload } from './pages/FileUpload'
import { Analytics } from './pages/Analytics'
import { Settings } from './pages/Settings'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/databases" element={<DatabaseManagement />} />
        <Route path="/graphs" element={<GraphManagement />} />
        <Route path="/users" element={<UserManagement />} />
        <Route path="/upload" element={<FileUpload />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route path="/settings" element={<Settings />} />
      </Routes>
    </Layout>
  )
}

export default App
