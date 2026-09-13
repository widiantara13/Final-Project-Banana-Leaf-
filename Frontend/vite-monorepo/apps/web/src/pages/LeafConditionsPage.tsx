import { useEffect, useState, useRef } from "react"
import {
  fetchLeafConditions,
  updateLeafCondition,
  type LeafConditionItem,
} from "@/api/leaves"
import { getAssetUrl } from "@/api/client"
import { Loader2, X, Upload } from "lucide-react"

export function LeafConditionsPage() {
  const [conditions, setConditions] = useState<LeafConditionItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [successMsg, setSuccessMsg] = useState<string | null>(null)

  // Edit Modal State
  const [editingItem, setEditingItem] = useState<LeafConditionItem | null>(null)
  const [editName, setEditName] = useState("")
  const [editDesc, setEditDesc] = useState("")
  const [editTreatment, setEditTreatment] = useState("")
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [filePreview, setFilePreview] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const [editError, setEditError] = useState<string | null>(null)

  const fileInputRef = useRef<HTMLInputElement | null>(null)

  const loadConditions = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await fetchLeafConditions()
      setConditions(data)
    } catch (err: any) {
      console.error("Gagal memuat kondisi daun:", err)
      setError(err.response?.data?.detail || "Gagal memuat data kondisi daun dari server")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadConditions()
  }, [])

  const handleOpenEdit = (item: LeafConditionItem) => {
    setEditingItem(item)
    setEditName(item.condition)
    setEditDesc(item.description)
    setEditTreatment(item.treatment)
    setSelectedFile(null)
    setFilePreview(null)
    setEditError(null)
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0]
      setSelectedFile(file)
      setFilePreview(URL.createObjectURL(file))
    }
  }

  const handleSaveEdit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!editingItem) return

    try {
      setSubmitting(true)
      setEditError(null)

      await updateLeafCondition(editingItem.id, {
        condition: editName,
        description: editDesc,
        treatment: editTreatment,
        file: selectedFile,
      })

      setSuccessMsg(`Berhasil memperbarui data kondisi "${editName}"`)
      setTimeout(() => setSuccessMsg(null), 4000)

      setEditingItem(null)
      loadConditions()
    } catch (err: any) {
      console.error("Gagal memperbarui kondisi daun:", err)
      setEditError(err.response?.data?.detail || "Gagal memperbarui data kondisi daun")
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="flex flex-col items-center w-full">
      {/* Title */}
      <h1 className="text-3xl font-bold text-white mb-8 tracking-wide">
        Kondisi Daun
      </h1>

      {error && (
        <div className="w-full max-w-6xl mb-6 p-3 rounded-lg bg-red-500/20 border border-red-500/40 text-red-200 text-sm text-center">
          {error}
        </div>
      )}

      {successMsg && (
        <div className="w-full max-w-6xl mb-6 p-3 rounded-lg bg-emerald-500/20 border border-emerald-500/40 text-emerald-200 text-sm text-center">
          {successMsg}
        </div>
      )}

      {loading ? (
        <div className="flex flex-col items-center justify-center py-20 text-neutral-400">
          <Loader2 className="w-8 h-8 animate-spin mb-3 text-neutral-300" />
          <p className="text-sm">Memuat data kondisi daun...</p>
        </div>
      ) : conditions.length === 0 ? (
        <div className="text-center py-14 text-neutral-400 text-sm">
          Tidak ada data kondisi daun yang ditemukan.
        </div>
      ) : (
        /* 4 Cards Grid Layout */
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 w-full max-w-6xl">
          {conditions.map((item) => (
            <div
              key={item.id}
              className="bg-[#141414] border border-neutral-700/80 rounded-[2rem] p-6 text-white flex flex-col justify-between shadow-2xl min-h-[540px] hover:border-neutral-500/80 transition-all"
            >
              <div>
                {/* Top Gambar Reference */}
                <div className="flex justify-center mb-4">
                  <div className="w-28 h-18 rounded-xl border border-white/80 overflow-hidden bg-neutral-900 flex items-center justify-center shadow-xs">
                    {item.image_reference ? (
                      <img
                        src={getAssetUrl(item.image_reference)}
                        alt={item.condition}
                        className="w-full h-full object-cover"
                        onError={(e) => {
                          ;(e.target as HTMLElement).style.display = "none"
                        }}
                      />
                    ) : (
                      <span className="text-xs font-medium text-white">Gambar</span>
                    )}
                  </div>
                </div>

                {/* Condition Name */}
                <h2 className="text-lg font-bold text-center text-white mb-6">
                  {item.condition}
                </h2>

                {/* Box Deskripsi */}
                <div className="border border-neutral-600/90 rounded-xl p-4 mb-4 bg-[#181818] min-h-[120px] flex flex-col">
                  <h3 className="font-bold text-sm text-white mb-2">Deskripsi</h3>
                  <p className="text-xs text-neutral-300 leading-relaxed line-clamp-4 overflow-y-auto">
                    {item.description || "-"}
                  </p>
                </div>

                {/* Box Treatment */}
                <div className="border border-neutral-600/90 rounded-xl p-4 mb-6 bg-[#181818] min-h-[120px] flex flex-col">
                  <h3 className="font-bold text-sm text-white mb-2">Treatment</h3>
                  <p className="text-xs text-neutral-300 leading-relaxed line-clamp-4 overflow-y-auto">
                    {item.treatment || "-"}
                  </p>
                </div>
              </div>

              {/* Edit Button */}
              <div className="flex justify-center pt-2">
                <button
                  type="button"
                  onClick={() => handleOpenEdit(item)}
                  className="px-8 py-2 rounded-lg bg-[#202020] border border-neutral-500/90 text-white text-xs font-medium hover:bg-neutral-800 hover:border-white transition-all cursor-pointer active:scale-95 shadow-xs"
                >
                  Edit
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Edit Modal Pop-up */}
      {editingItem && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-xs p-4 animate-in fade-in duration-150">
          <div className="bg-[#141414] border border-neutral-600 rounded-[2.2rem] p-7 sm:p-8 max-w-md w-full text-white shadow-2xl relative">
            {/* Close Button */}
            <button
              type="button"
              onClick={() => setEditingItem(null)}
              className="absolute top-5 right-5 p-1.5 rounded-lg text-neutral-400 hover:text-white hover:bg-neutral-800 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>

            {editError && (
              <div className="mb-4 p-2.5 rounded-lg bg-red-500/20 border border-red-500/40 text-red-200 text-xs text-center">
                {editError}
              </div>
            )}

            <form onSubmit={handleSaveEdit} className="space-y-4">
              {/* Gambar yang diperbaharui */}
              <div className="flex flex-col items-center justify-center mb-2">
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleFileChange}
                  accept="image/*"
                  className="hidden"
                />
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  className="w-40 h-32 rounded-xl border border-white/80 overflow-hidden bg-neutral-900 flex flex-col items-center justify-center text-center p-2 hover:border-white hover:bg-neutral-800/80 transition-all cursor-pointer relative group"
                  title="Klik untuk memilih gambar baru"
                >
                  {filePreview ? (
                    <img
                      src={filePreview}
                      alt="Preview Baru"
                      className="w-full h-full object-cover"
                    />
                  ) : editingItem.image_reference ? (
                    <img
                      src={getAssetUrl(editingItem.image_reference)}
                      alt={editingItem.condition}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="flex flex-col items-center text-neutral-300">
                      <Upload className="w-6 h-6 mb-1 text-neutral-400" />
                      <span className="text-xs font-medium leading-tight">
                        Gambar yang diperbaharui
                      </span>
                    </div>
                  )}
                  <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 flex items-center justify-center transition-opacity text-xs font-medium text-white">
                    Ganti Foto
                  </div>
                </button>
              </div>

              {/* Nama Kondisi */}
              <div className="text-center">
                <input
                  type="text"
                  value={editName}
                  onChange={(e) => setEditName(e.target.value)}
                  placeholder="Nama Kondisi"
                  required
                  className="w-full text-center font-bold text-lg bg-transparent border-b border-neutral-700 pb-1 text-white focus:outline-none focus:border-white transition-colors"
                />
              </div>

              {/* Box Deskripsi */}
              <div className="border border-neutral-600/90 rounded-xl p-4 bg-[#181818]">
                <h3 className="font-bold text-sm text-white mb-2">Deskripsi</h3>
                <textarea
                  value={editDesc}
                  onChange={(e) => setEditDesc(e.target.value)}
                  placeholder="Deskripsi baru yang akan dibuat atau diperbaharui disini."
                  required
                  rows={4}
                  className="w-full bg-transparent text-xs text-neutral-200 resize-none focus:outline-none leading-relaxed placeholder:text-neutral-500"
                />
              </div>

              {/* Box Treatment */}
              <div className="border border-neutral-600/90 rounded-xl p-4 bg-[#181818]">
                <h3 className="font-bold text-sm text-white mb-2">Treatment</h3>
                <textarea
                  value={editTreatment}
                  onChange={(e) => setEditTreatment(e.target.value)}
                  placeholder="Mengedit perlakuan atau treatmen yang perlu dilakukan pada kondisi daun tertentu"
                  required
                  rows={4}
                  className="w-full bg-transparent text-xs text-neutral-200 resize-none focus:outline-none leading-relaxed placeholder:text-neutral-500"
                />
              </div>

              {/* Modal Buttons */}
              <div className="pt-2 flex items-center justify-end gap-3">
                <button
                  type="button"
                  onClick={() => setEditingItem(null)}
                  disabled={submitting}
                  className="px-5 py-2 rounded-lg bg-[#222222] border border-neutral-600 text-white text-xs font-medium hover:bg-neutral-800 transition-colors cursor-pointer disabled:opacity-50"
                >
                  Batal
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-6 py-2 rounded-lg bg-white text-neutral-900 font-semibold text-xs hover:bg-neutral-200 transition-colors cursor-pointer disabled:opacity-50 flex items-center gap-2"
                >
                  {submitting && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
                  <span>{submitting ? "Menyimpan..." : "Simpan"}</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
