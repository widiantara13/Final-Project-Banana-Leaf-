import { apiClient } from "./client"

export interface LoginResponse {
  access_token: string
  token_type: string
}

export interface UserProfile {
  id: number
  full_name: string | null
  address: string | null
  phone_number: string | null
  avatar: string | null
  user_id: number
}

export async function loginUser(email: string, password: string):Promise<LoginResponse> {
  // OAuth2PasswordRequestForm expects application/x-www-form-urlencoded
  const params = new URLSearchParams()
  params.append("username", email)
  params.append("password", password)

  const response = await apiClient.post<LoginResponse>("/auth/login", params, {
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
  })
  return response.data
}

export async function logoutUser(): Promise<void> {
  try {
    await apiClient.post("/auth/logout/")
  } finally {
    localStorage.removeItem("token")
  }
}

export async function getProfile(): Promise<UserProfile> {
  const response = await apiClient.get<UserProfile>("/profile/show")
  return response.data
}

