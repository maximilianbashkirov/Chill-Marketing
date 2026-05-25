import apiClient from './api'

export interface SMIArticle {
  title: string
  source_name: string
  description: string
  full_text: string
  link: string
  published_at: string
}

export interface ViralPotential {
  score: number
  factors: string[]
  similar_articles: Array<{title: string; source: string; description: string; url: string}>
}

export interface SMIAnalyzeRequest {
  topic: string
  keywords?: string[]
}

export interface SMIAnalyzeResponse {
  request_id: number
  analysis: {
    articles_found: number
    relevance_score: number
    sources: Record<string, number>
    viral_potential: ViralPotential
    recommendations: string[]
    best_platforms: string[]
    estimated_reach: string
    rss_articles: SMIArticle[]
    from_cache?: boolean
  }
}

export const smiService = {
  analyze: async (request: SMIAnalyzeRequest): Promise<SMIAnalyzeResponse> => {
    const response = await apiClient.post('/smi/analyze', request)
    return response.data.data
  },

  getHistory: async (): Promise<SMIAnalyzeResponse[]> => {
    const response = await apiClient.get('/smi/history')
    return response.data
  },

  getById: async (id: number): Promise<SMIAnalyzeResponse> => {
    const response = await apiClient.get(`/smi/${id}`)
    return response.data
  },
}
