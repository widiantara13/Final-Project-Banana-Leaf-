import { apiClient } from "./client"

export interface LogItem {
  id: number
  user_id: number | null
  email: string | null
  action: string
  module: string
  ip: string | null
  browser: string | null
  created_at: string
}

export interface PaginatedLogs {
  items: LogItem[]
  total: number
  page: number
  size: number
  pages?: number
}

export async function fetchLogs(
  page = 1,
  size = 7,
  email?: string
): Promise<PaginatedLogs> {
  let url = `/log/show?page=${page}&size=${size}`
  if (email && email.trim() !== "") {
    url += `&email=${encodeURIComponent(email.trim())}`
  }
  const response = await apiClient.get<PaginatedLogs>(url)
  return response.data
}

