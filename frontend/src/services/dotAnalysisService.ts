import apiClient from './api'

export interface DotAnalysisRequest {
  caseDescription: string
  industry?: string
}

export interface SelectedModel {
  key: string
  name: string
  category: string
  description: string
  reason: string
}

export interface ModelAnalysis {
  key: string
  name: string
  category: string
  description: string
  analysis: Record<string, any>
  template_structure: string
}

export interface DotAnalysisResponse {
  id: number
  data: {
    data: {
      request_id: number
      industry: string
      selected_models: SelectedModel[]
      analyses: ModelAnalysis[]
    }
  }
  request_id: number
  industry: string
  selected_models: SelectedModel[]
  analyses: ModelAnalysis[]
}

export const dotAnalysisService = {
  analyze: async (request: DotAnalysisRequest): Promise<DotAnalysisResponse> => {
    const response = await apiClient.post('/dot-analysis/analyze', {
      caseDescription: request.caseDescription,
      industry: request.industry,
    })
    return response.data
  },

  getHistory: async (): Promise<DotAnalysisResponse[]> => {
    const response = await apiClient.get('/dot-analysis/requests')
    return response.data
  },

  getById: async (id: number): Promise<DotAnalysisResponse> => {
    const response = await apiClient.get(`/dot-analysis/requests/${id}`)
    return response.data
  },

  getAvailableModels: async (): Promise<any[]> => {
    const response = await apiClient.get('/dot-analysis/models')
    return response.data
  },
}
