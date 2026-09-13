import axios from "axios"

export const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000"

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
})

// Attach JWT Bearer token to each request if available
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token")
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor to handle 401 unauthorized
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("token")
    }
    return Promise.reject(error)
  }
)

export function getAssetUrl(path: string | null | undefined): string {
  if (!path) return ""
  if (path.startsWith("http://") || path.startsWith("https://")) return path
  const cleanPath = path.startsWith("/") ? path.slice(1) : path
  return `${API_BASE_URL}/${cleanPath}`
}
