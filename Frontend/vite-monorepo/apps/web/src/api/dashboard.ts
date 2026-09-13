import { apiClient } from "./client"

export interface ConditionStat {
  id: number
  name: string
  count: number
}

export interface PredictionTrendItem {
  date: string
  label: string
  day: string
  count: number
}

export interface ActiveUserPreview {
  id: number
  email: string
  role: string
  is_active: boolean
  full_name: string
  avatar: string | null
  created_at: string | null
}

export interface RecentLogItem {
  id: number
  action: string
  module: string
  email: string
  ip: string
  browser: string
  created_at: string | null
}

export interface RecentPredictionItem {
  id: number
  image_path: string
  confidence: number
  condition: string
  email: string
  created_at: string | null
}

export interface DashboardSummaryResponse {
  total_users: number
  active_users: number
  total_predictions: number
  conditions_count: {
    sigatoka: number
    cordana: number
    healthy: number
    panama: number
  }
  conditions_list: ConditionStat[]
  prediction_trends: PredictionTrendItem[]
  active_users_list: ActiveUserPreview[]
  recent_logs: RecentLogItem[]
  recent_predictions: RecentPredictionItem[]
}

export async function fetchDashboardSummary(): Promise<DashboardSummaryResponse> {
  const response = await apiClient.get<DashboardSummaryResponse>("/dashboard/summary")
  return response.data
}

