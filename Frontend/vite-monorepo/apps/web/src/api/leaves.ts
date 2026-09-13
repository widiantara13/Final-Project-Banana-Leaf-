import { apiClient } from "./client"

export interface LeafConditionItem {
  id: number
  condition: string
  description: string
  treatment: string
  image_reference: string
}

export async function fetchLeafConditions(): Promise<LeafConditionItem[]> {
  const response = await apiClient.get<LeafConditionItem[]>("/leaf/show")
  return response.data
}

export async function fetchLeafConditionDetail(
  id: number
): Promise<LeafConditionItem> {
  const response = await apiClient.get<LeafConditionItem>(`/leaf/show/${id}`)
  return response.data
}

export async function updateLeafCondition(
  id: number,
  data: {
    condition: string
    description: string
    treatment: string
    file?: File | null
  }
): Promise<{ message: string }> {
  const formData = new FormData()
  formData.append("condition", data.condition)
  formData.append("description", data.description)
  formData.append("treatment", data.treatment)
  if (data.file) {
    formData.append("file", data.file)
  }

  const response = await apiClient.patch<{ message: string }>(
    `/leaf/update/${id}`,
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    }
  )
  return response.data
}

