import { useEffect, useState } from "react"
import { Outlet, useNavigate } from "react-router-dom"
import { Sidebar } from "./Sidebar"

export function AdminLayout() {
  const navigate = useNavigate()
  const [collapsed, setCollapsed] = useState(false)

  useEffect(() => {
    const token = localStorage.getItem("token")
    if (!token) {
      navigate("/login")
    }
  }, [navigate])

  return (
    <div className="h-screen w-screen overflow-hidden flex bg-[#383838] font-sans text-white">
      {/* Fixed Height Sidebar dengan Fitur Collapsible bawaan */}
      <Sidebar collapsed={collapsed} onToggle={() => setCollapsed(!collapsed)} />

      {/* Main Content Area - Scroll independen agar sidebar tidak tertarik memanjang */}
      <main className="flex-1 h-screen overflow-y-auto p-6 sm:p-8 lg:p-10 flex flex-col items-center">
        <div className="w-full max-w-6xl">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
