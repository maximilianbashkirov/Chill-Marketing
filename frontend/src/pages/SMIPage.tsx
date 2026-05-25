import { useState } from 'react'
import { Box, Typography, TextField, Button, Card, CardContent, Grid, Chip, LinearProgress, Alert, Paper, Link } from '@mui/material'
import { useDispatch, useSelector } from 'react-redux'
import { startAnalysis, analysisSuccess, analysisFailure } from '@store/slices/smiSlice'
import { smiService, SMIArticle } from '@services/smiService'
import type { RootState } from '@store/store'

export default function SMIPage() {
  const dispatch = useDispatch()
  const { currentAnalysis, isLoading, error } = useSelector((state: RootState) => state.smi)
  const [topic, setTopic] = useState('')

  const handleAnalyze = async () => {
    if (!topic.trim()) return
    dispatch(startAnalysis())
    try {
      const result = await smiService.analyze({ topic })
      dispatch(analysisSuccess(result))
    } catch (err: any) {
      dispatch(analysisFailure(err.message || 'Ошибка анализа'))
    }
  }

  const analysis = currentAnalysis?.analysis

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 1, fontWeight: 700 }}>Анализ актуальности тем</Typography>
      <Typography color="text.secondary" sx={{ mb: 3 }}>Проверьте актуальность темы по базе российских СМИ</Typography>

      {isLoading && <LinearProgress sx={{ mb: 2 }} />}
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Card sx={{ position: 'sticky', top: 16 }}>
            <CardContent>
              <TextField 
                fullWidth 
                multiline 
                rows={3} 
                label="Тема статьи/новости" 
                value={topic} 
                onChange={(e) => setTopic(e.target.value)}
                sx={{ mb: 2 }} 
              />
              <Button 
                variant="contained" 
                size="large" 
                fullWidth 
                onClick={handleAnalyze}
                disabled={isLoading || !topic.trim()}
              >
                {isLoading ? 'Анализ...' : 'Найти в СМИ'}
              </Button>
              
              {analysis && (
                <Box sx={{ mt: 3 }}>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                    <Chip 
                      label={`Актуальность: ${Math.round((analysis.relevance_score || 0.5) * 100)}%`} 
                      color="primary" 
                      sx={{ justifyContent: 'flex-start' }} 
                    />
                    <Chip 
                      label={`Виральность: ${Math.round(((analysis.viral_potential as any)?.score || 0.5) * 100)}%`} 
                      color="secondary"
                      sx={{ justifyContent: 'flex-start' }} 
                    />
                    <Chip 
                      label={`Статей: ${analysis.articles_found || 0}`} 
                      color="info"
                      sx={{ justifyContent: 'flex-start' }} 
                    />
                  </Box>
                  
                  {analysis.estimated_reach && (
                    <Typography variant="body2" sx={{ mt: 2 }}>
                      Ожидаемый охват: <strong>{analysis.estimated_reach}</strong>
                    </Typography>
                  )}
                  
                  {analysis.from_cache && (
                    <Chip label="Из кэша" size="small" variant="outlined" sx={{ mt: 1 }} />
                  )}
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={8}>
          {analysis && (
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Card sx={{ height: '100%' }}>
                  <CardContent>
                    <Typography variant="h6" sx={{ mb: 1 }}>📰 Источники ({Object.keys(analysis.sources || {}).length})</Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {Object.entries(analysis.sources || {}).map(([name, count]) => (
                        <Chip key={name} label={`${name} (${count})`} size="small" variant="outlined" />
                      ))}
                    </Box>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} md={6}>
                <Card sx={{ height: '100%' }}>
                  <CardContent>
                    <Typography variant="h6" sx={{ mb: 1 }}>🎯 Площадки для публикации</Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {(analysis.best_platforms || []).map((p: string) => (
                        <Chip key={p} label={p} size="small" color="success" variant="outlined" />
                      ))}
                    </Box>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12}>
                <Card sx={{ bgcolor: 'success.50' }}>
                  <CardContent>
                    <Typography variant="h6" sx={{ mb: 1 }}>✅ Рекомендации</Typography>
                    {(analysis.recommendations || []).map((r: string, i: number) => (
                      <Typography key={i} variant="body2" sx={{ mb: 0.5 }}>• {r}</Typography>
                    ))}
                  </CardContent>
                </Card>
              </Grid>

              {(analysis.rss_articles || []).length > 0 && (
                <Grid item xs={12}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" sx={{ mb: 2 }}>
                        📰 Статьи по теме ({analysis.rss_articles.length})
                      </Typography>
                      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5, maxHeight: 500, overflow: 'auto' }}>
                        {(analysis.rss_articles as SMIArticle[]).slice(0, 20).map((article, i) => (
                          <Paper key={i} sx={{ p: 1.5, bgcolor: 'grey.50' }}>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 1 }}>
                              <Box sx={{ flex: 1 }}>
                                <Typography variant="subtitle2" sx={{ mb: 0.5 }}>{article.title}</Typography>
                                <Typography variant="caption" color="text.secondary">
                                  {article.source_name} • {article.published_at ? new Date(article.published_at).toLocaleDateString('ru-RU') : ''}
                                </Typography>
                                {article.description && (
                                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.5, fontSize: '0.75rem' }}>
                                    {article.full_text ? article.full_text.substring(0, 300) + '...' : article.description.substring(0, 150) + '...'}
                                  </Typography>
                                )}
                              </Box>
                              {article.link && (
                                <Link href={article.link} target="_blank" rel="noopener" sx={{ fontSize: '0.75rem', whiteSpace: 'nowrap' }}>
                                  Читать →
                                </Link>
                              )}
                            </Box>
                          </Paper>
                        ))}
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              )}

              {(analysis.viral_potential as any)?.similar_articles?.length > 0 && (
                <Grid item xs={12}>
                  <Card sx={{ bgcolor: 'warning.50' }}>
                    <CardContent>
                      <Typography variant="h6" sx={{ mb: 1 }}>🔥 Виральные статьи</Typography>
                      <Grid container spacing={1}>
                        {((analysis.viral_potential as any).similar_articles as Array<{title: string; source: string; url: string}>).map((a, i) => (
                          <Grid item xs={12} key={i}>
                            <Paper sx={{ p: 1, bgcolor: 'warning.100' }}>
                              <Link href={a.url || '#'} target="_blank" rel="noopener">{a.title}</Link>
                              <Typography variant="caption" color="text.secondary"> — {a.source}</Typography>
                            </Paper>
                          </Grid>
                        ))}
                      </Grid>
                    </CardContent>
                  </Card>
                </Grid>
              )}
            </Grid>
          )}
        </Grid>
      </Grid>
    </Box>
  )
}