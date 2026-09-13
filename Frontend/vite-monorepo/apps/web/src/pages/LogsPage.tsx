import { useEffect, useState } from "react"
import { fetchLogs, type LogItem } from "@/api/logs"
import { Loader2 } from "lucide-react"

export function LogsPage() {
  const [logs, setLogs] = useState<LogItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Filter & Pagination state
  const [emailFilter, setEmailFilter] = useState("")
  const [currentPage, setCurrentPage] = useState(1)
  const [pageSize] = useState(7) // 7 rows matching the wireframe
  const [totalItems, setTotalItems] = useState(0)

  const totalPages = Math.max(1, Math.ceil(totalItems / pageSize))

  const loadLogs = async (page: number, email?: string) => {
    try {
      setLoading(true)
      setError(null)
      const data = await fetchLogs(page, pageSize, email)
      setLogs(data.items || [])
      setTotalItems(data.total || 0)
    } catch (err: any) {
      console.error("Gagal memuat log aktivitas:", err)
      setError(err.response?.data?.detail || "Gagal memuat data log dari server")
    } finally {
      setLoading(false)
    }
  }

  // Reload when page or emailFilter changes
  useEffect(() => {
    const handler = setTimeout(() => {
      loadLogs(currentPage, emailFilter)
    }, 300) // Debounce 300ms for search

    return () => clearTimeout(handler)
  }, [currentPage, emailFilter])

  const formatDateTime = (dateString?: string) => {
    if (!dateString) return "-"
    // Replace T with space and strip milliseconds if any
    return dateString.replace("T", " ").split(".")[0]
  }

  return (
    <div className="flex flex-col items-center w-full">
      {/* Title */}
      <h1 className="text-3xl font-bold text-white mb-8 tracking-wide">
        Log Aktivitas
      </h1>

      {error && (
        <div className="w-full max-w-5xl mb-4 p-3 rounded-lg bg-red-500/20 border border-red-500/40 text-red-200 text-sm text-center">
          {error}
        </div>
      )}

      {/* Top Filter Container (Email Filter) */}
      <div className="w-full max-w-5xl mb-4 flex items-center justify-start">
        <div className="relative">
          <input
            type="text"
            value={emailFilter}
            onChange={(e) => {
              setEmailFilter(e.target.value)
              setCurrentPage(1) // Reset to page 1 on filter
            }}
            placeholder="Email"
            className="w-44 px-4 py-2 bg-[#141414] border border-neutral-500/80 rounded-xl text-white placeholder:text-neutral-300 text-sm focus:outline-none focus:border-white transition-colors"
          />
        </div>
      </div>

      {/* Main Table Card */}
      <div className="w-full max-w-5xl bg-[#141414] border border-neutral-600/80 rounded-xl shadow-2xl overflow-x-auto">
        {loading ? (
          <div className="flex flex-col items-center justify-center py-16 text-neutral-400">
            <Loader2 className="w-8 h-8 animate-spin mb-3 text-neutral-300" />
            <p className="text-sm">Memuat log aktivitas...</p>
          </div>
        ) : logs.length === 0 ? (
          <div className="text-center py-14 text-neutral-400 text-sm">
            Tidak ada riwayat aktivitas yang ditemukan.
          </div>
        ) : (
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-neutral-700 bg-[#161616] text-neutral-200 text-sm font-semibold">
                <th className="py-3.5 px-3 text-center border-r border-neutral-700 w-12">
                  No
                </th>
                <th className="py-3.5 px-4 border-r border-neutral-700 text-center">
                  action
                </th>
                <th className="py-3.5 px-4 border-r border-neutral-700 text-center">
                  module
                </th>
                <th className="py-3.5 px-4 border-r border-neutral-700 text-center">
                  email
                </th>
                <th className="py-3.5 px-3 border-r border-neutral-700 text-center">
                  ip
                </th>
                <th className="py-3.5 px-4 border-r border-neutral-700 text-center">
                  browser
                </th>
                <th className="py-3.5 px-4 text-center">created</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-700 text-xs sm:text-sm text-neutral-200">
              {logs.map((log, idx) => {
                const rowNumber = (currentPage - 1) * pageSize + idx + 1
                return (
                  <tr
                    key={log.id}
                    className="hover:bg-neutral-900/60 transition-colors"
                  >
                    <td className="py-3.5 px-3 text-center border-r border-neutral-700 text-neutral-400 font-medium">
                      {rowNumber}
                    </td>
                    <td className="py-3.5 px-4 border-r border-neutral-700 text-center font-medium">
                      {log.action}
                    </td>
                    <td className="py-3.5 px-4 border-r border-neutral-700 text-center text-neutral-300">
                      {log.module}
                    </td>
                    <td className="py-3.5 px-4 border-r border-neutral-700 text-center font-mono text-xs text-neutral-300">
                      {log.email || "-"}
                    </td>
                    <td className="py-3.5 px-3 border-r border-neutral-700 text-center font-mono text-xs text-neutral-400">
                      {log.ip || "-"}
                    </td>
                    <td className="py-3.5 px-4 border-r border-neutral-700 text-center text-xs text-neutral-300 max-w-[200px] truncate" title={log.browser || ""}>
                      {log.browser || "-"}
                    </td>
                    <td className="py-3.5 px-4 text-center font-mono text-xs text-neutral-400 whitespace-nowrap">
                      {formatDateTime(log.created_at)}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        )}
      </div>

      {/* Pagination Controls */}
      {!loading && totalPages > 1 && (
        <div className="mt-8 flex items-center justify-center gap-1.5 select-none">
          {/* Previous Page << */}
          <button
            type="button"
            disabled={currentPage <= 1}
            onClick={() => setCurrentPage((prev) => Math.max(1, prev - 1))}
            className="px-3 py-1.5 rounded-md bg-[#222222] border border-neutral-600 text-white text-xs font-medium hover:bg-neutral-800 hover:border-white disabled:opacity-40 disabled:cursor-not-allowed transition-colors cursor-pointer"
          >
            &lt;&lt;
          </button>

          {/* Page Numbers */}
          {Array.from({ length: totalPages }, (_, i) => i + 1).map((pageNum) => (
            <button
              key={pageNum}
              type="button"
              onClick={() => setCurrentPage(pageNum)}
              className={`min-w-8 py-1.5 px-2.5 rounded-md border text-xs font-medium transition-colors cursor-pointer ${
                currentPage === pageNum
                  ? "bg-[#383838] border-white text-white font-bold ring-1 ring-white/30"
                  : "bg-[#222222] border-neutral-600 text-neutral-300 hover:bg-neutral-800 hover:border-white"
              }`}
            >
              {pageNum}
            </button>
          ))}

          {/* Next Page >> */}
          <button
            type="button"
            disabled={currentPage >= totalPages}
            onClick={() => setCurrentPage((prev) => Math.min(totalPages, prev + 1))}
            className="px-3 py-1.5 rounded-md bg-[#222222] border border-neutral-600 text-white text-xs font-medium hover:bg-neutral-800 hover:border-white disabled:opacity-40 disabled:cursor-not-allowed transition-colors cursor-pointer"
          >
            &gt;&gt;
          </button>
        </div>
      )}
    </div>
  )
}
