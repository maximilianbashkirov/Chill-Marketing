import { useState } from 'react'
import { Box, Typography, TextField, Button, Card, CardContent, Grid, Paper, Chip, LinearProgress, Alert, ToggleButtonGroup, ToggleButton, Divider, Table, TableBody, TableCell, TableRow, Tooltip } from '@mui/material'
import { motion } from 'framer-motion'
import { useDispatch, useSelector } from 'react-redux'
import { startAnalysis, analysisSuccess, analysisFailure, clearAnalysis } from '@store/slices/analyticsSlice'
import { analyticsService, CompetitorAnalysisResult, SWOTAnalysisResult, AudienceAnalysisResult } from '@services/analyticsService'
import type { RootState } from '@store/store'

type AnalysisType = 'idea' | 'competitor' | 'swot' | 'audience'

const ANALYSIS_LABELS: Record<AnalysisType, { title: string; placeholder: string; hint: string }> = {
  idea: { title: 'Анализ маркетинговой идеи', placeholder: 'Опишите вашу маркетинговую идею...', hint: 'Введите описание вашей идеи, продукта или услуги' },
  competitor: { title: 'Конкурентный анализ', placeholder: 'Название конкурента, сайт или описание...', hint: 'Укажите название компании, сайт или опишите конкурента' },
  swot: { title: 'SWOT-анализ', placeholder: 'Опишите ваш бизнес, продукт или проект...', hint: 'Введите описание бизнеса для SWOT-анализа' },
  audience: { title: 'Сегментация аудитории', placeholder: 'Опишите ваш продукт или услугу...', hint: 'Введите описание продукта для определения ЦА' }
}

export default function AnalyticsPage() {
  const dispatch = useDispatch()
  const { currentAnalysis, isLoading, error } = useSelector((state: RootState) => state.analytics)
  
  const [analysisType, setAnalysisType] = useState<AnalysisType>('idea')
  const [input, setInput] = useState('')

  const handleAnalyze = async () => {
    if (!input.trim()) return
    
    console.log('DEBUG: analysisType =', analysisType)
    dispatch(startAnalysis())
    try {
      const result = await analyticsService.analyze({ 
        idea: input, 
        analysisType 
      })
      console.log('DEBUG: result =', result)
      dispatch(analysisSuccess(result))
    } catch (err: any) {
      dispatch(analysisFailure(err.message || 'Ошибка анализа'))
    }
  }

  const analysis = currentAnalysis?.analysis as any
  const { title, placeholder, hint } = ANALYSIS_LABELS[analysisType]

  const isCompetitor = analysisType === 'competitor' && analysis?.business_metrics
  const isSWOT = analysisType === 'swot' && analysis?.strategies
  const isAudience = analysisType === 'audience' && analysis?.segments

  const renderSWOTAnalysis = () => {
    const swot = analysis as SWOTAnalysisResult
    return (
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        <Card>
          <CardContent>
            <Typography variant="h6" sx={{ mb: 2, color: 'primary.main' }}>Описание бизнеса</Typography>
            <Typography variant="body2">{swot.business_description || 'Описание недоступно'}</Typography>
          </CardContent>
        </Card>

        <Grid container spacing={2}>
          <Grid item xs={6}>
            <Card sx={{ bgcolor: 'success.50' }}>
              <CardContent>
                <Typography variant="subtitle1" sx={{ fontWeight: 700, color: 'success.dark', mb: 2 }}>Сильные стороны (S)</Typography>
                {swot.strengths?.map((item, i) => (
                  <Box key={i} sx={{ mb: 2 }}>
                    <Typography variant="body2" sx={{ fontWeight: 600 }}>{item.title}</Typography>
                    <Typography variant="caption" color="text.secondary">{item.description}</Typography>
                    <Chip size="small" label={item.impact} sx={{ ml: 1, height: 20 }} />
                  </Box>
                ))}
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={6}>
            <Card sx={{ bgcolor: 'error.50' }}>
              <CardContent>
                <Typography variant="subtitle1" sx={{ fontWeight: 700, color: 'error.dark', mb: 2 }}>Слабые стороны (W)</Typography>
                {swot.weaknesses?.map((item, i) => (
                  <Box key={i} sx={{ mb: 2 }}>
                    <Typography variant="body2" sx={{ fontWeight: 600 }}>{item.title}</Typography>
                    <Typography variant="caption" color="text.secondary">{item.description}</Typography>
                    <Chip size="small" label={item.impact} sx={{ ml: 1, height: 20 }} />
                  </Box>
                ))}
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={6}>
            <Card sx={{ bgcolor: 'info.50' }}>
              <CardContent>
                <Typography variant="subtitle1" sx={{ fontWeight: 700, color: 'info.dark', mb: 2 }}>Возможности (O)</Typography>
                {swot.opportunities?.map((item, i) => (
                  <Box key={i} sx={{ mb: 2 }}>
                    <Typography variant="body2" sx={{ fontWeight: 600 }}>{item.title}</Typography>
                    <Typography variant="caption" color="text.secondary">{item.description}</Typography>
                    <Box sx={{ mt: 0.5 }}>
                      <Chip size="small" label={item.timeline} sx={{ mr: 0.5, height: 20 }} />
                      <Chip size="small" label={item.potential} sx={{ height: 20 }} />
                    </Box>
                  </Box>
                ))}
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={6}>
            <Card sx={{ bgcolor: 'warning.50' }}>
              <CardContent>
                <Typography variant="subtitle1" sx={{ fontWeight: 700, color: 'warning.dark', mb: 2 }}>Угрозы (T)</Typography>
                {swot.threats?.map((item, i) => (
                  <Box key={i} sx={{ mb: 2 }}>
                    <Typography variant="body2" sx={{ fontWeight: 600 }}>{item.title}</Typography>
                    <Typography variant="caption" color="text.secondary">{item.description}</Typography>
                    <Box sx={{ mt: 0.5 }}>
                      <Chip size="small" label={item.likelihood} sx={{ mr: 0.5, height: 20 }} />
                      <Chip size="small" label={item.severity} sx={{ height: 20 }} />
                    </Box>
                  </Box>
                ))}
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        <Card sx={{ bgcolor: 'secondary.50' }}>
          <CardContent>
            <Typography variant="h6" sx={{ mb: 2 }}>Стратегии (TOWS матрица)</Typography>
            <Grid container spacing={2}>
              {Object.entries(swot.strategies || {}).map(([strategy, items], i) => (
                <Grid item xs={6} key={i}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>{strategy}</Typography>
                  {items?.map((item: string, j: number) => (
                    <Typography key={j} variant="caption" sx={{ display: 'block', mb: 0.5 }}>• {item}</Typography>
                  ))}
                </Grid>
              ))}
            </Grid>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Typography variant="h6" sx={{ mb: 2, color: 'primary.main' }}>Ключевые инсайты</Typography>
            {swot.key_insights?.map((insight, i) => (
              <Typography key={i} variant="body2" sx={{ mb: 1 }}>• {insight}</Typography>
            ))}
          </CardContent>
        </Card>

        <Card sx={{ bgcolor: 'primary.50' }}>
          <CardContent>
            <Typography variant="h6" sx={{ mb: 2, color: 'primary.main' }}>Рекомендации</Typography>
            {swot.recommendations?.map((rec, i) => (
              <Typography key={i} variant="body2" sx={{ mb: 1 }}>• {rec}</Typography>
            ))}
          </CardContent>
        </Card>

        {swot.pest_factors && Object.keys(swot.pest_factors).length > 0 && (
          <Card sx={{ bgcolor: 'deepPurple.50' }}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, color: 'deepPurple.main' }}>PEST-анализ</Typography>
              <Grid container spacing={2}>
                {Object.entries(swot.pest_factors).map(([category, factors], i) => (
                  <Grid item xs={6} key={i}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>{category}</Typography>
                    {factors?.map((factor: string, j: number) => (
                      <Typography key={j} variant="caption" sx={{ display: 'block', mb: 0.5 }}>• {factor}</Typography>
                    ))}
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        )}

        {swot.kpis && swot.kpis.length > 0 && (
          <Card sx={{ bgcolor: 'indigo.50' }}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, color: 'indigo.main' }}>KPI для отслеживания</Typography>
              <Table size="small">
                <TableBody>
                  {swot.kpis.map((kpi, i) => (
                    <TableRow key={i}>
                      <TableCell sx={{ fontWeight: 600 }}>{kpi.name}</TableCell>
                      <TableCell>{kpi.description}</TableCell>
                      <TableCell>{kpi.target}</TableCell>
                      <TableCell>{kpi.current}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        )}

        {swot.competitor_comparison && swot.competitor_comparison.length > 0 && (
          <Card sx={{ bgcolor: 'orange.50' }}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, color: 'orange.main' }}>Сравнение с конкурентами</Typography>
              <Table size="small">
                <TableBody>
                  {swot.competitor_comparison.map((comp, i) => (
                    <TableRow key={i}>
                      <TableCell sx={{ fontWeight: 600 }}>{comp.metric}</TableCell>
                      <TableCell>{comp.your_position}</TableCell>
                      <TableCell>{comp.competitor_advantage}</TableCell>
                      <TableCell sx={{ fontWeight: 500, color: 'primary.main' }}>{comp.action}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        )}
      </Box>
    )
  }

  const renderAudienceAnalysis = () => {
    const audience = analysis as AudienceAnalysisResult
    return (
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        {audience.product_description && (
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, color: 'primary.main' }}>Описание продукта</Typography>
              <Typography variant="body2">{audience.product_description}</Typography>
            </CardContent>
          </Card>
        )}

        <Card sx={{ bgcolor: 'info.50' }}>
          <CardContent>
            <Typography variant="h6" sx={{ mb: 2, color: 'info.dark' }}>Общий объем рынка (TAM)</Typography>
            <Typography variant="body1" sx={{ fontWeight: 500 }}>{audience.total_addressable_market || 'Требует уточнения'}</Typography>
          </CardContent>
        </Card>

        <Card sx={{ bgcolor: 'success.50' }}>
          <CardContent>
            <Typography variant="h6" sx={{ mb: 2, color: 'success.dark' }}>Сегменты аудитории</Typography>
            <Grid container spacing={2}>
              {audience.segments?.map((seg, i) => (
                <Grid item xs={12} md={4} key={i}>
                  <Paper sx={{ p: 2, bgcolor: 'white' }}>
                    <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>{seg.name}</Typography>
                    <Chip label={seg.size} size="small" color="primary" sx={{ mb: 1 }} />
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>{seg.description}</Typography>
                    <Typography variant="caption" display="block">Возраст: {seg.age_range}</Typography>
                    <Typography variant="caption" display="block">Доход: {seg.income_level}</Typography>
                    <Typography variant="caption" display="block">Онлайн: {seg.online_behavior}</Typography>
                  </Paper>
                </Grid>
              ))}
            </Grid>
          </CardContent>
        </Card>

        {audience.primary_persona && (
          <Card sx={{ bgcolor: 'warning.50' }}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, color: 'warning.dark' }}>Главная персона (Primary Persona)</Typography>
              <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>{audience.primary_persona.name}</Typography>
              <Divider sx={{ my: 1 }} />
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="caption" sx={{ fontWeight: 600 }}>Демография:</Typography>
                  <Typography variant="body2">{audience.primary_persona.demographics}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="caption" sx={{ fontWeight: 600 }}>Цели:</Typography>
                  <Typography variant="body2">{audience.primary_persona.goals}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="caption" sx={{ fontWeight: 600 }}>Боли:</Typography>
                  <Typography variant="body2">{audience.primary_persona.frustrations}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="caption" sx={{ fontWeight: 600 }}>Ценности:</Typography>
                  <Typography variant="body2">{audience.primary_persona.values}</Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        )}

        <Grid container spacing={2}>
          <Grid item xs={6}>
            <Card>
              <CardContent>
                <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 1 }}>Поведенческие черты</Typography>
                {audience.behavioral_traits?.map((trait, i) => (
                  <Typography key={i} variant="body2" sx={{ mb: 0.5 }}>• {trait}</Typography>
                ))}
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={6}>
            <Card>
              <CardContent>
                <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 1 }}>Боли и проблемы</Typography>
                {audience.pain_points?.map((pain, i) => (
                  <Typography key={i} variant="body2" sx={{ mb: 0.5 }}>• {pain}</Typography>
                ))}
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={6}>
            <Card>
              <CardContent>
                <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 1 }}>Мотивации</Typography>
                {audience.motivations?.map((mot, i) => (
                  <Typography key={i} variant="body2" sx={{ mb: 0.5 }}>• {mot}</Typography>
                ))}
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={6}>
            <Card>
              <CardContent>
                <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 1 }}>Предпочитаемые каналы</Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {audience.preferred_channels?.map((ch, i) => (
                    <Chip key={i} label={ch} size="small" color="info" variant="outlined" />
                  ))}
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        <Card>
          <CardContent>
            <Typography variant="h6" sx={{ mb: 2 }}>Факторы принятия решения</Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {audience.decision_factors?.map((factor, i) => (
                <Chip key={i} label={factor} color="secondary" variant="outlined" />
              ))}
            </Box>
          </CardContent>
        </Card>

        <Card sx={{ bgcolor: 'primary.50' }}>
          <CardContent>
            <Typography variant="h6" sx={{ mb: 2, color: 'primary.main' }}>Ключевые инсайты</Typography>
            {audience.key_insights?.map((insight, i) => (
              <Typography key={i} variant="body2" sx={{ mb: 1 }}>• {insight}</Typography>
            ))}
          </CardContent>
        </Card>

        <Card sx={{ bgcolor: 'success.50' }}>
          <CardContent>
            <Typography variant="h6" sx={{ mb: 2, color: 'success.dark' }}>Рекомендации</Typography>
            {audience.recommendations?.map((rec, i) => (
              <Typography key={i} variant="body2" sx={{ mb: 1 }}>• {rec}</Typography>
            ))}
          </CardContent>
        </Card>
      </Box>
    )
  }

  const renderStandardAnalysis = () => (
    <Card>
      <CardContent>
        <Box sx={{ mb: 3 }}>
          <Tooltip title="Вероятность успеха рассчитывается на основе: уникальности идеи (30%), размера целевой аудитории (20%), конкурентности рынка (20%), реализуемости (15%), финансовой перспективы (15%). Модель анализирует сильные/слабые стороны и выводит 综合ную оценку." placement="top">
            <Chip 
              label={`Вероятность успеха: ${Math.round((analysis.success_probability || 0.5) * 100)}%`} 
              color="primary" 
              clickable
              sx={{ cursor: 'help' }}
            />
          </Tooltip>
        </Box>

        {analysis.ai_summary && (
          <Card sx={{ mb: 3, bgcolor: 'primary.50' }}>
            <CardContent>
              <Typography variant="subtitle1" sx={{ fontWeight: 600, color: 'primary.main', mb: 1 }}>Резюме от AI</Typography>
              <Typography variant="body2">{analysis.ai_summary}</Typography>
            </CardContent>
          </Card>
        )}
        
        <Typography variant="h6" sx={{ mb: 2 }}>Сильные стороны</Typography>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 3 }}>
          {(analysis.strengths || []).map((s: string, i: number) => (
            <Tooltip key={i} title={s} placement="top" arrow>
              <Chip label={s.length > 50 ? s.substring(0, 50) + '...' : s} color="success" variant="outlined" />
            </Tooltip>
          ))}
        </Box>
        
        <Typography variant="h6" sx={{ mb: 2 }}>Слабые стороны</Typography>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 3 }}>
          {(analysis.weaknesses || []).map((s: string, i: number) => (
            <Tooltip key={i} title={s} placement="top" arrow>
              <Chip label={s.length > 50 ? s.substring(0, 50) + '...' : s} color="error" variant="outlined" />
            </Tooltip>
          ))}
        </Box>
        
        <Typography variant="h6" sx={{ mb: 2 }}>Рекомендации</Typography>
        <Box sx={{ bgcolor: 'grey.50', p: 2, borderRadius: 2, mb: 3 }}>
          {(analysis.recommendations || []).map((r: string, i: number) => (
            <Typography key={i} variant="body2" sx={{ mb: 1 }}>• {r}</Typography>
          ))}
        </Box>

        {analysis.propagation_suggestions && analysis.propagation_suggestions.length > 0 && (
          <Card sx={{ bgcolor: 'success.50' }}>
            <CardContent>
              <Typography variant="subtitle1" sx={{ fontWeight: 600, color: 'success.dark', mb: 2 }}>Предложения по продвижению и масштабированию</Typography>
              {(analysis.propagation_suggestions || []).map((s: string, i: number) => (
                <Typography key={i} variant="body2" sx={{ mb: 1 }}>• {s}</Typography>
              ))}
            </CardContent>
          </Card>
        )}
      </CardContent>
    </Card>
  )

  const renderCompetitorAnalysis = () => {
    const comp = analysis as CompetitorAnalysisResult
    return (
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        <Card>
          <CardContent>
            <Typography variant="h6" sx={{ mb: 2, color: 'primary.main' }}>Информация о компании</Typography>
            <Table size="small">
              <TableBody>
                <TableRow><TableCell sx={{ fontWeight: 600 }}>Название</TableCell><TableCell>{comp.company_info?.name}</TableCell></TableRow>
                <TableRow><TableCell sx={{ fontWeight: 600 }}>Год основания</TableCell><TableCell>{comp.company_info?.founded_year}</TableCell></TableRow>
                <TableRow><TableCell sx={{ fontWeight: 600 }}>Штаб-квартира</TableCell><TableCell>{comp.company_info?.headquarters}</TableCell></TableRow>
                <TableRow><TableCell sx={{ fontWeight: 600 }}>Собственность</TableCell><TableCell>{comp.company_info?.ownership}</TableCell></TableRow>
                <TableRow><TableCell sx={{ fontWeight: 600 }}>Юр. форма</TableCell><TableCell>{comp.company_info?.legal_form}</TableCell></TableRow>
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Typography variant="h6" sx={{ mb: 2, color: 'primary.main' }}>Бизнес-показатели</Typography>
            <Table size="small">
              <TableBody>
                <TableRow><TableCell sx={{ fontWeight: 600 }}>Оборот (годовой)</TableCell><TableCell>{comp.business_metrics?.revenue} {comp.business_metrics?.revenue_currency}</TableCell></TableRow>
                <TableRow><TableCell sx={{ fontWeight: 600 }}>Сотрудников</TableCell><TableCell>{comp.business_metrics?.employees_count} ({comp.business_metrics?.employees_range})</TableCell></TableRow>
                <TableRow><TableCell sx={{ fontWeight: 600 }}>Филиалов/офисов</TableCell><TableCell>{comp.business_metrics?.branches_count}</TableCell></TableRow>
                <TableRow><TableCell sx={{ fontWeight: 600 }}>Франчайзинг</TableCell><TableCell>{comp.business_metrics?.franchise_count}</TableCell></TableRow>
                <TableRow><TableCell sx={{ fontWeight: 600 }}>Доля рынка</TableCell><TableCell>{comp.business_metrics?.market_share}</TableCell></TableRow>
                <TableRow><TableCell sx={{ fontWeight: 600 }}>Годовой рост</TableCell><TableCell>{comp.business_metrics?.annual_growth}</TableCell></TableRow>
                <TableRow><TableCell sx={{ fontWeight: 600 }}>Прибыльность</TableCell><TableCell>{comp.business_metrics?.profitability}</TableCell></TableRow>
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Typography variant="h6" sx={{ mb: 2, color: 'primary.main' }}>Позиционирование на рынке</Typography>
            <Table size="small">
              <TableBody>
                <TableRow><TableCell sx={{ fontWeight: 600 }}>Сегмент</TableCell><TableCell>{comp.market_position?.segment}</TableCell></TableRow>
                <TableRow><TableCell sx={{ fontWeight: 600 }}>Позиционирование</TableCell><TableCell>{comp.market_position?.positioning}</TableCell></TableRow>
                <TableRow><TableCell sx={{ fontWeight: 600 }}>Целевая аудитория</TableCell><TableCell>{comp.market_position?.target_audience}</TableCell></TableRow>
                <TableRow><TableCell sx={{ fontWeight: 600 }}>УТП</TableCell><TableCell>{comp.market_position?.unique_sellingProposition}</TableCell></TableRow>
                <TableRow><TableCell sx={{ fontWeight: 600 }}>Конкурентное преимущество</TableCell><TableCell>{comp.market_position?.competitive_advantage}</TableCell></TableRow>
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Typography variant="h6" sx={{ mb: 2, color: 'primary.main' }}>Каналы продвижения</Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {comp.marketing_channels?.map((ch: string, i: number) => (
                <Chip key={i} label={ch} color="info" variant="outlined" />
              ))}
            </Box>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Typography variant="h6" sx={{ mb: 2, color: 'primary.main' }}>Онлайн-присутствие</Typography>
            <Table size="small">
              <TableBody>
                <TableRow><TableCell sx={{ fontWeight: 600 }}>Сайт</TableCell><TableCell>{comp.online_presence?.website}</TableCell></TableRow>
                <TableRow><TableCell sx={{ fontWeight: 600 }}>Трафик/мес</TableCell><TableCell>{comp.online_presence?.website_traffic}</TableCell></TableRow>
                <TableRow><TableCell sx={{ fontWeight: 600 }}>SEO рейтинг</TableCell><TableCell>{comp.online_presence?.seo_rating}</TableCell></TableRow>
                <TableRow><TableCell sx={{ fontWeight: 600 }}>Рейтинг отзывов</TableCell><TableCell>{comp.online_presence?.reviews_rating}</TableCell></TableRow>
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Typography variant="h6" sx={{ mb: 2, color: 'primary.main' }}>SWOT-анализ конкурента</Typography>
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <Typography variant="subtitle2" sx={{ color: 'success.main', fontWeight: 600 }}>Сильные стороны</Typography>
                {comp.strengths?.map((s: string, i: number) => (
                  <Typography key={i} variant="body2" sx={{ mb: 0.5 }}>• {s}</Typography>
                ))}
              </Grid>
              <Grid item xs={6}>
                <Typography variant="subtitle2" sx={{ color: 'error.main', fontWeight: 600 }}>Слабые стороны</Typography>
                {comp.weaknesses?.map((s: string, i: number) => (
                  <Typography key={i} variant="body2" sx={{ mb: 0.5 }}>• {s}</Typography>
                ))}
              </Grid>
              <Grid item xs={6}>
                <Typography variant="subtitle2" sx={{ color: 'info.main', fontWeight: 600 }}>Возможности для вас</Typography>
                {comp.opportunities?.map((s: string, i: number) => (
                  <Typography key={i} variant="body2" sx={{ mb: 0.5 }}>• {s}</Typography>
                ))}
              </Grid>
              <Grid item xs={6}>
                <Typography variant="subtitle2" sx={{ color: 'warning.main', fontWeight: 600 }}>Угрозы</Typography>
                {comp.threats?.map((s: string, i: number) => (
                  <Typography key={i} variant="body2" sx={{ mb: 0.5 }}>• {s}</Typography>
                ))}
              </Grid>
            </Grid>
          </CardContent>
        </Card>

        <Card sx={{ bgcolor: 'primary.50' }}>
          <CardContent>
            <Typography variant="h6" sx={{ mb: 2, color: 'primary.main' }}>Рекомендации по конкуренции</Typography>
            {comp.recommendations?.map((r: string, i: number) => (
              <Typography key={i} variant="body2" sx={{ mb: 1 }}>• {r}</Typography>
            ))}
          </CardContent>
        </Card>
      </Box>
    )
  }

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 1, fontWeight: 700 }}>AI-powered аналитика</Typography>
      <Typography color="text.secondary" sx={{ mb: 4 }}>Используйте AI для глубокого маркетингового анализа</Typography>

      <ToggleButtonGroup value={analysisType} exclusive onChange={(_, v) => v && setAnalysisType(v)} sx={{ mb: 3 }} fullWidth>
        <ToggleButton value="idea">Идея</ToggleButton>
        <ToggleButton value="competitor">Конкуренты</ToggleButton>
        <ToggleButton value="swot">SWOT</ToggleButton>
        <ToggleButton value="audience">ЦА</ToggleButton>
      </ToggleButtonGroup>

      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2 }}>{title}</Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>{hint}</Typography>
              <TextField fullWidth multiline rows={4} placeholder={placeholder} value={input} onChange={(e) => setInput(e.target.value)} sx={{ mb: 3 }} />
              <Button variant="contained" size="large" fullWidth onClick={handleAnalyze} disabled={isLoading || !input.trim()}>
                {isLoading ? 'Анализ...' : 'Проанализировать'}
              </Button>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12}>
          {isLoading && <LinearProgress sx={{ mb: 2 }} />}
          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
          
          {analysis && (
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
              {isAudience ? renderAudienceAnalysis() : isSWOT ? renderSWOTAnalysis() : isCompetitor ? renderCompetitorAnalysis() : renderStandardAnalysis()}
            </motion.div>
          )}
        </Grid>
      </Grid>
    </Box>
  )
}
