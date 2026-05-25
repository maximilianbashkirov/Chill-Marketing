import { useState } from 'react'
import { Box, Typography, TextField, Button, Card, CardContent, Grid, Chip, LinearProgress, Alert, Select, MenuItem, FormControl, InputLabel, Divider, Tooltip, Paper } from '@mui/material'
import { motion } from 'framer-motion'
import { useDispatch, useSelector } from 'react-redux'
import { startAnalysis, analysisSuccess, analysisFailure } from '@store/slices/contentSlice'
import { contentService, ContentAnalysisResult } from '@services/contentService'
import type { RootState } from '@store/store'

export default function ContentPage() {
  const dispatch = useDispatch()
  const { currentAnalysis, isLoading, error } = useSelector((state: RootState) => state.content)
  
  const [content, setContent] = useState('')
  const [contentType, setContentType] = useState('post')
  const [platform, setPlatform] = useState('instagram')

  const handleAnalyze = async () => {
    if (!content.trim()) return
    console.log('Starting analysis...')
    dispatch(startAnalysis())
    try {
      const result = await contentService.analyze({ 
        content, 
        content_type: contentType, 
        platform
      })
      console.log('Analysis result:', result)
      dispatch(analysisSuccess(result))
    } catch (err: any) {
      console.error('Analysis error:', err)
      dispatch(analysisFailure(err.message || 'Ошибка анализа'))
    }
  }

  const analysis = currentAnalysis as ContentAnalysisResult
  console.log('Current analysis in render:', currentAnalysis)

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 1, fontWeight: 700 }}>AI Анализ контента</Typography>
      <Typography color="text.secondary" sx={{ mb: 4 }}>Оцените идею для поста, рилса или подкаста с анализом трендов</Typography>

      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Grid container spacing={2}>
                <Grid item xs={12} md={3}>
                  <FormControl fullWidth>
                    <InputLabel>Тип контента</InputLabel>
                    <Select value={contentType} label="Тип контента" onChange={(e) => setContentType(e.target.value)}>
                      <MenuItem value="post">Пост</MenuItem>
                      <MenuItem value="reel">Reels/Shorts</MenuItem>
                      <MenuItem value="article">Статья</MenuItem>
                      <MenuItem value="story">Story</MenuItem>
                      <MenuItem value="carousel">Карусель</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} md={3}>
                  <FormControl fullWidth>
                    <InputLabel>Платформа</InputLabel>
                    <Select value={platform} label="Платформа" onChange={(e) => setPlatform(e.target.value)}>
                      <MenuItem value="instagram">Instagram</MenuItem>
                      <MenuItem value="telegram">Telegram</MenuItem>
                      <MenuItem value="youtube">YouTube</MenuItem>
                      <MenuItem value="tiktok">TikTok</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField fullWidth multiline rows={3} label="Идея контента" placeholder="Опишите вашу идею..." value={content} onChange={(e) => setContent(e.target.value)} />
                </Grid>
              </Grid>
              <Button variant="contained" size="large" fullWidth onClick={handleAnalyze} disabled={isLoading || !content.trim()} sx={{ mt: 2 }}>
                {isLoading ? 'Анализ...' : 'Проанализировать контент'}
              </Button>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12}>
          {isLoading && <LinearProgress sx={{ mb: 2 }} />}
          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
          
          {analysis && (
            <motion.div 
              key={Date.now()}
              initial={{ opacity: 0, y: 20 }} 
              animate={{ opacity: 1, y: 0 }}
            >
              <Grid container spacing={2}>
                <Grid item xs={12} md={4}>
                  <Card sx={{ bgcolor: 'primary.50', height: '100%' }}>
                    <CardContent>
                      <Typography variant="h6" sx={{ mb: 2 }}>Оценка контента</Typography>
                      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                        <Tooltip title="Вероятность успеха = (уникальность × 0.3) + (виральность × 0.25) + (соответствие трендам × 0.25) + (качество контента × 0.2)" placement="top" arrow>
                          <Chip label={`Успех: ${Math.round((analysis.success_probability || 0.5) * 100)}%`} color="primary" clickable sx={{ cursor: 'help' }} />
                        </Tooltip>
                        <Tooltip title="Виральность = (эмоциональность × 0.35) + (новизна × 0.25) + (визуальная привлекательность × 0.2) + (трендовость × 0.2)" placement="top" arrow>
                          <Chip label={`Виральность: ${Math.round((analysis.viral_potential || 0.5) * 10)}/10`} color="secondary" clickable sx={{ cursor: 'help' }} />
                        </Tooltip>
                        {analysis.originality_score !== undefined && (
                          <Tooltip title="Оригинальность = (уникальность идеи × 0.4) + (свежесть подхода × 0.3) + (отличие от конкурентов × 0.3)" placement="top" arrow>
                            <Chip label={`Оригинальность: ${Math.round(analysis.originality_score * 10)}/10`} color="info" clickable sx={{ cursor: 'help' }} />
                          </Tooltip>
                        )}
                      </Box>
                      <Divider sx={{ my: 2 }} />
                      <Typography variant="subtitle2" sx={{ mb: 1 }}>Прогноз вовлеченности:</Typography>
                      <Typography variant="body2">❤️ Лайки: {analysis.engagement_prediction?.likes || 'N/A'}</Typography>
                      <Typography variant="body2">💬 Комментарии: {analysis.engagement_prediction?.comments || 'N/A'}</Typography>
                      <Typography variant="body2">🔄 Репосты: {analysis.engagement_prediction?.shares || 'N/A'}</Typography>
                    </CardContent>
                  </Card>
                </Grid>

                <Grid item xs={12} md={4}>
                  <Card sx={{ bgcolor: 'warning.50', height: '100%' }}>
                    <CardContent>
                      <Typography variant="h6" sx={{ mb: 2 }}>Рекомендации</Typography>
                      {(analysis.recommendations || []).map((r: string, i: number) => (
                        <Typography key={i} variant="body2" sx={{ mb: 1 }}>• {r}</Typography>
                      ))}
                    </CardContent>
                  </Card>
                </Grid>

                <Grid item xs={12} md={4}>
                  <Card sx={{ height: '100%' }}>
                    <CardContent>
                      <Typography variant="h6" sx={{ mb: 2 }}>⏰ Время постинга</Typography>
                      <Typography variant="body2" sx={{ mb: 1 }}>Лучшее время: <strong>{analysis.best_posting_time || '19:00-21:00'}</strong></Typography>
                      {(analysis.posting_schedule || []).length > 0 && (
                        <Box sx={{ mt: 1 }}>
                          {(analysis.posting_schedule || []).map((sch: { day: string; time: string }, i: number) => (
                            <Typography key={i} variant="caption" sx={{ display: 'block' }}>{sch.day}: {sch.time}</Typography>
                          ))}
                        </Box>
                      )}
                    </CardContent>
                  </Card>
                </Grid>

                {analysis.audience_segments && analysis.audience_segments.length > 0 && (
                  <Grid item xs={12}>
                    <Card sx={{ bgcolor: 'cyan.50' }}>
                      <CardContent>
                        <Typography variant="h6" sx={{ mb: 2 }}>🎯 Сегменты целевой аудитории</Typography>
                        <Grid container spacing={2}>
                          {(analysis.audience_segments as Array<{name: string, description: string, age_range: string, interests: string[], pain_points: string[]}>).map((segment, i) => (
                            <Grid item xs={12} sm={6} md={3} key={i}>
                              <Paper sx={{ p: 2, bgcolor: 'white', height: '100%' }}>
                                <Typography variant="subtitle1" fontWeight="bold" sx={{ mb: 1 }}>
                                  {segment.name}
                                </Typography>
                                <Typography variant="caption" color="primary">{segment.age_range}</Typography>
                                <Typography variant="body2" sx={{ mb: 1, mt: 1 }}>{segment.description}</Typography>
                                {segment.interests && segment.interests.length > 0 && (
                                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 0.5 }}>
                                    {segment.interests.slice(0, 3).map((interest: string, j: number) => (
                                      <Chip key={j} label={interest} size="small" variant="outlined" sx={{ height: 18, fontSize: 10 }} />
                                    ))}
                                  </Box>
                                )}
                              </Paper>
                            </Grid>
                          ))}
                        </Grid>
                      </CardContent>
                    </Card>
                  </Grid>
                )}

                <Grid item xs={12} md={6}>
                  <Card sx={{ bgcolor: 'success.50', height: '100%' }}>
                    <CardContent>
                      <Typography variant="h6" sx={{ mb: 2 }}>✓ Сильные стороны</Typography>
                      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                        {(analysis.strengths || []).map((s: string, i: number) => (
                          <Paper key={i} sx={{ p: 1, bgcolor: 'success.50' }}>
                            <Typography variant="body2">{s}</Typography>
                          </Paper>
                        ))}
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>

                <Grid item xs={12} md={6}>
                  <Card sx={{ bgcolor: 'error.50', height: '100%' }}>
                    <CardContent>
                      <Typography variant="h6" sx={{ mb: 2 }}>✗ Слабые стороны</Typography>
                      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                        {(analysis.weaknesses || []).map((s: string, i: number) => (
                          <Paper key={i} sx={{ p: 1, bgcolor: 'error.50' }}>
                            <Typography variant="body2">{s}</Typography>
                          </Paper>
                        ))}
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>

                <Grid item xs={12} md={6}>
                  <Card sx={{ height: '100%' }}>
                    <CardContent>
                      <Typography variant="h6" sx={{ mb: 2 }}># Хэштеги</Typography>
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                        {(analysis.suggested_hashtags || []).map((h: string, i: number) => (
                          <Chip key={i} label={h} size="small" color="info" variant="outlined" />
                        ))}
                      </Box>
                      {(analysis.key_words || []).length > 0 && (
                        <>
                          <Divider sx={{ my: 1 }} />
                          <Typography variant="subtitle2" sx={{ mb: 1 }}>Ключевые слова:</Typography>
                          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                            {(analysis.key_words || []).map((w: string, i: number) => (
                              <Chip key={i} label={w} size="small" variant="outlined" />
                            ))}
                          </Box>
                        </>
                      )}
                    </CardContent>
                  </Card>
                </Grid>

                {(analysis.format_suggestions || []).length > 0 && (
                  <Grid item xs={12} md={6}>
                    <Card sx={{ bgcolor: 'info.50', height: '100%' }}>
                      <CardContent>
                        <Typography variant="h6" sx={{ mb: 2 }}>📱 Форматы</Typography>
                        {(analysis.format_suggestions || []).map((fmt: { name: string; description: string; platforms: string[] }, i: number) => (
                          <Box key={i} sx={{ mb: 1 }}>
                            <Typography variant="subtitle2">{fmt.name}</Typography>
                            <Typography variant="caption" color="text.secondary">{fmt.description}</Typography>
                          </Box>
                        ))}
                      </CardContent>
                    </Card>
                  </Grid>
                )}

                {(analysis.content_ideas || []).length > 0 && (
                  <Grid item xs={12} md={6}>
                    <Card sx={{ bgcolor: 'secondary.50', height: '100%' }}>
                      <CardContent>
                        <Typography variant="h6" sx={{ mb: 2 }}>💡 Идеи контента</Typography>
                        {(analysis.content_ideas || []).map((idea: string, i: number) => (
                          <Typography key={i} variant="body2" sx={{ mb: 1 }}>• {idea}</Typography>
                        ))}
                      </CardContent>
                    </Card>
                  </Grid>
                )}

                {(analysis.trend_alignment) && (
                  <Grid item xs={12}>
                    <Card sx={{ bgcolor: 'deepPurple.50' }}>
                      <CardContent>
                        <Typography variant="h6" sx={{ mb: 2 }}>📊 Источники данных и анализ трендов</Typography>
                        <Grid container spacing={2}>
                          <Grid item xs={12} sm={6} md={4}>
                            <Paper sx={{ p: 2, bgcolor: 'white' }}>
                              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                                <Chip label="YouTube" size="small" color="error" sx={{ mr: 1 }} />
                                <Typography variant="subtitle2">YouTube Trending</Typography>
                              </Box>
                              <Typography variant="caption" color="text.secondary">
                                Анализ популярных видео, заголовков и форматов
                              </Typography>
                            </Paper>
                          </Grid>
                          <Grid item xs={12} sm={6} md={4}>
                            <Paper sx={{ p: 2, bgcolor: 'white' }}>
                              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                                <Chip label="TikTok" size="small" color="default" sx={{ mr: 1 }} />
                                <Typography variant="subtitle2">TikTok Trends</Typography>
                              </Box>
                              <Typography variant="caption" color="text.secondary">
                                Тренды звуков, хэштегов и визуальных форматов
                              </Typography>
                            </Paper>
                          </Grid>
                          <Grid item xs={12} sm={6} md={4}>
                            <Paper sx={{ p: 2, bgcolor: 'white' }}>
                              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                                <Chip label="Reddit" size="small" color="warning" sx={{ mr: 1 }} />
                                <Typography variant="subtitle2">Reddit (r/popular)</Typography>
                              </Box>
                              <Typography variant="caption" color="text.secondary">
                                Обсуждения: r/technology, r/marketing, r/business
                              </Typography>
                            </Paper>
                          </Grid>
                          <Grid item xs={12} sm={6} md={4}>
                            <Paper sx={{ p: 2, bgcolor: 'white' }}>
                              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                                <Chip label="Google" size="small" color="info" sx={{ mr: 1 }} />
                                <Typography variant="subtitle2">Google Trends</Typography>
                              </Box>
                              <Typography variant="caption" color="text.secondary">
                                Поисковые запросы и их динамика в России
                              </Typography>
                            </Paper>
                          </Grid>
                          <Grid item xs={12} sm={6} md={4}>
                            <Paper sx={{ p: 2, bgcolor: 'white' }}>
                              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                                <Chip label="Medium" size="small" color="success" sx={{ mr: 1 }} />
                                <Typography variant="subtitle2">Medium</Typography>
                              </Box>
                              <Typography variant="caption" color="text.secondary">
                                Статьи: technology, business, marketing
                              </Typography>
                            </Paper>
                          </Grid>
                          <Grid item xs={12} sm={6} md={4}>
                            <Paper sx={{ p: 2, bgcolor: 'white' }}>
                              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                                <Chip label="HN" size="small" color="secondary" sx={{ mr: 1 }} />
                                <Typography variant="subtitle2">Hacker News</Typography>
                              </Box>
                              <Typography variant="caption" color="text.secondary">
                                Техно-тренды и стартап-сообщество
                              </Typography>
                            </Paper>
                          </Grid>
                        </Grid>
                        <Divider sx={{ my: 2 }} />
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <Chip 
                            label={`Трендовость: ${analysis.trend_alignment?.trending_score || 'средний'}`} 
                            color={analysis.trend_alignment?.trending_score === 'высокий' ? 'success' : 'default'}
                            sx={{ mr: 1 }}
                          />
                          <Typography variant="body2">
                            {analysis.trend_alignment?.alignment || 'Соответствует теме'}
                          </Typography>
                        </Box>
                        <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                          🔄 Данные обновляются автоматически при каждом анализе
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                )}
              </Grid>
            </motion.div>
          )}
        </Grid>
      </Grid>
    </Box>
  )
}
