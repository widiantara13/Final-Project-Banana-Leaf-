import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom"
import { LoginPage } from "@/pages/LoginPage"
import { AdminLayout } from "@/components/layout/AdminLayout"
import { DashboardPage } from "@/pages/DashboardPage"
import { UsersPage } from "@/pages/UsersPage"
import { PredictionsPage } from "@/pages/PredictionsPage"
import { LogsPage } from "@/pages/LogsPage"
import { LeafConditionsPage } from "@/pages/LeafConditionsPage"
import { ModelsPage } from "@/pages/ModelsPage"
import { ProfilePage } from "@/pages/ProfilePage"

export function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />

        {/* Protected Admin Routes with Sidebar Layout */}
        <Route element={<AdminLayout />}>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/users" element={<UsersPage />} />
          <Route path="/predictions" element={<PredictionsPage />} />
          <Route path="/logs" element={<LogsPage />} />
          <Route path="/leaf-conditions" element={<LeafConditionsPage />} />
          <Route path="/models" element={<ModelsPage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/profile/:userId" element={<ProfilePage />} />
        </Route>

        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
