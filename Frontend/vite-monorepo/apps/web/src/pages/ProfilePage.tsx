import { useEffect, useState } from "react"
import { useParams, useNavigate } from "react-router-dom"
import { fetchFullProfile, type FullProfile } from "@/api/users"
import { getAssetUrl } from "@/api/client"
import { Loader2, ArrowLeft } from "lucide-react"

export function ProfilePage() {
  const { userId } = useParams<{ userId?: string }>()
  const navigate = useNavigate()

  const [profile, setProfile] = useState<FullProfile | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadProfile = async () => {
      try {
        setLoading(true)
        setError(null)
        const parsedUserId = userId ? parseInt(userId, 10) : undefined
        const data = await fetchFullProfile(parsedUserId)
        setProfile(data)
      } catch (err: any) {
        console.error("Gagal memuat data profil:", err)
        setError(err.response?.data?.detail || "Gagal memuat profil pengguna")
      } finally {
        setLoading(false)
      }
    }

    loadProfile()
  }, [userId])

  return (
    <div className="flex flex-col items-center w-full">
      {/* Title */}
      <h1 className="text-3xl font-bold text-white mb-8 tracking-wide">Profil</h1>

      {/* Optional Back Button if viewing a specific user */}
      {userId && (
        <div className="w-full max-w-md mb-4 flex items-center justify-start">
          <button
            type="button"
            onClick={() => navigate("/users")}
            className="flex items-center gap-1.5 text-xs text-neutral-300 hover:text-white bg-[#222222] border border-neutral-600 px-3 py-1.5 rounded-lg transition-colors cursor-pointer"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Kembali ke Daftar Users</span>
          </button>
        </div>
      )}

      {error && (
        <div className="w-full max-w-md mb-4 p-3 rounded-lg bg-red-500/20 border border-red-500/40 text-red-200 text-sm text-center">
          {error}
        </div>
      )}

      {/* Main Profile Card */}
      <div className="w-full max-w-md bg-[#141414] border border-neutral-600/80 rounded-[2.2rem] shadow-2xl p-8 sm:p-10 text-white">
        {loading ? (
          <div className="flex flex-col items-center justify-center py-16 text-neutral-400">
            <Loader2 className="w-8 h-8 animate-spin mb-3 text-neutral-300" />
            <p className="text-sm">Memuat informasi profil...</p>
          </div>
        ) : profile ? (
          <div>
            {/* Foto Avatar Frame */}
            <div className="flex justify-center mb-10">
              <div className="w-28 h-28 rounded-full border border-white/80 flex items-center justify-center overflow-hidden bg-neutral-900 shadow-md">
                {profile.avatar &&
                profile.avatar !== "app/static/profile_images/avatar/avatar_img.jpg" ? (
                  <img
                    src={getAssetUrl(profile.avatar)}
                    alt="Foto Profil"
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      ;(e.target as HTMLElement).style.display = "none"
                    }}
                  />
                ) : (
                  <span className="text-white text-base font-medium">Foto</span>
                )}
              </div>
            </div>

            {/* Profile Info Key-Value List */}
            <div className="space-y-6 text-sm sm:text-base px-2">
              {/* Nama */}
              <div className="flex items-center">
                <span className="w-24 text-neutral-200 font-normal">Nama</span>
                <span className="text-white font-medium flex-1">
                  {profile.full_name || "-"}
                </span>
              </div>

              {/* Email */}
              <div className="flex items-center">
                <span className="w-24 text-neutral-200 font-normal">email</span>
                <span className="text-white font-mono text-xs sm:text-sm flex-1 break-all">
                  {profile.email}
                </span>
              </div>

              {/* Phone */}
              <div className="flex items-center">
                <span className="w-24 text-neutral-200 font-normal">phone</span>
                <span className="text-white flex-1 font-mono text-xs sm:text-sm">
                  {profile.phone_number || "-"}
                </span>
              </div>

              {/* Role */}
              <div className="flex items-center">
                <span className="w-24 text-neutral-200 font-normal">role</span>
                <span className="text-white font-medium capitalize flex-1">
                  {profile.role}
                </span>
              </div>

              {/* Status */}
              <div className="flex items-center">
                <span className="w-24 text-neutral-200 font-normal">status</span>
                <span className="text-white flex-1">
                  {profile.is_active ? "aktif" : "non-aktif"}
                </span>
              </div>
            </div>
          </div>
        ) : (
          <p className="text-center text-neutral-400 py-10">Data profil tidak ditemukan</p>
        )}
      </div>
    </div>
  )
}
