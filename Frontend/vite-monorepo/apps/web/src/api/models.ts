import { apiClient } from "./client"

export interface ModelItem {
  id: number
  models_name: string
  model_type: string // "0" | "1" | "Filter" | "Prediksi"
  is_active: boolean
  class_model?: number
  url?: string
}

export interface ActiveModelsResponse {
  filter: ModelItem | null
  diseases: ModelItem | null
}

export async function fetchModels(): Promise<ModelItem[]> {
  const response = await apiClient.get<ModelItem[]>("/model/show")
  return response.data
}

export async function fetchActiveModels(): Promise<[ModelItem | null, ModelItem | null]> {
  try {
    const response = await apiClient.get<[ModelItem | null, ModelItem | null]>("/model/show-active")
    return response.data
  } catch (err) {
    return [null, null]
  }
}

export async function setModelActive(id: number): Promise<{ message: string }> {
  const response = await apiClient.put<{ message: string }>(`/model/set-status/${id}`)
  return response.data
}

export async function deactivateModel(id: number): Promise<{ message: string; detail?: string }> {
  const response = await apiClient.put<{ message: string; detail?: string }>(`/model/deactivate/${id}`)
  return response.data
}

export async function deleteModel(id: number): Promise<{ message: string }> {
  const response = await apiClient.delete<{ message: string }>(`/model/delete/${id}`)
  return response.data
}

export async function uploadNewModel(data: {
  model_type: string
  class_model: number
  file: File
}): Promise<{ message: string }> {
  const formData = new FormData()
  formData.append("model_type", data.model_type)
  formData.append("class_model", data.class_model.toString())
  formData.append("file", data.file)

  const response = await apiClient.post<{ message: string }>("/model/add", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  })
  return response.data
}

