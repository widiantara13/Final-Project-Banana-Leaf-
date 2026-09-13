import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import { fetchUsers, type UserItem } from "@/api/users"
import { Loader2 } from "lucide-react"

export function UsersPage() {
  const navigate = useNavigate()
  const [users, setUsers] = useState<UserItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Pagination state
  const [currentPage, setCurrentPage] = useState(1)
  const [pageSize] = useState(7) // 7 rows matching the wireframe
  const [totalItems, setTotalItems] = useState(0)

  const totalPages = Math.max(1, Math.ceil(totalItems / pageSize))

  const loadUsers = async (page: number) => {
    try {
      setLoading(true)
      setError(null)
      const data = await fetchUsers(page, pageSize)
      setUsers(data.items || [])
      setTotalItems(data.total || 0)
    } catch (err: any) {
      console.error("Gagal memuat data users:", err)
      setError(err.response?.data?.detail || "Gagal memuat data users dari server")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadUsers(currentPage)
  }, [currentPage])

  const formatDate = (dateString?: string) => {
    if (!dateString) return "-"
    return dateString.split("T")[0]
  }

  return (
    <div className="flex flex-col items-center w-full">
      {/* Title */}
      <h1 className="text-3xl font-bold text-white mb-8 tracking-wide">User</h1>

      {error && (
        <div className="w-full max-w-4xl mb-4 p-3 rounded-lg bg-red-500/20 border border-red-500/40 text-red-200 text-sm text-center">
          {error}
        </div>
      )}

      {/* Main Table Card */}
      <div className="w-full max-w-4xl bg-[#141414] border border-neutral-600/80 rounded-xl p-6 sm:p-8 shadow-2xl overflow-x-auto">
        {loading ? (
          <div className="flex flex-col items-center justify-center py-16 text-neutral-400">
            <Loader2 className="w-8 h-8 animate-spin mb-3 text-neutral-300" />
            <p className="text-sm">Memuat daftar users...</p>
          </div>
        ) : users.length === 0 ? (
          <div className="text-center py-14 text-neutral-400 text-sm">
            Tidak ada data pengguna yang ditemukan.
          </div>
        ) : (
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-neutral-800 text-neutral-200 text-sm font-semibold">
                <th className="py-3 px-3 text-center w-12">No</th>
                <th className="py-3 px-4">email</th>
                <th className="py-3 px-4 text-center">status</th>
                <th className="py-3 px-4 text-center">role</th>
                <th className="py-3 px-4 text-center">created</th>
                <th className="py-3 px-4 text-center">updated</th>
                <th className="py-3 px-4 text-center">action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-800/80 text-sm">
              {users.map((u, idx) => {
                const rowNumber = (currentPage - 1) * pageSize + idx + 1
                return (
                  <tr
                    key={u.id}
                    className="hover:bg-neutral-900/50 transition-colors text-neutral-200"
                  >
                    <td className="py-3.5 px-3 text-center text-neutral-400 font-medium">
                      {rowNumber}
                    </td>
                    <td className="py-3.5 px-4 font-mono text-xs sm:text-sm text-neutral-300">
                      {u.email}
                    </td>
                    <td className="py-3.5 px-4 text-center">
                      <span
                        className={`text-xs px-2.5 py-0.5 rounded-full ${
                          u.is_active
                            ? "text-emerald-300 bg-emerald-950/50 border border-emerald-800/50"
                            : "text-neutral-400 bg-neutral-800 border border-neutral-700"
                        }`}
                      >
                        {u.is_active ? "aktif" : "non-aktif"}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-center font-medium capitalize text-neutral-300">
                      {u.role}
                    </td>
                    <td className="py-3.5 px-4 text-center text-neutral-400 text-xs">
                      {formatDate(u.created_at)}
                    </td>
                    <td className="py-3.5 px-4 text-center text-neutral-400 text-xs">
                      {formatDate(u.updated_at)}
                    </td>
                    <td className="py-3.5 px-4 text-center">
                      <button
                        type="button"
                        onClick={() => navigate(`/profile/${u.id}`)}
                        className="px-3.5 py-1.5 rounded-lg bg-[#202020] border border-neutral-500/80 text-white text-xs font-medium hover:bg-neutral-800 hover:border-white transition-all cursor-pointer shadow-xs active:scale-95"
                      >
                        Show Profile
                      </button>
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
