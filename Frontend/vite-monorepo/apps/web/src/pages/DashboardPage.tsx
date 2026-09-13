import { useEffect, useState, useRef } from "react"
import { Link } from "react-router-dom"
import {
  fetchDashboardSummary,
  type DashboardSummaryResponse,
} from "@/api/dashboard"
import { getAssetUrl, API_BASE_URL } from "@/api/client"
import {
  Users,
  UserCheck,
  Activity,
  ChevronRight,
  Loader2,
  Calendar,
  Image as ImageIcon,
} from "lucide-react"

export function DashboardPage() {
  const [summary, setSummary] = useState<DashboardSummaryResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [hoveredTrendIndex, setHoveredTrendIndex] = useState<number | null>(null)
  const [isLive, setIsLive] = useState(false)
  const eventSourceRef = useRef<EventSource | null>(null)

  const loadData = async (silent = false) => {
    try {
      if (!silent) setLoading(true)
      setError(null)
      const data = await fetchDashboardSummary()
      setSummary(data)
    } catch (err: any) {
      console.error("Gagal memuat ringkasan dashboard:", err)
      if (!silent) {
        setError(err.response?.data?.detail || "Gagal memuat data ringkasan dashboard dari server")
      }
    } finally {
      if (!silent) setLoading(false)
    }
  }

  useEffect(() => {
    loadData(false)

    // Setup Live Server-Sent Events (SSE)
    const token = localStorage.getItem("token")
    if (!token) return

    const sseUrl = `${API_BASE_URL}/dashboard/stream?token=${encodeURIComponent(token)}`
    const es = new EventSource(sseUrl)
    eventSourceRef.current = es

    es.onopen = () => {
      setIsLive(true)
    }

    es.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        if (data.type === "NEW_ACTIVITY") {
          // Ketika ada aktivitas baru (prediksi, login, dll.), refetch data dashboard secara halus di latar belakang
          loadData(true)
        }
      } catch (e) {
        // Heartbeat comment or ping
      }
    }

    es.onerror = () => {
      setIsLive(false)
    }

    return () => {
      es.close()
      eventSourceRef.current = null
    }
  }, [])

  const formatDateTime = (dateString?: string | null) => {
    if (!dateString) return "-"
    return dateString.replace("T", " ").split(".")[0]
  }

  const formatPercentage = (val?: number) => {
    if (val === null || val === undefined) return "-"
    return val % 1 === 0 ? `${val}%` : `${val.toFixed(1)}%`
  }

  return (
    <div className="flex flex-col items-center w-full max-w-6xl mx-auto space-y-6 pb-12">
      {/* Title & Live Status Indicator */}
      <div className="flex flex-col items-center gap-2 mb-2">
        <h1 className="text-3xl font-bold text-white tracking-wide text-center">
          Dashboard
        </h1>
        <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-[#161616] border border-neutral-700/80 text-xs">
          <span
            className={`w-2 h-2 rounded-full transition-colors ${
              isLive
                ? "bg-emerald-400 animate-pulse shadow-xs shadow-emerald-400"
                : "bg-neutral-500"
            }`}
          />
          <span className={isLive ? "text-emerald-300 font-medium" : "text-neutral-400"}>
            {isLive ? "Live Real-Time Aktif" : "Menyambungkan Live..."}
          </span>
        </div>
      </div>

      {error && (
        <div className="w-full p-3.5 rounded-xl bg-red-500/20 border border-red-500/40 text-red-200 text-sm text-center">
          {error}
        </div>
      )}

      {loading ? (
        <div className="w-full py-32 flex flex-col items-center justify-center gap-3 text-neutral-400">
          <Loader2 className="w-8 h-8 animate-spin text-white" />
          <span className="text-sm">Memuat informasi dashboard...</span>
        </div>
      ) : (
        <>
          {/* BARIS 1: 3 Kartu Ringkasan Utama */}
          <div className="w-full grid grid-cols-1 md:grid-cols-3 gap-5">
            {/* Kartu 1: Jumlah user */}
            <div className="bg-[#141414] border border-neutral-700/80 rounded-2xl p-6 shadow-xl flex flex-col justify-between hover:border-neutral-500/80 transition-colors">
              <div className="flex items-center justify-between mb-3 text-neutral-400">
                <span className="text-sm font-medium text-neutral-200">Jumlah user</span>
                <div className="w-9 h-9 rounded-xl bg-neutral-800/80 border border-neutral-700 flex items-center justify-center text-white">
                  <Users className="w-4 h-4" />
                </div>
              </div>
              <div className="flex items-baseline justify-between mt-1">
                <span className="text-3xl font-bold text-white font-mono">
                  {summary?.total_users ?? 0}
                </span>
                <span className="text-xs text-neutral-400 font-medium">Total Akun</span>
              </div>
            </div>

            {/* Kartu 2: Jumlah user aktif */}
            <div className="bg-[#141414] border border-neutral-700/80 rounded-2xl p-6 shadow-xl flex flex-col justify-between hover:border-neutral-500/80 transition-colors">
              <div className="flex items-center justify-between mb-3 text-neutral-400">
                <span className="text-sm font-medium text-neutral-200">Jumlah user aktif</span>
                <div className="w-9 h-9 rounded-xl bg-emerald-950/60 border border-emerald-800/60 flex items-center justify-center text-emerald-400">
                  <UserCheck className="w-4 h-4" />
                </div>
              </div>
              <div className="flex items-baseline justify-between mt-1">
                <span className="text-3xl font-bold text-emerald-400 font-mono">
                  {summary?.active_users ?? 0}
                </span>
                <span className="text-xs text-emerald-500/80 font-medium flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                  Aktif
                </span>
              </div>
            </div>

            {/* Kartu 3: Jumlah prediksi */}
            <div className="bg-[#141414] border border-neutral-700/80 rounded-2xl p-6 shadow-xl flex flex-col justify-between hover:border-neutral-500/80 transition-colors">
              <div className="flex items-center justify-between mb-3 text-neutral-400">
                <span className="text-sm font-medium text-neutral-200">Jumlah prediksi</span>
                <div className="w-9 h-9 rounded-xl bg-sky-950/60 border border-sky-800/60 flex items-center justify-center text-sky-400">
                  <Activity className="w-4 h-4" />
                </div>
              </div>
              <div className="flex items-baseline justify-between mt-1">
                <span className="text-3xl font-bold text-sky-300 font-mono">
                  {summary?.total_predictions ?? 0}
                </span>
                <span className="text-xs text-sky-400/80 font-medium">Pemindaian</span>
              </div>
            </div>
          </div>

          {/* BARIS 2: 4 Kartu Kondisi Daun */}
          <div className="w-full grid grid-cols-2 md:grid-cols-4 gap-5">
            {/* Kartu 1: Jumlah sigota */}
            <div className="bg-[#141414] border border-neutral-700/80 rounded-2xl p-5 shadow-xl flex flex-col justify-between hover:border-amber-500/50 transition-colors">
              <div className="flex items-center justify-between text-neutral-400 mb-2">
                <span className="text-xs font-semibold uppercase tracking-wider text-neutral-300">
                  Jumlah Sigatoka
                </span>
                <span className="w-2 h-2 rounded-full bg-amber-400" />
              </div>
              <div className="flex items-baseline justify-between mt-2">
                <span className="text-2xl font-bold text-amber-300 font-mono">
                  {summary?.conditions_count.sigatoka ?? 0}
                </span>
                <span className="text-[11px] text-amber-400/70 font-medium">Kasus</span>
              </div>
            </div>

            {/* Kartu 2: Jumlah Cordana */}
            <div className="bg-[#141414] border border-neutral-700/80 rounded-2xl p-5 shadow-xl flex flex-col justify-between hover:border-orange-500/50 transition-colors">
              <div className="flex items-center justify-between text-neutral-400 mb-2">
                <span className="text-xs font-semibold uppercase tracking-wider text-neutral-300">
                  Jumlah Cordana
                </span>
                <span className="w-2 h-2 rounded-full bg-orange-400" />
              </div>
              <div className="flex items-baseline justify-between mt-2">
                <span className="text-2xl font-bold text-orange-300 font-mono">
                  {summary?.conditions_count.cordana ?? 0}
                </span>
                <span className="text-[11px] text-orange-400/70 font-medium">Kasus</span>
              </div>
            </div>

            {/* Kartu 3: Jumlah Daun Sehat (Healthy) */}
            <div className="bg-[#141414] border border-neutral-700/80 rounded-2xl p-5 shadow-xl flex flex-col justify-between hover:border-emerald-500/50 transition-colors">
              <div className="flex items-center justify-between text-neutral-400 mb-2">
                <span className="text-xs font-semibold uppercase tracking-wider text-neutral-300">
                  Jumlah Sehat
                </span>
                <span className="w-2 h-2 rounded-full bg-emerald-400" />
              </div>
              <div className="flex items-baseline justify-between mt-2">
                <span className="text-2xl font-bold text-emerald-300 font-mono">
                  {summary?.conditions_count.healthy ?? 0}
                </span>
                <span className="text-[11px] text-emerald-400/70 font-medium">Sehat</span>
              </div>
            </div>

            {/* Kartu 4: Jumlah Panama */}
            <div className="bg-[#141414] border border-neutral-700/80 rounded-2xl p-5 shadow-xl flex flex-col justify-between hover:border-purple-500/50 transition-colors">
              <div className="flex items-center justify-between text-neutral-400 mb-2">
                <span className="text-xs font-semibold uppercase tracking-wider text-neutral-300">
                  Jumlah Panama
                </span>
                <span className="w-2 h-2 rounded-full bg-purple-400" />
              </div>
              <div className="flex items-baseline justify-between mt-2">
                <span className="text-2xl font-bold text-purple-300 font-mono">
                  {summary?.conditions_count.panama ?? 0}
                </span>
                <span className="text-[11px] text-purple-400/70 font-medium">Kasus</span>
              </div>
            </div>
          </div>

          {/* BARIS 3: Grafik Prediksi & Data User Aktif */}
          <div className="w-full grid grid-cols-1 lg:grid-cols-12 gap-5">
            {/* Kiri (7 Kolom): Grafik Prediksi */}
            <div className="lg:col-span-7 bg-[#141414] border border-neutral-700/80 rounded-2xl p-6 shadow-xl flex flex-col justify-between">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-base font-semibold text-white tracking-wide">
                    Grafik Prediksi
                  </h2>
                  <p className="text-xs text-neutral-400 mt-0.5">
                    Aktivitas prediksi daun pisang 7 hari terakhir
                  </p>
                </div>
                <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-neutral-800 border border-neutral-700 text-xs text-neutral-300 font-mono">
                  <Calendar className="w-3.5 h-3.5 text-neutral-400" />
                  <span>7 Hari Terakhir</span>
                </div>
              </div>

              {/* Chart Visualizer (SVG Bar/Column Chart) */}
              <div className="w-full h-56 flex flex-col justify-end pt-4 pb-1">
                {summary?.prediction_trends && summary.prediction_trends.length > 0 ? (
                  (() => {
                    const trends = summary.prediction_trends
                    const maxVal = Math.max(...trends.map((t) => t.count), 5)

                    return (
                      <div className="flex items-end justify-between gap-3 h-full px-2">
                        {trends.map((item, idx) => {
                          const heightPct = Math.round((item.count / maxVal) * 80) + 8
                          const isHovered = hoveredTrendIndex === idx

                          return (
                            <div
                              key={item.date}
                              className="flex-1 flex flex-col items-center h-full justify-end group cursor-pointer relative"
                              onMouseEnter={() => setHoveredTrendIndex(idx)}
                              onMouseLeave={() => setHoveredTrendIndex(null)}
                            >
                              {/* Tooltip on Hover */}
                              {isHovered && (
                                <div className="absolute -top-10 z-10 px-2 py-1 rounded-md bg-neutral-800 border border-neutral-600 text-[11px] text-white whitespace-nowrap shadow-lg">
                                  <span className="font-semibold text-emerald-400">{item.count}</span>{" "}
                                  prediksi ({item.label})
                                </div>
                              )}

                              {/* Bar Pillar */}
                              <div className="w-full max-w-[36px] flex flex-col justify-end items-center h-full">
                                <div
                                  style={{ height: `${heightPct}%` }}
                                  className={`w-full rounded-t-lg transition-all duration-300 ${
                                    isHovered
                                      ? "bg-emerald-400 shadow-lg shadow-emerald-500/30"
                                      : item.count > 0
                                        ? "bg-gradient-to-t from-emerald-700 to-emerald-400/80"
                                        : "bg-neutral-800 border border-neutral-700/60"
                                  }`}
                                />
                              </div>

                              {/* Bar count number */}
                              <span
                                className={`text-[10px] font-mono mt-1 transition-colors ${
                                  isHovered ? "text-emerald-300 font-bold" : "text-neutral-400"
                                }`}
                              >
                                {item.count}
                              </span>

                              {/* Day Label */}
                              <span className="text-[11px] font-medium text-neutral-300 mt-0.5">
                                {item.day}
                              </span>
                            </div>
                          )
                        })}
                      </div>
                    )
                  })()
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-neutral-500 text-xs">
                    Belum ada data riwayat prediksi
                  </div>
                )}
              </div>
            </div>

            {/* Kanan (5 Kolom): Data User Aktif */}
            <div className="lg:col-span-5 bg-[#141414] border border-neutral-700/80 rounded-2xl p-6 shadow-xl flex flex-col justify-between">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h2 className="text-base font-semibold text-white tracking-wide">
                    Data User Aktif
                  </h2>
                  <p className="text-xs text-neutral-400 mt-0.5">
                    Pengguna aktif terbaru
                  </p>
                </div>
                <Link
                  to="/users"
                  className="text-xs font-medium text-neutral-400 hover:text-white flex items-center gap-1 transition-colors"
                >
                  <span>Lihat Semua</span>
                  <ChevronRight className="w-3.5 h-3.5" />
                </Link>
              </div>

              {/* List Pengguna Aktif */}
              <div className="divide-y divide-neutral-800/80 flex-1 flex flex-col justify-around">
                {summary?.active_users_list && summary.active_users_list.length > 0 ? (
                  summary.active_users_list.map((u) => (
                    <div key={u.id} className="py-2.5 flex items-center justify-between gap-3">
                      <div className="flex items-center gap-3 min-w-0">
                        <div className="w-8 h-8 rounded-full border border-neutral-700 bg-neutral-800 overflow-hidden flex items-center justify-center shrink-0">
                          {u.avatar ? (
                            <img
                              src={getAssetUrl(u.avatar)}
                              alt={u.full_name}
                              className="w-full h-full object-cover"
                              onError={(e) => {
                                e.currentTarget.style.display = "none"
                              }}
                            />
                          ) : (
                            <span className="text-xs font-bold text-neutral-300">
                              {u.full_name.charAt(0).toUpperCase()}
                            </span>
                          )}
                        </div>
                        <div className="min-w-0">
                          <p className="text-xs font-medium text-white truncate max-w-[140px] sm:max-w-[170px]">
                            {u.full_name}
                          </p>
                          <p className="text-[11px] text-neutral-400 truncate max-w-[140px] sm:max-w-[170px]">
                            {u.email}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2 shrink-0">
                        <span
                          className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${
                            u.role.toLowerCase() === "admin"
                              ? "bg-purple-950/60 text-purple-300 border border-purple-800/50"
                              : "bg-neutral-800 text-neutral-300 border border-neutral-700"
                          }`}
                        >
                          {u.role}
                        </span>
                        <span className="w-2 h-2 rounded-full bg-emerald-400" title="Aktif" />
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="py-8 text-center text-xs text-neutral-500">
                    Tidak ada pengguna aktif ditemukan
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* BARIS 4: Log Aktivitas & Riwayat Prediksi */}
          <div className="w-full grid grid-cols-1 md:grid-cols-2 gap-5">
            {/* Kiri: Log Aktivitas */}
            <div className="bg-[#141414] border border-neutral-700/80 rounded-2xl p-6 shadow-xl flex flex-col justify-between">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h2 className="text-base font-semibold text-white tracking-wide">
                    Log Aktivitas
                  </h2>
                  <p className="text-xs text-neutral-400 mt-0.5">
                    Riwayat tindakan sistem & admin
                  </p>
                </div>
                <Link
                  to="/logs"
                  className="text-xs font-medium text-neutral-400 hover:text-white flex items-center gap-1 transition-colors"
                >
                  <span>Lihat Semua</span>
                  <ChevronRight className="w-3.5 h-3.5" />
                </Link>
              </div>

              {/* List Log Aktivitas */}
              <div className="divide-y divide-neutral-800/80 flex-1 flex flex-col justify-around">
                {summary?.recent_logs && summary.recent_logs.length > 0 ? (
                  summary.recent_logs.map((log) => (
                    <div key={log.id} className="py-2.5 flex items-start justify-between gap-3">
                      <div className="min-w-0 flex-1">
                        <p className="text-xs font-medium text-white truncate max-w-[320px]">
                          {log.action}
                        </p>
                        <p className="text-[11px] text-neutral-400 mt-0.5 truncate">
                          {log.email}
                        </p>
                      </div>
                      <span className="text-[10px] text-neutral-500 font-mono whitespace-nowrap shrink-0">
                        {formatDateTime(log.created_at)}
                      </span>
                    </div>
                  ))
                ) : (
                  <div className="py-8 text-center text-xs text-neutral-500">
                    Belum ada log aktivitas tercatat
                  </div>
                )}
              </div>
            </div>

            {/* Kanan: Riwayat Prediksi */}
            <div className="bg-[#141414] border border-neutral-700/80 rounded-2xl p-6 shadow-xl flex flex-col justify-between">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h2 className="text-base font-semibold text-white tracking-wide">
                    Riwayat Prediksi
                  </h2>
                  <p className="text-xs text-neutral-400 mt-0.5">
                    Deteksi penyakit daun terkini
                  </p>
                </div>
                <Link
                  to="/predictions"
                  className="text-xs font-medium text-neutral-400 hover:text-white flex items-center gap-1 transition-colors"
                >
                  <span>Lihat Semua</span>
                  <ChevronRight className="w-3.5 h-3.5" />
                </Link>
              </div>

              {/* List Riwayat Prediksi */}
              <div className="divide-y divide-neutral-800/80 flex-1 flex flex-col justify-around">
                {summary?.recent_predictions && summary.recent_predictions.length > 0 ? (
                  summary.recent_predictions.map((p) => (
                    <div key={p.id} className="py-2.5 flex items-center justify-between gap-3">
                      <div className="flex items-center gap-3 min-w-0">
                        <div className="w-10 h-10 rounded-lg border border-neutral-700 bg-neutral-900 overflow-hidden shrink-0 flex items-center justify-center">
                          {p.image_path ? (
                            <img
                              src={getAssetUrl(p.image_path)}
                              alt={p.condition}
                              className="w-full h-full object-cover"
                              onError={(e) => {
                                e.currentTarget.style.display = "none"
                              }}
                            />
                          ) : (
                            <ImageIcon className="w-4 h-4 text-neutral-500" />
                          )}
                        </div>
                        <div className="min-w-0">
                          <p className="text-xs font-semibold text-white truncate max-w-[150px] sm:max-w-[180px]">
                            {p.condition}
                          </p>
                          <p className="text-[11px] text-neutral-400 truncate max-w-[150px] sm:max-w-[180px]">
                            {p.email}
                          </p>
                        </div>
                      </div>
                      <div className="text-right shrink-0">
                        <span className="text-xs font-mono font-bold text-emerald-400 block">
                          {formatPercentage(p.confidence)}
                        </span>
                        <span className="text-[10px] text-neutral-500 font-mono block">
                          {formatDateTime(p.created_at)}
                        </span>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="py-8 text-center text-xs text-neutral-500">
                    Belum ada riwayat prediksi tercatat
                  </div>
                )}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
