import apiClient from './api'

const METRIC_LABELS: Record<string, string> = {
  market_size: 'Размер рынка',
  growth_rate: 'Темп роста',
  unemployment_rate: 'Уровень безработицы',
  key_players_count: 'Ключевые игроки',
  market_leaders: 'Лидеры рынка',
  regional_distribution: 'Распределение по регионам',
}

function formatStatValue(key: string, raw: string): string {
  if (!raw || raw === 'data not available' || raw === 'нет данных' || raw === 'н/д') return ''
  const num = Number(raw)
  if (isNaN(num)) return raw
  if (key === 'growth_rate' || key === 'unemployment_rate') return `${Number(num.toFixed(2))}%`
  if (key === 'market_size') {
    if (num >= 1e12) return `$${(num / 1e12).toFixed(2)} трлн`
    if (num >= 1e9) return `$${(num / 1e9).toFixed(2)} млрд`
    if (num >= 1e6) return `$${(num / 1e6).toFixed(2)} млн`
    return `$${num.toLocaleString()}`
  }
  return num.toLocaleString()
}

const NA_VALUES = new Set(['data not available', '', 'n/a', 'none', 'нет данных', 'н/д'])

export interface MarketResearchRequest {
  topic: string
  industry?: string
  requirements?: {
    needStatistics: boolean
    needCases: boolean
    needStrategies: boolean
    needExamples: boolean
  }
}

export interface MarketResearchResponse {
  id: number
  topic: string
  research: {
    overview: string
    statistics?: Array<{
      metric: string
      value: string
      source: string
      year: number
    }>
    competitive_map?: Array<{
      company: string
      market_share: string
      specialization: string
      strengths: string[]
      weaknesses: string[]
      products: string[]
    }>
    tech_stack?: {
      main_technologies: string[]
      popular_tools: string[]
      emerging_tech: string[]
      typical_stack: string
    }
    regulatory_risks?: Array<{
      risk: string
      description: string
      jurisdiction: string
      mitigation: string
    }>
    investment_landscape?: {
      total_funding: string
      notable_startups: string[]
      key_investors: string[]
      recent_deals: string[]
    }
    pricing_analysis?: {
      models: string[]
      typical_range: string
      freemium_prevalence: string
      enterprise_pricing: string
    }
    forecast?: {
      short_term_1year: string
      medium_term_3year: string
      long_term_5year: string
      key_drivers: string[]
      key_barriers: string[]
    }
    key_metrics?: {
      average_cac: string
      average_ltv: string
      ltv_cac_ratio: string
      conversion_rate: string
      retention_rate: string
      churn_rate: string
    }
    cases?: Array<{
      company: string
      description: string
      results: string
      source?: string
      keyTakeaways?: string[]
    }>
    strategies?: string[]
    examples?: Array<{
      title: string
      context?: string
      description: string
      outcome: string
      source?: string
    }>
    trends?: string[]
    sources?: string[]
  }
  createdAt: string
}

function mapResearch(raw: any, topic: string): MarketResearchResponse['research'] {
  const r = raw?.data?.research || raw?.research || raw || {}
  const statsObj = r.statistics || {}

  const statsArray: MarketResearchResponse['research']['statistics'] = Object.entries(statsObj)
    .filter(([_, v]) => !NA_VALUES.has(String(v ?? '').toLowerCase()))
    .map(([k, v]) => {
      const formatted = formatStatValue(k, String(v ?? ''))
      if (!formatted) return null
      return {
        metric: METRIC_LABELS[k] || k.replace(/_/g, ' ').replace(/\b\w/g, (c: string) => c.toUpperCase()),
        value: formatted,
        source: 'World Bank',
        year: new Date().getFullYear(),
      }
    })
    .filter(Boolean) as MarketResearchResponse['research']['statistics']

  return {
    overview: r.overview || `Результаты исследования по теме "${topic}"`,
    statistics: statsArray,
    competitive_map: r.competitive_map,
    tech_stack: r.tech_stack,
    regulatory_risks: r.regulatory_risks,
    investment_landscape: r.investment_landscape,
    pricing_analysis: r.pricing_analysis,
    forecast: r.forecast,
    key_metrics: r.key_metrics,
    cases: (r.cases || []).map((c: any) => ({
      company: c.company || '',
      description: `${c.challenge || c.description || ''}\n\nРешение: ${c.solution || ''}`,
      results: c.result || c.results || '',
      source: c.source || '',
      keyTakeaways: [],
    })),
    strategies: (r.strategies || []).map((s: any) =>
      typeof s === 'string'
        ? s
        : `${s.name || ''}: ${s.description || ''}${s.implementation_steps ? '\nШаги: ' + s.implementation_steps.join(', ') : ''}${s.expected_roi ? '\nROI: ' + s.expected_roi : ''}`
    ).filter(Boolean),
    examples: (r.examples || []).map((e: any) => ({
      title: e.company || e.name || e.type || 'Пример',
      context: e.context || '',
      description: e.approach || e.description || '',
      outcome: e.metrics || e.result || '',
      source: e.source || '',
    })),
    trends: r.trends || [],
    sources: r.sources || [],
  }
}

export const marketResearchService = {
  conduct: async (request: MarketResearchRequest): Promise<MarketResearchResponse> => {
    const response = await apiClient.post('/market-research/conduct', request)
    const research = mapResearch(response.data, request.topic)
    return {
      id: response.data?.data?.request_id || 0,
      topic: request.topic,
      research,
      createdAt: new Date().toISOString(),
    }
  },

  getHistory: async (): Promise<MarketResearchResponse[]> => {
    const response = await apiClient.get('/market-research/history')
    const list = response.data || []
    return list.map((item: any, i: number) => ({
      id: item.id || i,
      topic: item.topic || '',
      research: mapResearch(item, item.topic || ''),
      createdAt: item.created_at || new Date().toISOString(),
    }))
  },

  getById: async (id: number): Promise<MarketResearchResponse> => {
    const response = await apiClient.get(`/market-research/${id}`)
    const research = mapResearch(response.data, response.data?.topic || '')
    return {
      id: response.data?.id || id,
      topic: response.data?.topic || '',
      research,
      createdAt: response.data?.created_at || new Date().toISOString(),
    }
  },
}
