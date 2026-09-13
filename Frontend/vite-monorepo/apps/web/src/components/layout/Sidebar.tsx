import { NavLink, useNavigate } from "react-router-dom"
import {
  User,
  LogOut,
  LayoutDashboard,
  Users as UsersIcon,
  History,
  FileText,
  Leaf,
  Cpu,
  PanelLeftClose,
  PanelLeftOpen,
} from "lucide-react"
import { useState } from "react"
import { logoutUser } from "@/api/auth"

interface NavItem {
  title: string
  path: string
  icon: any
}

const navItems: NavItem[] = [
  { title: "Dashboard", path: "/", icon: LayoutDashboard },
  { title: "Users", path: "/users", icon: UsersIcon },
  { title: "Riwayat Prediksi", path: "/predictions", icon: History },
  { title: "Log Aktivitas", path: "/logs", icon: FileText },
  { title: "Kondisi Daun", path: "/leaf-conditions", icon: Leaf },
  { title: "Model", path: "/models", icon: Cpu },
]

interface SidebarProps {
  collapsed: boolean
  onToggle: () => void
}

export function Sidebar({ collapsed, onToggle }: SidebarProps) {
  const navigate = useNavigate()
  const [showProfileMenu, setShowProfileMenu] = useState(false)

  const handleLogout = async () => {
    await logoutUser()
    navigate("/login")
  }

  return (
    <aside
      className={`h-screen bg-[#121212] border-r border-neutral-800 flex flex-col justify-between select-none shrink-0 relative transition-all duration-300 z-30 ${
        collapsed ? "w-20 p-3" : "w-64 p-6"
      }`}
    >
      {/* Top Section & Navigation */}
      <div className="flex flex-col items-center w-full">
        {/* Header with Toggle Button */}
        <div className="w-full flex items-center justify-between mb-4">
          {!collapsed && (
            <span className="text-[11px] font-mono uppercase tracking-wider text-neutral-500">
              Menu Admin
            </span>
          )}
          <button
            type="button"
            onClick={onToggle}
            title={collapsed ? "Buka Sidebar" : "Sembunyikan Sidebar"}
            className={`p-1.5 rounded-lg text-neutral-400 hover:text-white hover:bg-neutral-800/80 transition-colors cursor-pointer active:scale-95 ${
              collapsed ? "mx-auto" : "ml-auto"
            }`}
          >
            {collapsed ? (
              <PanelLeftOpen className="w-5 h-5 text-emerald-400" />
            ) : (
              <PanelLeftClose className="w-5 h-5" />
            )}
          </button>
        </div>

        {/* Logo Container */}
        <div
          className={`border-2 border-white/80 rounded-md flex items-center justify-center text-white font-semibold shadow-sm transition-all ${
            collapsed ? "w-12 h-12 text-xs mb-6" : "w-28 h-28 text-lg mb-8"
          }`}
        >
          {collapsed ? "BLD" : "Logo"}
        </div>

        {/* Nav Links */}
        <nav className="w-full flex flex-col space-y-3">
          {navItems.map((item) => {
            const Icon = item.icon
            return (
              <NavLink
                key={item.path}
                to={item.path}
                end={item.path === "/"}
                title={collapsed ? item.title : undefined}
                className={({ isActive }) =>
                  collapsed
                    ? `w-12 h-12 mx-auto rounded-xl flex items-center justify-center transition-all border ${
                        isActive
                          ? "bg-[#383838] border-white text-white shadow-sm ring-1 ring-white/30"
                          : "bg-[#222222] border-neutral-600/60 text-neutral-300 hover:bg-[#303030] hover:text-white hover:border-white/80"
                      }`
                    : `w-full py-3 px-4 rounded-xl text-center text-sm font-medium transition-all block border ${
                        isActive
                          ? "bg-[#383838] border-white text-white shadow-sm ring-1 ring-white/30"
                          : "bg-[#222222] border-neutral-500/60 text-white hover:bg-[#303030] hover:border-white/80"
                      }`
                }
              >
                {collapsed ? <Icon className="w-5 h-5" /> : item.title}
              </NavLink>
            )
          })}
        </nav>
      </div>

      {/* Bottom Profile / Avatar Section */}
      <div className="relative flex flex-col items-center pt-4">
        {/* Profile Popover Menu */}
        {showProfileMenu && (
          <div
            className={`absolute bottom-20 bg-[#222222] border border-neutral-700 rounded-xl p-2 w-48 shadow-xl text-white text-sm z-50 animate-in fade-in zoom-in-95 duration-150 ${
              collapsed ? "left-16" : ""
            }`}
          >
            <button
              onClick={() => {
                setShowProfileMenu(false)
                navigate("/profile")
              }}
              className="w-full flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-neutral-800 transition-colors text-left cursor-pointer"
            >
              <User className="w-4 h-4" />
              <span>Profil Admin</span>
            </button>
            <button
              onClick={handleLogout}
              className="w-full flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-red-500/20 text-red-300 transition-colors text-left cursor-pointer"
            >
              <LogOut className="w-4 h-4" />
              <span>Keluar (Logout)</span>
            </button>
          </div>
        )}

        <button
          type="button"
          onClick={() => setShowProfileMenu(!showProfileMenu)}
          className={`rounded-full bg-white flex items-center justify-center shadow-lg hover:scale-105 active:scale-95 transition-all cursor-pointer border-2 border-transparent hover:border-neutral-300 ${
            collapsed ? "w-11 h-11" : "w-16 h-16"
          }`}
          title="Menu Profil"
        >
          <User
            className={`text-neutral-900 stroke-[2.2] ${
              collapsed ? "w-6 h-6" : "w-9 h-9"
            }`}
          />
        </button>
      </div>
    </aside>
  )
}
