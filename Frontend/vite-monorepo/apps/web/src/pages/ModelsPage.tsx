import { useEffect, useState, useRef } from "react"
import {
  fetchModels,
  fetchActiveModels,
  setModelActive,
  deactivateModel,
  deleteModel,
  uploadNewModel,
  type ModelItem,
} from "@/api/models"
import { Loader2, Plus, X, Upload, CheckCircle2 } from "lucide-react"

export function ModelsPage() {
  const [models, setModels] = useState<ModelItem[]>([])
  const [activeFilter, setActiveFilter] = useState<ModelItem | null>(null)
  const [activeDisease, setActiveDisease] = useState<ModelItem | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [successMsg, setSuccessMsg] = useState<string | null>(null)

  // Upload Modal state
  const [showUploadModal, setShowUploadModal] = useState(false)
  const [uploadType, setUploadType] = useState("0") // "0" = Filter, "1" = Prediksi
  const [uploadClass, setUploadClass] = useState(2)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [uploadError, setUploadError] = useState<string | null>(null)

  // Confirmation Modal state
  type ConfirmActionType = "activate" | "deactivate" | "delete"
  interface ConfirmModalState {
    isOpen: boolean
    type: ConfirmActionType
    model: ModelItem | null
  }
  const [confirmModal, setConfirmModal] = useState<ConfirmModalState>({
    isOpen: false,
    type: "activate",
    model: null,
  })
  const [isConfirmLoading, setIsConfirmLoading] = useState(false)

  const [actionLoadingId, setActionLoadingId] = useState<number | null>(null)
  const fileInputRef = useRef<HTMLInputElement | null>(null)

  const loadData = async () => {
    try {
      setLoading(true)
      setError(null)
      const [allModels, activeList] = await Promise.all([
        fetchModels(),
        fetchActiveModels(),
      ])
      setModels(allModels)
      setActiveFilter(activeList[0] || null)
      setActiveDisease(activeList[1] || null)
    } catch (err: any) {
      console.error("Gagal memuat data model:", err)
      setError(err.response?.data?.detail || "Gagal memuat data model dari server")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  const openConfirmModal = (type: ConfirmActionType, model: ModelItem) => {
    setConfirmModal({
      isOpen: true,
      type,
      model,
    })
  }

  const getConfirmMessage = (type: ConfirmActionType) => {
    switch (type) {
      case "deactivate":
        return "Apakah anda yakin untuk menon-aktifkan model ini?"
      case "activate":
        return "Apakah anda yakin untuk mengaktifkan model ini?"
      case "delete":
        return "Apakah anda yakin untuk menghapus model ini?"
    }
  }

  const handleConfirmAction = async () => {
    if (!confirmModal.model) return
    const { type, model } = confirmModal

    try {
      setIsConfirmLoading(true)
      setActionLoadingId(model.id)
      setError(null)

      if (type === "activate") {
        await setModelActive(model.id)
        setSuccessMsg(`Berhasil mengaktifkan model "${model.models_name}"`)
      } else if (type === "deactivate") {
        await deactivateModel(model.id)
        setSuccessMsg(`Berhasil menonaktifkan model "${model.models_name}"`)
      } else if (type === "delete") {
        await deleteModel(model.id)
        setSuccessMsg(`Berhasil menghapus model "${model.models_name}"`)
      }

      setConfirmModal({ isOpen: false, type: "activate", model: null })
      setTimeout(() => setSuccessMsg(null), 4000)
      await loadData()
    } catch (err: any) {
      console.error(`Gagal ${type} model:`, err)
      setError(err.response?.data?.detail || "Gagal memproses aksi pada model")
      setConfirmModal({ isOpen: false, type: "activate", model: null })
    } finally {
      setIsConfirmLoading(false)
      setActionLoadingId(null)
    }
  }

  const handleUploadSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedFile) {
      setUploadError("Pilih file model (.keras atau .h5) terlebih dahulu")
      return
    }

    try {
      setUploading(true)
      setUploadError(null)

      await uploadNewModel({
        model_type: uploadType,
        class_model: uploadClass,
        file: selectedFile,
      })

      setSuccessMsg(`Model "${selectedFile.name}" berhasil diunggah`)
      setTimeout(() => setSuccessMsg(null), 4000)
      setShowUploadModal(false)
      setSelectedFile(null)
      loadData()
    } catch (err: any) {
      console.error("Gagal mengunggah model:", err)
      setUploadError(err.response?.data?.detail || "Gagal mengunggah file model")
    } finally {
      setUploading(false)
    }
  }

  // Helper formatting for model type column
  const formatModelType = (type: string) => {
    if (type === "0" || type.toLowerCase() === "false" || type.toLowerCase() === "filter") {
      return "Filter"
    }
    return "Prediksi"
  }

  return (
    <div className="flex flex-col items-center w-full">
      {/* Title */}
      <h1 className="text-3xl font-bold text-white mb-8 tracking-wide">
        Model Deep Learning
      </h1>

      {error && (
        <div className="w-full max-w-5xl mb-4 p-3 rounded-lg bg-red-500/20 border border-red-500/40 text-red-200 text-sm text-center">
          {error}
        </div>
      )}

      {successMsg && (
        <div className="w-full max-w-5xl mb-4 p-3 rounded-lg bg-emerald-500/20 border border-emerald-500/40 text-emerald-200 text-sm text-center">
          {successMsg}
        </div>
      )}

      {/* Top 2 Active Model Banners */}
      <div className="w-full max-w-5xl grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        {/* Model Filter Aktif */}
        <div className="bg-[#141414] border border-neutral-600/80 rounded-2xl py-4 px-6 text-center text-white shadow-xl flex flex-col items-center justify-center">
          <span className="text-sm font-semibold tracking-wide text-neutral-200">
            Model filter aktif
          </span>
          <span className="text-xs font-mono mt-1 text-emerald-400">
            {activeFilter ? activeFilter.models_name : "Belum ada model filter aktif"}
          </span>
        </div>

        {/* Model Prediksi Aktif */}
        <div className="bg-[#141414] border border-neutral-600/80 rounded-2xl py-4 px-6 text-center text-white shadow-xl flex flex-col items-center justify-center">
          <span className="text-sm font-semibold tracking-wide text-neutral-200">
            Model prediksi aktif
          </span>
          <span className="text-xs font-mono mt-1 text-emerald-400">
            {activeDisease ? activeDisease.models_name : "Belum ada model prediksi aktif"}
          </span>
        </div>
      </div>

      {/* Button Tambah Model */}
      <div className="w-full max-w-5xl mb-4 flex justify-start">
        <button
          type="button"
          onClick={() => {
            setShowUploadModal(true)
            setUploadError(null)
          }}
          className="px-5 py-2.5 rounded-xl bg-[#141414] border border-neutral-500/80 text-white text-xs font-medium hover:bg-neutral-800 hover:border-white transition-all cursor-pointer shadow-xs active:scale-95 flex items-center gap-2"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>Tambah Model</span>
        </button>
      </div>

      {/* Table Section */}
      <div className="w-full max-w-5xl bg-[#141414] border border-neutral-600/80 rounded-xl shadow-2xl overflow-hidden">
        {/* Header Bar "Daftar Model" */}
        <div className="bg-[#181818] border-b border-neutral-700/80 py-3 text-center text-sm font-semibold text-white tracking-wide">
          Daftar Model
        </div>

        {loading ? (
          <div className="flex flex-col items-center justify-center py-16 text-neutral-400">
            <Loader2 className="w-8 h-8 animate-spin mb-3 text-neutral-300" />
            <p className="text-sm">Memuat daftar model deep learning...</p>
          </div>
        ) : models.length === 0 ? (
          <div className="text-center py-14 text-neutral-400 text-sm">
            Belum ada model yang diunggah.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-neutral-700 bg-[#161616] text-neutral-300 text-xs sm:text-sm font-semibold">
                  <th className="py-3.5 px-4 text-center border-r border-neutral-700 w-14">
                    No
                  </th>
                  <th className="py-3.5 px-6 border-r border-neutral-700">
                    Nama Model
                  </th>
                  <th className="py-3.5 px-6 border-r border-neutral-700 text-center">
                    Tipe Model
                  </th>
                  <th className="py-3.5 px-6 border-r border-neutral-700 text-center">
                    Status
                  </th>
                  <th className="py-3.5 px-6 text-center w-48">
                    Action
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-neutral-700 text-xs sm:text-sm text-neutral-200">
                {models.map((m, idx) => {
                  const isCurrentActive =
                    m.is_active ||
                    (activeFilter && activeFilter.id === m.id) ||
                    (activeDisease && activeDisease.id === m.id)

                  const isLoadingAction = actionLoadingId === m.id

                  return (
                    <tr
                      key={m.id}
                      className="hover:bg-neutral-900/60 transition-colors"
                    >
                      <td className="py-4 px-4 text-center border-r border-neutral-700 text-neutral-400 font-medium">
                        {idx + 1}
                      </td>
                      <td className="py-4 px-6 border-r border-neutral-700 font-mono text-xs text-white">
                        {m.models_name}
                      </td>
                      <td className="py-4 px-6 border-r border-neutral-700 text-center">
                        {formatModelType(m.model_type)}
                      </td>
                      <td className="py-4 px-6 border-r border-neutral-700 text-center font-medium">
                        <span
                          className={`inline-flex items-center gap-1.5 text-xs px-2.5 py-0.5 rounded-full ${
                            isCurrentActive
                              ? "text-emerald-300 bg-emerald-950/50 border border-emerald-800/60"
                              : "text-neutral-400 bg-neutral-800 border border-neutral-700"
                          }`}
                        >
                          {isCurrentActive ? (
                            <>
                              <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                              Aktif
                            </>
                          ) : (
                            "Non-aktif"
                          )}
                        </span>
                      </td>
                      <td className="py-4 px-6 text-center">
                        <div className="flex items-center justify-center gap-2.5">
                          {/* Action Button: Set / Nonaktifkan */}
                          {isCurrentActive ? (
                            <button
                              type="button"
                              onClick={() => openConfirmModal("deactivate", m)}
                              disabled={isLoadingAction}
                              title="Nonaktifkan model ini"
                              className="px-3.5 py-1.5 rounded-lg bg-[#141414] border border-amber-500/70 text-amber-300 text-xs font-medium hover:bg-amber-950/40 hover:border-amber-400 transition-all cursor-pointer active:scale-95 disabled:opacity-50"
                            >
                              {isLoadingAction ? (
                                <Loader2 className="w-3.5 h-3.5 animate-spin mx-auto" />
                              ) : (
                                "Nonaktifkan"
                              )}
                            </button>
                          ) : (
                            <button
                              type="button"
                              onClick={() => openConfirmModal("activate", m)}
                              disabled={isLoadingAction}
                              className="px-4 py-1.5 rounded-lg text-xs font-medium transition-all shadow-xs bg-[#141414] border border-neutral-500/80 text-white hover:bg-neutral-800 hover:border-white cursor-pointer active:scale-95 disabled:opacity-50"
                            >
                              {isLoadingAction ? (
                                <Loader2 className="w-3.5 h-3.5 animate-spin mx-auto" />
                              ) : (
                                "Set"
                              )}
                            </button>
                          )}

                          {/* Delete Button (Only available if non-active) */}
                          {!isCurrentActive && (
                            <button
                              type="button"
                              onClick={() => openConfirmModal("delete", m)}
                              disabled={isLoadingAction}
                              className="px-3.5 py-1.5 rounded-lg bg-[#141414] border border-red-500/70 text-red-300 text-xs font-medium hover:bg-red-950 hover:border-red-400 transition-all cursor-pointer active:scale-95 disabled:opacity-50"
                            >
                              Delete
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Upload Model Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-xs p-4 animate-in fade-in duration-150">
          <div className="bg-[#141414] border border-neutral-600 rounded-[2.2rem] p-7 sm:p-8 max-w-md w-full text-white shadow-2xl relative">
            <button
              type="button"
              onClick={() => setShowUploadModal(false)}
              className="absolute top-5 right-5 p-1.5 rounded-lg text-neutral-400 hover:text-white hover:bg-neutral-800 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>

            <h2 className="text-xl font-bold mb-5 border-b border-neutral-700 pb-3">
              Upload Model Baru
            </h2>

            {uploadError && (
              <div className="mb-4 p-2.5 rounded-lg bg-red-500/20 border border-red-500/40 text-red-200 text-xs text-center">
                {uploadError}
              </div>
            )}

            <form onSubmit={handleUploadSubmit} className="space-y-4">
              {/* File Drop / Select Area */}
              <div>
                <label className="block text-xs font-medium text-neutral-300 mb-2">
                  File Model (.keras atau .h5)
                </label>
                <input
                  type="file"
                  ref={fileInputRef}
                  accept=".keras,.h5"
                  onChange={(e) => {
                    if (e.target.files && e.target.files[0]) {
                      setSelectedFile(e.target.files[0])
                    }
                  }}
                  className="hidden"
                />
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  className="w-full py-6 border-2 border-dashed border-neutral-600 hover:border-white rounded-xl flex flex-col items-center justify-center bg-[#181818] transition-colors cursor-pointer"
                >
                  <Upload className="w-7 h-7 text-neutral-400 mb-2" />
                  <span className="text-xs text-neutral-200 font-medium font-mono truncate max-w-[280px]">
                    {selectedFile ? selectedFile.name : "Klik untuk memilih file model"}
                  </span>
                  <span className="text-[10px] text-neutral-500 mt-1">
                    Format: .keras / .h5
                  </span>
                </button>
              </div>

              {/* Tipe Model */}
              <div>
                <label className="block text-xs font-medium text-neutral-300 mb-2">
                  Tipe Model
                </label>
                <select
                  value={uploadType}
                  onChange={(e) => {
                    const val = e.target.value
                    setUploadType(val)
                    setUploadClass(val === "0" ? 2 : 4)
                  }}
                  className="w-full px-3.5 py-2.5 rounded-lg bg-[#181818] border border-neutral-700 text-white text-xs focus:outline-none focus:border-white transition-colors"
                >
                  <option value="0">Model Filter (Random vs Banana)</option>
                  <option value="1">Model Prediksi (4 Penyakit Daun)</option>
                </select>
              </div>

              {/* Jumlah Kelas */}
              <div>
                <label className="block text-xs font-medium text-neutral-300 mb-2">
                  Jumlah Kelas (Output Class)
                </label>
                <input
                  type="number"
                  value={uploadClass}
                  onChange={(e) => setUploadClass(parseInt(e.target.value, 10) || 1)}
                  min={1}
                  required
                  className="w-full px-3.5 py-2 rounded-lg bg-[#181818] border border-neutral-700 text-white text-xs focus:outline-none focus:border-white transition-colors"
                />
              </div>

              {/* Actions */}
              <div className="pt-3 flex items-center justify-end gap-3">
                <button
                  type="button"
                  onClick={() => setShowUploadModal(false)}
                  disabled={uploading}
                  className="px-5 py-2 rounded-lg bg-[#222222] border border-neutral-600 text-white text-xs font-medium hover:bg-neutral-800 transition-colors cursor-pointer disabled:opacity-50"
                >
                  Batal
                </button>
                <button
                  type="submit"
                  disabled={uploading}
                  className="px-6 py-2 rounded-lg bg-white text-neutral-900 font-semibold text-xs hover:bg-neutral-200 transition-colors cursor-pointer disabled:opacity-50 flex items-center gap-2"
                >
                  {uploading && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
                  <span>{uploading ? "Mengunggah..." : "Upload Model"}</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Confirmation Action Modal (Aktifkan / Menon-aktifkan / Menghapus) */}
      {confirmModal.isOpen && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-xs p-4 animate-in fade-in duration-150"
          onClick={() => {
            if (!isConfirmLoading) {
              setConfirmModal({ isOpen: false, type: "activate", model: null })
            }
          }}
        >
          <div
            className="bg-[#121212] border border-white/60 rounded-2xl pt-7 pb-6 px-8 max-w-sm w-full text-center shadow-2xl animate-in zoom-in-95 duration-150"
            onClick={(e) => e.stopPropagation()}
          >
            <p className="text-white text-xs sm:text-sm font-medium text-center mb-6 leading-relaxed">
              {getConfirmMessage(confirmModal.type)}
            </p>

            <div className="flex items-center justify-center gap-4">
              <button
                type="button"
                onClick={handleConfirmAction}
                disabled={isConfirmLoading}
                className="w-28 py-2 rounded-xl bg-transparent border border-white/80 hover:border-white hover:bg-white/10 text-white text-xs sm:text-sm font-medium transition-all text-center cursor-pointer active:scale-95 disabled:opacity-50 flex items-center justify-center gap-1.5"
              >
                {isConfirmLoading && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
                <span>Yakin</span>
              </button>

              <button
                type="button"
                onClick={() => setConfirmModal({ isOpen: false, type: "activate", model: null })}
                disabled={isConfirmLoading}
                className="w-28 py-2 rounded-xl bg-transparent border border-white/80 hover:border-white hover:bg-white/10 text-white text-xs sm:text-sm font-medium transition-all text-center cursor-pointer active:scale-95 disabled:opacity-50"
              >
                Batalkan
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
