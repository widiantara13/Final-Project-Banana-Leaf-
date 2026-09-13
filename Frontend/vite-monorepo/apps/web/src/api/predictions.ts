import { apiClient } from "./client"

export interface PredictionItem {
  id: number
  image_path: string
  condition: string
  confidence: number
  email: string
  created_at: string
}

export interface PaginatedPredictions {
  items: PredictionItem[]
  total: number
  page: number
  size: number
  pages?: number
}

export async function fetchPredictions(
  page = 1,
  size = 7,
  email?: string
): Promise<PaginatedPredictions> {
  let url = `/predict/show-all?page=${page}&size=${size}`
  if (email && email.trim() !== "") {
    url += `&email=${encodeURIComponent(email.trim())}`
  }
  const response = await apiClient.get<PaginatedPredictions>(url)
  return response.data
}

