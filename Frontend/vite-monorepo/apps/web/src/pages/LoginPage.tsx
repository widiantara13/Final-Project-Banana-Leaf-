import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { loginUser } from "@/api/auth"
import { Sprout } from "lucide-react"

export function LoginPage() {
  const navigate = useNavigate()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)

    if (!email || !password) {
      setError("Email dan password wajib diisi")
      return
    }

    try {
      setLoading(true)
      const data = await loginUser(email, password)
      localStorage.setItem("token", data.access_token)
      navigate("/")
    } catch (err: any) {
      console.error("Login failed:", err)
      if (err.response?.data?.detail) {
        setError(err.response.data.detail)
      } else if (err.code === "ERR_NETWORK") {
        setError("Gagal terhubung ke server backend (pastikan FastAPI aktif di port 8000)")
      } else {
        setError("Terjadi kesalahan saat login")
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-[#ececec] flex flex-col items-center justify-center p-4 select-none">
      {/* Top Logo Badge (Identik dengan versi Mobile) */}
      <div className="mb-8 flex items-center gap-3.5 bg-white border border-emerald-500/20 rounded-2xl px-5 py-3 shadow-md shadow-emerald-950/5">
        <div className="w-11 h-11 rounded-xl bg-emerald-100 border border-emerald-500/30 flex items-center justify-center shrink-0">
          <Sprout className="w-6 h-6 text-emerald-600 stroke-[2.2]" />
        </div>
        <div className="flex flex-col text-left">
          <div className="flex items-center gap-1.5">
            <span className="font-bold text-neutral-800 text-base tracking-tight">
              Banana Leaf
            </span>
            <span className="w-2 h-2 rounded-full bg-yellow-500 shrink-0" />
          </div>
          <span className="text-[11px] text-neutral-500 font-medium tracking-tight">
            Sistem Deteksi Penyakit
          </span>
        </div>
      </div>

      {/* Main Login Card */}
      <div className="w-full max-w-[420px] bg-[#3a3a3a] rounded-[2.2rem] shadow-xl p-8 sm:p-10 text-white">
        <h1 className="text-2xl font-semibold text-center mb-8 tracking-wide">
          Login
        </h1>

        {error && (
          <div className="mb-6 p-3 rounded-lg bg-red-500/20 border border-red-500/50 text-red-200 text-xs text-center">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Email Field */}
          <div>
            <label className="block text-sm font-medium mb-2 text-neutral-100">
              Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="email"
              required
              className="w-full px-4 py-3 rounded-lg bg-[#181818] border border-neutral-700 text-white placeholder-neutral-500 text-sm focus:outline-none focus:border-neutral-400 transition-colors"
            />
          </div>

          {/* Password Field */}
          <div>
            <label className="block text-sm font-medium mb-2 text-neutral-100">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="password"
              required
              className="w-full px-4 py-3 rounded-lg bg-[#181818] border border-neutral-700 text-white placeholder-neutral-500 text-sm focus:outline-none focus:border-neutral-400 transition-colors"
            />
          </div>

          {/* Login Button */}
          <div className="pt-2 flex justify-center">
            <button
              type="submit"
              disabled={loading}
              className="px-8 py-2.5 rounded-lg bg-[#222222] border border-neutral-400 text-white text-sm font-medium hover:bg-neutral-800 active:scale-95 transition-all cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? "Loading..." : "Login"}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

