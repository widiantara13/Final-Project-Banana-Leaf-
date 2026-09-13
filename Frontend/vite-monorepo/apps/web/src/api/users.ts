import { apiClient } from "./client"

export interface UserItem {
  id: number
  uuid: string
  email: string
  role: "admin" | "petani"
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface PaginatedUsers {
  items: UserItem[]
  total: number
  page: number
  size: number
  pages?: number
}

export interface FullProfile {
  user_id: number
  email: string
  role: string
  is_active: boolean
  full_name: string | null
  phone_number: string | null
  address: string | null
  avatar: string | null
}

export async function fetchUsers(page = 1, size = 7): Promise<PaginatedUsers> {
  const response = await apiClient.get<PaginatedUsers>(`/users/show?page=${page}&size=${size}`)
  return response.data
}

export async function fetchFullProfile(userId?: number): Promise<FullProfile> {
  const url = userId ? `/profile/detail/${userId}` : `/profile/detail`
  const response = await apiClient.get<FullProfile>(url)
  return response.data
}
