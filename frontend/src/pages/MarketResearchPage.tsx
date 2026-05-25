import { useState } from 'react'
import { Box, Typography, TextField, Button, Card, CardContent, Grid, LinearProgress, Alert, Checkbox, FormControlLabel, Chip, Divider, Link } from '@mui/material'
import { motion } from 'framer-motion'
import { useDispatch, useSelector } from 'react-redux'
import { startResearch, researchSuccess, researchFailure } from '@store/slices/marketResearchSlice'
import { marketResearchService } from '@services/marketResearchService'
import { exportHTML, exportCSV, exportXLSX, exportDOC } from '@services/exportService'
import type { RootState } from '@store/store'
import type { MarketResearchResponse } from '@services/marketResearchService'

export default function MarketResearchPage() {
  const dispatch = useDispatch()
  const { currentResearch, isLoading, error } = useSelector((state: RootState) => state.marketResearch)
  
  const [topic, setTopic] = useState('')
  const [industry, setIndustry] = useState('')
  const [requirements, setRequirements] = useState({
    needStatistics: true,
    needCases: true,
    needStrategies: true,
    needExamples: true,
  })

  const handleResearch = async () => {
    if (!topic.trim()) return
    dispatch(startResearch())
    try {
      const result = await marketResearchService.conduct({ topic, industry, requirements })
      dispatch(researchSuccess(result))
    } catch (err: any) {
      dispatch(researchFailure(err.message || 'Ошибка исследования'))
    }
  }

  const r = currentResearch?.research

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 1, fontWeight: 700 }}>Маркетинговые исследования</Typography>
      <Typography color="text.secondary" sx={{ mb: 4 }}>Получите реальные цифры, статистику и кейсы по вашей теме</Typography>

      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <TextField fullWidth label="Тема исследования" value={topic} onChange={(e) => setTopic(e.target.value)} sx={{ mb: 2 }} />
              <TextField fullWidth label="Индустрия" value={industry} onChange={(e) => setIndustry(e.target.value)} sx={{ mb: 2 }} />
              
              <Typography variant="subtitle2" sx={{ mb: 1 }}>Что включить:</Typography>
              <FormControlLabel control={<Checkbox checked={requirements.needStatistics} onChange={(e) => setRequirements({...requirements, needStatistics: e.target.checked})} />} label="Статистика" />
              <FormControlLabel control={<Checkbox checked={requirements.needCases} onChange={(e) => setRequirements({...requirements, needCases: e.target.checked})} />} label="Кейсы" />
              <FormControlLabel control={<Checkbox checked={requirements.needStrategies} onChange={(e) => setRequirements({...requirements, needStrategies: e.target.checked})} />} label="Стратегии" />
              <FormControlLabel control={<Checkbox checked={requirements.needExamples} onChange={(e) => setRequirements({...requirements, needExamples: e.target.checked})} />} label="Примеры" />
              
              <Button variant="contained" size="large" fullWidth onClick={handleResearch} disabled={isLoading || !topic.trim()} sx={{ mt: 2 }}>
                {isLoading ? 'Исследование...' : 'Провести исследование'}
              </Button>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12}>
          {isLoading && <LinearProgress sx={{ mb: 2 }} />}
          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
          
          {r && (
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2, flexWrap: 'wrap', gap: 1 }}>
                    <Typography variant="h6">Обзор</Typography>
                    <Box sx={{ display: 'flex', gap: 0.5 }}>
                      <Button size="small" variant="outlined" onClick={() => exportHTML(currentResearch, currentResearch.topic)}>HTML</Button>
                      <Button size="small" variant="outlined" onClick={() => exportCSV(currentResearch, currentResearch.topic)}>CSV</Button>
                      <Button size="small" variant="outlined" onClick={() => exportXLSX(currentResearch, currentResearch.topic)}>XLSX</Button>
                      <Button size="small" variant="outlined" onClick={() => exportDOC(currentResearch, currentResearch.topic)}>DOC</Button>
                    </Box>
                  </Box>
                  <Typography variant="body2" sx={{ mb: 3, lineHeight: 1.6 }}>{r.overview}</Typography>
                  
                  {requirements.needStatistics && r.statistics?.length > 0 && (
                    <>
                      <Divider sx={{ my: 2 }} />
                      <Typography variant="h6" sx={{ mb: 2 }}>Статистика</Typography>
                      <Grid container spacing={2}>
                        {r.statistics.map((stat: any, i: number) => (
                          <Grid item xs={12} sm={6} key={i}>
                            <Box sx={{ p: 2, bgcolor: 'grey.50', borderRadius: 2, height: '100%' }}>
                              <Typography variant="caption" color="text.secondary" sx={{ textTransform: 'uppercase', letterSpacing: 0.5 }}>
                                {stat.metric}
                              </Typography>
                              <Typography variant="h5" sx={{ fontWeight: 700, mt: 0.5 }}>
                                {stat.value}
                              </Typography>
                              <Typography variant="caption" color="text.secondary">
                                {stat.source}, {stat.year}
                              </Typography>
                            </Box>
                          </Grid>
                        ))}
                      </Grid>
                    </>
                  )}

                  {requirements.needCases && r.cases?.length > 0 && (
                    <>
                      <Divider sx={{ my: 3 }} />
                      <Typography variant="h6" sx={{ mb: 2 }}>Кейсы</Typography>
                      {r.cases.map((c: any, i: number) => (
                        <Box key={i} sx={{ mb: 2, p: 2, border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
                          <Typography variant="subtitle2" sx={{ fontWeight: 600, color: 'primary.main' }}>{c.company}</Typography>
                          {c.description.split('\n\n').map((part: string, j: number) => (
                            <Typography key={j} variant="body2" sx={{ mt: 0.5, whiteSpace: 'pre-line' }}>{part}</Typography>
                          ))}
                          <Typography variant="body2" color="success.main" sx={{ mt: 1, fontWeight: 500 }}>Результат: {c.results}</Typography>
                          {c.source && (
                            <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
                              Источник:{' '}
                              {c.source.startsWith('http://') || c.source.startsWith('https://') ? (
                                <Link href={c.source} target="_blank" rel="noopener" underline="hover">{c.source}</Link>
                              ) : (
                                c.source
                              )}
                            </Typography>
                          )}
                        </Box>
                      ))}
                    </>
                  )}

                  {requirements.needStrategies && r.strategies?.length > 0 && (
                    <>
                      <Divider sx={{ my: 3 }} />
                      <Typography variant="h6" sx={{ mb: 2 }}>Стратегии</Typography>
                      {r.strategies.map((s: string, i: number) => {
                        const lines = s.split('\n')
                        return (
                          <Box key={i} sx={{ mb: 2, p: 2, bgcolor: 'grey.50', borderRadius: 2 }}>
                            <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
                              <Chip label={i + 1} size="small" color="primary" />
                              <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>{lines[0]}</Typography>
                            </Box>
                            {lines.slice(1).map((line: string, j: number) => (
                              line.startsWith('Шаги:')
                                ? <Typography key={j} variant="body2" sx={{ mt: 0.5, color: 'text.secondary' }}>{line}</Typography>
                                : line.startsWith('ROI:')
                                ? <Typography key={j} variant="body2" color="success.main" sx={{ mt: 0.5 }}>{line}</Typography>
                                : <Typography key={j} variant="body2" sx={{ mt: 0.5 }}>{line}</Typography>
                            ))}
                          </Box>
                        )
                      })}
                    </>
                  )}

                  {requirements.needExamples && r.examples?.length > 0 && (
                    <>
                      <Divider sx={{ my: 3 }} />
                      <Typography variant="h6" sx={{ mb: 2 }}>Примеры из практики</Typography>
                      {r.examples.map((e: any, i: number) => (
                        <Box key={i} sx={{ mb: 2, p: 2, border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
                          <Typography variant="subtitle2" sx={{ fontWeight: 600, color: 'primary.main' }}>{e.title}</Typography>
                          {e.context && (
                            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.5 }}>
                              Контекст: {e.context}
                            </Typography>
                          )}
                          <Typography variant="body2" sx={{ mt: 0.5 }}>{e.description}</Typography>
                          <Typography variant="body2" color="primary.main" sx={{ mt: 0.5, fontWeight: 500 }}>Результат: {e.outcome}</Typography>
                          {e.source && (
                            <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
                              Источник:{' '}
                              {typeof e.source === 'string' && (e.source.startsWith('http://') || e.source.startsWith('https://')) ? (
                                <Link href={e.source} target="_blank" rel="noopener" underline="hover">{e.source}</Link>
                              ) : (
                                e.source
                              )}
                            </Typography>
                          )}
                        </Box>
                      ))}
                    </>
                  )}

                  {r.trends?.length > 0 && (
                    <>
                      <Divider sx={{ my: 3 }} />
                      <Typography variant="h6" sx={{ mb: 2 }}>Тренды</Typography>
                      {r.trends.map((t: string, i: number) => (
                        <Box key={i} sx={{ mb: 1.5, p: 1.5, bgcolor: 'grey.50', borderRadius: 1 }}>
                          <Typography variant="body2" sx={{ lineHeight: 1.5 }}>▸ {t}</Typography>
                        </Box>
                      ))}
                    </>
                  )}

                  {r.competitive_map?.length > 0 && (
                    <>
                      <Divider sx={{ my: 3 }} />
                      <Typography variant="h6" sx={{ mb: 2 }}>Конкурентная карта</Typography>
                      {r.competitive_map.map((c: any, i: number) => (
                        <Box key={i} sx={{ mb: 2, p: 2, border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
                          <Typography variant="subtitle2" sx={{ fontWeight: 600, color: 'primary.main' }}>{c.company}</Typography>
                          <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>Доля: {c.market_share} | {c.specialization}</Typography>
                          <Box sx={{ mt: 1, display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                            {(c.strengths || []).map((s: string, j: number) => <Chip key={j} label={s} size="small" color="success" variant="outlined" />)}
                            {(c.weaknesses || []).map((w: string, j: number) => <Chip key={j} label={w} size="small" color="error" variant="outlined" />)}
                          </Box>
                          {(c.products || []).length > 0 && (
                            <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>Продукты: {c.products.join(', ')}</Typography>
                          )}
                        </Box>
                      ))}
                    </>
                  )}

                  {r.tech_stack && (
                    <>
                      <Divider sx={{ my: 3 }} />
                      <Typography variant="h6" sx={{ mb: 2 }}>Технологический стек</Typography>
                      <Box sx={{ mb: 1.5 }}>
                        <Typography variant="caption" color="text.secondary">Основные технологии:</Typography>
                        <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap', mt: 0.5 }}>
                          {(r.tech_stack.main_technologies || []).map((t: string, i: number) => <Chip key={i} label={t} size="small" />)}
                        </Box>
                      </Box>
                      <Box sx={{ mb: 1.5 }}>
                        <Typography variant="caption" color="text.secondary">Популярные инструменты:</Typography>
                        <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap', mt: 0.5 }}>
                          {(r.tech_stack.popular_tools || []).map((t: string, i: number) => <Chip key={i} label={t} size="small" variant="outlined" />)}
                        </Box>
                      </Box>
                      {r.tech_stack.emerging_tech?.length > 0 && (
                        <Box sx={{ mb: 1.5 }}>
                          <Typography variant="caption" color="text.secondary">Новые технологии:</Typography>
                          <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap', mt: 0.5 }}>
                            {(r.tech_stack.emerging_tech || []).map((t: string, i: number) => <Chip key={i} label={t} size="small" color="info" variant="outlined" />)}
                          </Box>
                        </Box>
                      )}
                      <Typography variant="body2" sx={{ mt: 1, p: 1.5, bgcolor: 'grey.50', borderRadius: 1 }}>
                        Типичный стек: {r.tech_stack.typical_stack}
                      </Typography>
                    </>
                  )}

                  {r.regulatory_risks?.length > 0 && (
                    <>
                      <Divider sx={{ my: 3 }} />
                      <Typography variant="h6" sx={{ mb: 2 }}>Регуляторные риски</Typography>
                      {r.regulatory_risks.map((rr: any, i: number) => (
                        <Box key={i} sx={{ mb: 2, p: 2, bgcolor: '#fff3e0', borderRadius: 2, border: '1px solid', borderColor: '#ffe0b2' }}>
                          <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>{rr.risk}</Typography>
                          <Typography variant="body2" sx={{ mt: 0.5 }}>{rr.description}</Typography>
                          <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.5 }}>Юрисдикция: {rr.jurisdiction}</Typography>
                          <Typography variant="body2" color="primary.main" sx={{ mt: 0.5 }}>Смягчение: {rr.mitigation}</Typography>
                        </Box>
                      ))}
                    </>
                  )}

                  {r.investment_landscape && (
                    <>
                      <Divider sx={{ my: 3 }} />
                      <Typography variant="h6" sx={{ mb: 2 }}>Инвестиционный ландшафт</Typography>
                      <Typography variant="body2" sx={{ fontWeight: 500, mb: 1 }}>{r.investment_landscape.total_funding}</Typography>
                      {(r.investment_landscape.notable_startups || []).length > 0 && (
                        <Box sx={{ mb: 1 }}><Typography variant="caption" color="text.secondary">Стартапы:</Typography> {r.investment_landscape.notable_startups.join('; ')}</Box>
                      )}
                      {(r.investment_landscape.key_investors || []).length > 0 && (
                        <Box><Typography variant="caption" color="text.secondary">Инвесторы:</Typography> {r.investment_landscape.key_investors.join(', ')}</Box>
                      )}
                    </>
                  )}

                  {r.pricing_analysis && (
                    <>
                      <Divider sx={{ my: 3 }} />
                      <Typography variant="h6" sx={{ mb: 2 }}>Ценовой анализ</Typography>
                      {(r.pricing_analysis.models || []).length > 0 && (
                        <Box sx={{ mb: 1.5 }}>
                          <Typography variant="caption" color="text.secondary">Модели:</Typography>
                          <Box component="ul" sx={{ m: 0, mt: 0.5, pl: 2 }}>
                            {r.pricing_analysis.models.map((m: string, i: number) => <Typography key={i} component="li" variant="body2">{m}</Typography>)}
                          </Box>
                        </Box>
                      )}
                      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                        <Typography variant="body2"><strong>Диапазон:</strong> {r.pricing_analysis.typical_range}</Typography>
                        <Typography variant="body2"><strong>Freemium:</strong> {r.pricing_analysis.freemium_prevalence}</Typography>
                        <Typography variant="body2"><strong>Enterprise:</strong> {r.pricing_analysis.enterprise_pricing}</Typography>
                      </Box>
                    </>
                  )}

                  {r.forecast && (
                    <>
                      <Divider sx={{ my: 3 }} />
                      <Typography variant="h6" sx={{ mb: 2 }}>Прогноз 3-5 лет</Typography>
                      <Grid container spacing={1} sx={{ mb: 2 }}>
                        <Grid item xs={12} sm={4}>
                          <Box sx={{ p: 1.5, bgcolor: '#e8f5e9', borderRadius: 1, height: '100%' }}>
                            <Typography variant="caption" color="text.secondary">1 год</Typography>
                            <Typography variant="body2">{r.forecast.short_term_1year}</Typography>
                          </Box>
                        </Grid>
                        <Grid item xs={12} sm={4}>
                          <Box sx={{ p: 1.5, bgcolor: '#e3f2fd', borderRadius: 1, height: '100%' }}>
                            <Typography variant="caption" color="text.secondary">3 года</Typography>
                            <Typography variant="body2">{r.forecast.medium_term_3year}</Typography>
                          </Box>
                        </Grid>
                        <Grid item xs={12} sm={4}>
                          <Box sx={{ p: 1.5, bgcolor: '#f3e5f5', borderRadius: 1, height: '100%' }}>
                            <Typography variant="caption" color="text.secondary">5 лет</Typography>
                            <Typography variant="body2">{r.forecast.long_term_5year}</Typography>
                          </Box>
                        </Grid>
                      </Grid>
                      {(r.forecast.key_drivers || []).length > 0 && (
                        <Box sx={{ mb: 1 }}><Typography variant="caption" color="success.main">Драйверы роста:</Typography> {r.forecast.key_drivers.join('; ')}</Box>
                      )}
                      {(r.forecast.key_barriers || []).length > 0 && (
                        <Box><Typography variant="caption" color="error.main">Барьеры:</Typography> {r.forecast.key_barriers.join('; ')}</Box>
                      )}
                    </>
                  )}

                  {r.key_metrics && (
                    <>
                      <Divider sx={{ my: 3 }} />
                      <Typography variant="h6" sx={{ mb: 2 }}>Ключевые метрики</Typography>
                      <Grid container spacing={1}>
                        {[
                          { label: 'CAC', value: r.key_metrics.average_cac },
                          { label: 'LTV', value: r.key_metrics.average_ltv },
                          { label: 'LTV/CAC', value: r.key_metrics.ltv_cac_ratio },
                          { label: 'Конверсия', value: r.key_metrics.conversion_rate },
                          { label: 'Retention', value: r.key_metrics.retention_rate },
                          { label: 'Отток', value: r.key_metrics.churn_rate },
                        ].map((m: any, i: number) => (
                          <Grid item xs={6} sm={4} key={i}>
                            <Box sx={{ p: 1.5, bgcolor: 'grey.50', borderRadius: 1, textAlign: 'center' }}>
                              <Typography variant="caption" color="text.secondary">{m.label}</Typography>
                              <Typography variant="body2" sx={{ fontWeight: 600 }}>{m.value}</Typography>
                            </Box>
                          </Grid>
                        ))}
                      </Grid>
                    </>
                  )}

                  {r.sources && r.sources.length > 0 && (
                    <>
                      <Divider sx={{ my: 3 }} />
                      <Typography variant="h6" sx={{ mb: 2 }}>Источники</Typography>
                      <Box component="ul" sx={{ m: 0, pl: 2 }}>
                        {r.sources.map((s: string, i: number) => (
                          <Typography key={i} component="li" variant="caption" color="text.secondary" sx={{ mb: 0.5 }}>
                            {typeof s === 'string' && (s.startsWith('http://') || s.startsWith('https://')) ? (
                              <Link href={s} target="_blank" rel="noopener" underline="hover">{s}</Link>
                            ) : (
                              s
                            )}
                          </Typography>
                        ))}
                      </Box>
                    </>
                  )}
                </CardContent>
              </Card>
            </motion.div>
          )}
        </Grid>
      </Grid>
    </Box>
  )
}
