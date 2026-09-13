import { useEffect, useState } from "react"
import { fetchPredictions, type PredictionItem } from "@/api/predictions"
import { getAssetUrl } from "@/api/client"
import { Loader2, Image as ImageIcon, X } from "lucide-react"

export function PredictionsPage() {
  const [predictions, setPredictions] = useState<PredictionItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Filter & Pagination state
  const [emailFilter, setEmailFilter] = useState("")
  const [currentPage, setCurrentPage] = useState(1)
  const [pageSize] = useState(7) // 7 rows matching the wireframe
  const [totalItems, setTotalItems] = useState(0)

  // Image preview modal state
  const [previewImage, setPreviewImage] = useState<string | null>(null)

  const totalPages = Math.max(1, Math.ceil(totalItems / pageSize))

  const loadPredictions = async (page: number, email?: string) => {
    try {
      setLoading(true)
      setError(null)
      const data = await fetchPredictions(page, pageSize, email)
      setPredictions(data.items || [])
      setTotalItems(data.total || 0)
    } catch (err: any) {
      console.error("Gagal memuat riwayat prediksi:", err)
      setError(err.response?.data?.detail || "Gagal memuat riwayat prediksi dari server")
    } finally {
      setLoading(false)
    }
  }

  // Reload when page or emailFilter changes with debounce
  useEffect(() => {
    const handler = setTimeout(() => {
      loadPredictions(currentPage, emailFilter)
    }, 300)

    return () => clearTimeout(handler)
  }, [currentPage, emailFilter])

  const formatDateTime = (dateString?: string) => {
    if (!dateString) return "-"
    return dateString.replace("T", " ").split(".")[0]
  }

  const formatPercentage = (val: number) => {
    if (val === null || val === undefined) return "-"
    // If integer, e.g. 100%, show 100%, else 2 decimal places
    return val % 1 === 0 ? `${val}%` : `${val.toFixed(2)}%`
  }

  return (
    <div className="flex flex-col items-center w-full">
      {/* Title */}
      <h1 className="text-3xl font-bold text-white mb-8 tracking-wide">
        Riwayat Prediksi
      </h1>

      {error && (
        <div className="w-full max-w-5xl mb-4 p-3 rounded-lg bg-red-500/20 border border-red-500/40 text-red-200 text-sm text-center">
          {error}
        </div>
      )}

      {/* Top Filter Container (Email Filter) */}
      <div className="w-full max-w-5xl mb-4 flex items-center justify-start">
        <input
          type="text"
          value={emailFilter}
          onChange={(e) => {
            setEmailFilter(e.target.value)
            setCurrentPage(1) // Reset to page 1 on search
          }}
          placeholder="Email"
          className="w-44 px-4 py-2 bg-[#141414] border border-neutral-500/80 rounded-xl text-white placeholder:text-neutral-300 text-sm focus:outline-none focus:border-white transition-colors"
        />
      </div>

      {/* Main Table Card */}
      <div className="w-full max-w-5xl bg-[#141414] border border-neutral-600/80 rounded-xl shadow-2xl overflow-x-auto">
        {loading ? (
          <div className="flex flex-col items-center justify-center py-16 text-neutral-400">
            <Loader2 className="w-8 h-8 animate-spin mb-3 text-neutral-300" />
            <p className="text-sm">Memuat data riwayat prediksi...</p>
          </div>
        ) : predictions.length === 0 ? (
          <div className="text-center py-14 text-neutral-400 text-sm">
            Tidak ada riwayat prediksi yang ditemukan.
          </div>
        ) : (
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-neutral-700 bg-[#161616] text-neutral-200 text-sm font-semibold">
                <th className="py-3.5 px-3 text-center border-r border-neutral-700 w-12">
                  No
                </th>
                <th className="py-3.5 px-4 border-r border-neutral-700 text-center w-24">
                  Gambar
                </th>
                <th className="py-3.5 px-4 border-r border-neutral-700 text-center">
                  Prediksi
                </th>
                <th className="py-3.5 px-4 border-r border-neutral-700 text-center">
                  Presentase
                </th>
                <th className="py-3.5 px-4 border-r border-neutral-700 text-center">
                  email
                </th>
                <th className="py-3.5 px-4 text-center">created</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-700 text-xs sm:text-sm text-neutral-200">
              {predictions.map((p, idx) => {
                const rowNumber = (currentPage - 1) * pageSize + idx + 1
                return (
                  <tr
                    key={p.id}
                    className="hover:bg-neutral-900/60 transition-colors"
                  >
                    <td className="py-3.5 px-3 text-center border-r border-neutral-700 text-neutral-400 font-medium">
                      {rowNumber}
                    </td>
                    <td className="py-2.5 px-3 border-r border-neutral-700 text-center">
                      <div className="flex justify-center">
                        {p.image_path ? (
                          <button
                            type="button"
                            onClick={() =>
                              setPreviewImage(getAssetUrl(p.image_path))
                            }
                            className="w-14 h-9 rounded-md border border-neutral-600 bg-neutral-900 overflow-hidden flex items-center justify-center hover:scale-105 transition-transform cursor-pointer relative"
                            title="Klik untuk memperbesar gambar"
                          >
                            <img
                              src={getAssetUrl(p.image_path)}
                              alt={p.condition}
                              className="w-full h-full object-cover"
                              onError={(e) => {
                                const target = e.currentTarget
                                target.style.display = "none"
                                const parent = target.parentElement
                                if (parent && !parent.querySelector(".fallback-icon")) {
                                  const fallback = document.createElement("div")
                                  fallback.className =
                                    "fallback-icon text-[10px] text-neutral-400 flex items-center justify-center w-full h-full"
                                  fallback.innerText = "No Img"
                                  parent.appendChild(fallback)
                                }
                              }}
                            />
                          </button>
                        ) : (
                          <div className="w-14 h-9 rounded-md border border-neutral-700 bg-neutral-800 flex items-center justify-center text-neutral-500">
                            <ImageIcon className="w-4 h-4" />
                          </div>
                        )}
                      </div>
                    </td>
                    <td className="py-3.5 px-4 border-r border-neutral-700 text-center font-medium">
                      {p.condition}
                    </td>
                    <td className="py-3.5 px-4 border-r border-neutral-700 text-center font-mono text-neutral-300">
                      {formatPercentage(p.confidence)}
                    </td>
                    <td className="py-3.5 px-4 border-r border-neutral-700 text-center font-mono text-xs text-neutral-300">
                      {p.email}
                    </td>
                    <td className="py-3.5 px-4 text-center font-mono text-xs text-neutral-400 whitespace-nowrap">
                      {formatDateTime(p.created_at)}
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

      {/* Image Zoom Modal */}
      {previewImage && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-xs p-4 animate-in fade-in"
          onClick={() => setPreviewImage(null)}
        >
          <div
            className="relative max-w-xl max-h-[85vh] p-2 bg-[#181818] border border-neutral-700 rounded-2xl shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            <button
              type="button"
              onClick={() => setPreviewImage(null)}
              className="absolute -top-3 -right-3 p-1.5 rounded-full bg-[#222] border border-neutral-600 text-neutral-300 hover:text-white transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
            <img
              src={previewImage}
              alt="Preview Daun"
              className="max-h-[75vh] w-auto rounded-xl object-contain"
            />
          </div>
        </div>
      )}
    </div>
  )
}
