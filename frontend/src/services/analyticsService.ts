import apiClient from './api'

export interface AnalyzeRequest {
  idea: string
  industry?: string
  targetAudience?: string
  analysisType?: 'idea' | 'competitor' | 'swot' | 'audience'
}

export interface AnalysisResult {
  success_probability: number
  strengths: string[]
  weaknesses: string[]
  recommendations: string[]
  similar_cases?: any[]
  suggested_models?: string[]
  ai_summary?: string
  propagation_suggestions?: string[]
}

export interface CompetitorAnalysisResult {
  company_info: {
    name: string
    founded_year: string
    headquarters: string
    ownership: string
    legal_form: string
    registration_info: string
  }
  business_metrics: {
    revenue: string
    revenue_currency: string
    employees_count: string
    employees_range: string
    branches_count: string
    franchise_count: string
    market_share: string
    annual_growth: string
    profitability: string
  }
  market_position: {
    segment: string
    positioning: string
    target_audience: string
    unique_sellingProposition: string
    competitive_advantage: string
  }
  products_services: Array<{
    name: string
    description: string
    price_range: string
    popularity: string
  }>
  pricing: {
    model: string
    average_check: string
    discounts: string
    payment_terms: string
  }
  marketing_channels: string[]
  online_presence: {
    website: string
    website_traffic: string
    seo_rating: string
    social_media: Record<string, string>
    app_downloads: string
    reviews_rating: string
  }
  strengths: string[]
  weaknesses: string[]
  opportunities: string[]
  threats: string[]
  recommendations: string[]
}

export interface SWOTAnalysisResult {
  business_description: string
  strengths: Array<{title: string; description: string; impact: string; category: string}>
  weaknesses: Array<{title: string; description: string; impact: string; category: string}>
  opportunities: Array<{title: string; description: string; timeline: string; potential: string}>
  threats: Array<{title: string; description: string; likelihood: string; severity: string}>
  strategies: Record<string, string[]>
  key_insights: string[]
  recommendations: string[]
  pest_factors?: Record<string, string[]>
  kpis?: Array<{name: string; description: string; target: string; current: string}>
  competitor_comparison?: Array<{metric: string; your_position: string; competitor_advantage: string; action: string}>
}

export interface AudienceAnalysisResult {
  product_description: string
  total_addressable_market: string
  segments: Array<{
    name: string
    size: string
    description: string
    age_range: string
    income_level: string
    online_behavior: string
  }>
  primary_persona: {
    name: string
    demographics: string
    goals: string
    frustrations: string
    values: string
  }
  behavioral_traits: string[]
  pain_points: string[]
  motivations: string[]
  preferred_channels: string[]
  decision_factors: string[]
  key_insights: string[]
  recommendations: string[]
}

export interface AnalyzeResponse {
  request_id: number
  analysis: AnalysisResult | CompetitorAnalysisResult | SWOTAnalysisResult | AudienceAnalysisResult
  analysis_type?: string
}

export const analyticsService = {
  analyze: async (request: AnalyzeRequest): Promise<AnalyzeResponse> => {
    const response = await apiClient.post('/analytics/analyze', request)
    return response.data.data
  },

  getHistory: async (): Promise<AnalyzeResponse[]> => {
    const response = await apiClient.get('/analytics/requests')
    return response.data
  },

  getById: async (id: number): Promise<AnalyzeResponse> => {
    const response = await apiClient.get(`/analytics/requests/${id}`)
    return response.data
  },
}
