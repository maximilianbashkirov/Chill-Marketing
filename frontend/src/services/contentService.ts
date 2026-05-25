import apiClient from './api'

export interface ContentAnalyzeRequest {
  content_type: string
  content: string
  platform?: string
  target_audience?: string
}

export interface ContentAnalysisResult {
  success_probability: number
  viral_potential: number
  originality_score?: number
  engagement_prediction: { likes: string; comments: string; shares: string }
  strengths: string[]
  weaknesses: string[]
  recommendations: string[]
  best_posting_time: string
  suggested_hashtags: string[]
  similar_content?: Array<{ title: string; platform: string; url: string }>
  trend_alignment?: { trending_score: string; alignment: string }
  format_suggestions?: Array<{ name: string; description: string; platforms: string[] }>
  content_ideas?: string[]
  key_words?: string[]
  posting_schedule?: Array<{ day: string; time: string }>
  target_audience?: string
  audience_segments?: Array<{ name: string; description: string; age_range: string; interests: string[]; pain_points: string[] }>
}

export const contentService = {
  analyze: async (request: ContentAnalyzeRequest): Promise<ContentAnalysisResult> => {
    const response = await apiClient.post('/content/analyze', request)
    return response.data.data.analysis
  },
}
