import { useState } from 'react'
import { Box, Typography, TextField, Button, Card, CardContent, Grid, LinearProgress, Alert, Chip, Accordion, AccordionSummary, AccordionDetails, IconButton, Tooltip, Paper, Divider } from '@mui/material'
import { motion } from 'framer-motion'
import { useDispatch, useSelector } from 'react-redux'
import { startAnalysis, analysisSuccess, analysisFailure } from '@store/slices/dotAnalysisSlice'
import { dotAnalysisService } from '@services/dotAnalysisService'
import type { RootState } from '@store/store'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
import OpenInNewIcon from '@mui/icons-material/OpenInNew'
import DownloadIcon from '@mui/icons-material/Download'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import TrendingUpIcon from '@mui/icons-material/TrendingUp'
import WarningIcon from '@mui/icons-material/Warning'
import StarBorderIcon from '@mui/icons-material/StarBorder'

const SECTION_COLORS: Record<string, string> = {
  findings: '#e3f2fd',
  metrics: '#f3e5f5',
  recommendations: '#e8f5e9',
  risks: '#fce4ec',
  conclusion: '#fff3e0',
  kpi_list: '#f3e5f5',
  target_metrics: '#e8eaf6',
}

function renderMetricCard(label: string, value: any): JSX.Element {
  return (
    <Paper elevation={0} sx={{ p: 1.5, bgcolor: '#f5f5f5', borderRadius: 2, textAlign: 'center', minWidth: 100 }}>
      <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5, textTransform: 'uppercase', fontSize: 10, letterSpacing: 0.5 }}>
        {label.replace(/_/g, ' ')}
      </Typography>
      <Typography variant="h6" sx={{ fontWeight: 700, color: '#1976d2' }}>
        {value ?? '—'}
      </Typography>
    </Paper>
  )
}

function renderAnalysisValue(key: string, value: any, depth: number = 0): JSX.Element {
  if (value === null || value === undefined) return <Typography variant="body2" color="text.secondary">—</Typography>
  if (typeof value === 'boolean') return <Chip label={value ? 'Да' : 'Нет'} size="small" color={value ? 'success' : 'default'} />

  if (Array.isArray(value)) {
    if (value.length === 0) return <Typography variant="body2" color="text.secondary">—</Typography>

    // Массив объектов — рендерим каждый как карточку
    if (typeof value[0] === 'object') {
      return (
        <Grid container spacing={1.5}>
          {value.map((item, i) => (
            <Grid item xs={12} sm={6} md={4} key={i}>
              <Paper elevation={0} sx={{ p: 2, bgcolor: '#fafafa', borderRadius: 2, border: '1px solid #eee' }}>
                {Object.entries(item).map(([k, v]) => (
                  <Box key={k} sx={{ mb: 1 }}>
                    <Typography variant="caption" color="text.secondary" sx={{ display: 'block', fontSize: 10, textTransform: 'uppercase', letterSpacing: 0.5 }}>
                      {k.replace(/_/g, ' ')}
                    </Typography>
                    {renderAnalysisValue(k, v, depth + 1)}
                  </Box>
                ))}
              </Paper>
            </Grid>
          ))}
        </Grid>
      )
    }

    return (
      <Box component="ul" sx={{ m: 0, pl: 0, listStyle: 'none' }}>
        {value.map((item, i) => (
          <Typography key={i} component="li" variant="body2" sx={{ mb: 0.75, display: 'flex', alignItems: 'flex-start', gap: 1, lineHeight: 1.5 }}>
            <CheckCircleIcon sx={{ fontSize: 16, color: '#4caf50', mt: 0.3, flexShrink: 0 }} />
            <span>{item}</span>
          </Typography>
        ))}
      </Box>
    )
  }

  if (typeof value === 'object') {
    const bgColor = SECTION_COLORS[key] || 'transparent'
    return (
      <Box sx={{ pl: depth > 0 ? 2 : 0 }}>
        {Object.entries(value).map(([k, v]) => {
          const displayLabel = k.replace(/_/g, ' ')
          // Метрики — показываем как карточки
          if (['revenue', 'profit', 'aov', 'roas', 'acos', 'cac', 'ltv', 'conversion', 'cost', 'budget', 'orders', 'sales'].includes(k)) {
            return (
              <Box key={k} sx={{ display: 'inline-flex', mr: 1, mb: 1 }}>
                {renderMetricCard(displayLabel, v)}
              </Box>
            )
          }
          return (
            <Box key={k} sx={{ mb: 1.5, p: bgColor !== 'transparent' ? 1.5 : 0, bgcolor: bgColor, borderRadius: 2 }}>
              <Typography variant="caption" color="text.secondary" sx={{
                textTransform: 'uppercase', letterSpacing: 0.5, fontWeight: 600,
                display: 'flex', alignItems: 'center', gap: 0.5, mb: 0.75
              }}>
                {k === 'recommendations' ? <TrendingUpIcon sx={{ fontSize: 16 }} /> :
                 k === 'risks' ? <WarningIcon sx={{ fontSize: 16 }} /> :
                 k === 'conclusion' ? <StarBorderIcon sx={{ fontSize: 16 }} /> : null}
                {displayLabel}
              </Typography>
              {renderAnalysisValue(k, v, depth + 1)}
            </Box>
          )
        })}
      </Box>
    )
  }

  return <Typography variant="body2">{String(value)}</Typography>
}

function openFullAnalysis(modelName: string, analysis: Record<string, any>) {
  const w = window.open('', '_blank')
  if (!w) return
  const html = `<!DOCTYPE html><html lang="ru"><head><meta charset="UTF-8"><title>${modelName}</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; padding: 40px; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); color: #333; min-height: 100vh; }
  .container { max-width: 960px; margin: 0 auto; }
  h1 { font-size: 32px; margin-bottom: 4px; background: linear-gradient(135deg, #1976d2, #42a5f5); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
  .meta { color: #666; font-size: 14px; margin-bottom: 32px; }
  .section { background: white; border-radius: 12px; padding: 24px; margin-bottom: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); border-left: 4px solid #1976d2; transition: transform 0.2s; }
  .section:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0,0,0,0.12); }
  .section h2 { font-size: 18px; margin-bottom: 16px; color: #1976d2; display: flex; align-items: center; gap: 8px; padding-bottom: 10px; border-bottom: 2px solid #e3f2fd; }
  ul { padding-left: 24px; }
  li { margin-bottom: 8px; line-height: 1.6; }
  li::marker { color: #1976d2; }
  p { line-height: 1.7; margin-bottom: 8px; }
  .label { font-size: 11px; text-transform: uppercase; letter-spacing: 0.8px; color: #888; font-weight: 700; margin-bottom: 6px; }
  .sub { margin-left: 16px; margin-top: 10px; padding-left: 16px; border-left: 3px solid #e3f2fd; }
  .metric-row { display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 16px; }
  .metric-card { background: linear-gradient(135deg, #e3f2fd, #bbdefb); border-radius: 10px; padding: 14px 20px; text-align: center; min-width: 110px; flex: 1; }
  .metric-card .val { font-size: 24px; font-weight: 700; color: #1565c0; }
  .metric-card .lbl { font-size: 10px; text-transform: uppercase; letter-spacing: 0.5px; color: #666; margin-top: 4px; }
  .recommendation { background: #e8f5e9; border-left-color: #4caf50; }
  .risk { background: #fce4ec; border-left-color: #f44336; }
  .conclusion { background: linear-gradient(135deg, #fff3e0, #ffe0b2); border-left-color: #ff9800; }
  .tag { display: inline-block; background: #e3f2fd; color: #1976d2; border-radius: 12px; padding: 2px 10px; font-size: 11px; font-weight: 600; margin-right: 4px; text-transform: uppercase; }
  hr { border: none; border-top: 1px solid #eee; margin: 16px 0; }
</style></head><body>
<div class="container">
<h1>${escapeHtml(modelName)}</h1>
<div class="meta">Полный анализ</div>
${renderFullAnalysisHTML(analysis)}
</div>
</body></html>`
  w.document.write(html)
  w.document.close()
}

function escapeHtml(s: string): string {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;')
}

function renderMetricHTML(label: string, value: any): string {
  return `<div class="metric-card"><div class="val">${escapeHtml(String(value ?? '—'))}</div><div class="lbl">${escapeHtml(label.replace(/_/g, ' '))}</div></div>`
}

function renderFullAnalysisHTML(value: any): string {
  if (!value || typeof value === 'string') return `<p>${escapeHtml(value || '—')}</p>`
  if (Array.isArray(value)) {
    if (value.length === 0) return '<p>—</p>'
    // Object arrays
    if (typeof value[0] === 'object') {
      return '<div style="display:flex;flex-wrap:wrap;gap:12px">' + value.map(item => {
        if (typeof item === 'object') {
          let card = '<div style="background:#fafafa;border-radius:10px;padding:16px;flex:1;min-width:200px;border:1px solid #eee">'
          for (const [k, v] of Object.entries(item)) {
            card += `<div class="label">${escapeHtml(k.replace(/_/g, ' '))}</div><p>${escapeHtml(String(v ?? '—'))}</p>`
          }
          card += '</div>'
          return card
        }
        return `<li>${escapeHtml(String(item))}</li>`
      }).join('') + '</div>'
    }
    return '<ul>' + value.map(item => `<li>${typeof item === 'object' ? renderFullAnalysisHTML(item) : escapeHtml(String(item))}</li>`).join('') + '</ul>'
  }
  if (typeof value === 'object') {
    let html = ''
    for (const [key, val] of Object.entries(value)) {
      if (key.startsWith('_')) continue
      const displayKey = key.replace(/_/g, ' ')
      let extraClass = ''
      if (key === 'recommendations') extraClass = ' recommendation'
      else if (key === 'risks') extraClass = ' risk'
      else if (key === 'conclusion') extraClass = ' conclusion'

      // Metric-style rendering for numeric values
      const metricKeys = ['revenue', 'profit', 'aov', 'roas', 'acos', 'cac', 'ltv', 'conversion', 'cost', 'budget', 'orders', 'sales', 'commission', 'profitability']
      if (typeof val === 'number' && metricKeys.includes(key)) {
        html += renderMetricHTML(displayKey, val)
        continue
      }

      html += `<div class="section${extraClass}"><h2>${displayKey}</h2>${renderFullAnalysisHTML(val)}</div>`
    }
    return html
  }
  return `<p>${escapeHtml(String(value))}</p>`
}

function triggerDownload(content: string, filename: string, mime: string) {
  const blob = new Blob([content], { type: mime })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

function buildFullHTML(modelName: string, analysis: Record<string, any>): string {
  const content = renderFullAnalysisHTML(analysis)
  return `<!DOCTYPE html><html lang="ru"><head><meta charset="UTF-8"><title>${escapeHtml(modelName)}</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; padding: 40px; background: #f5f5f5; color: #333; }
  .container { max-width: 960px; margin: 0 auto; }
  h1 { font-size: 28px; margin-bottom: 16px; color: #1976d2; }
  .section { background: white; border-radius: 8px; padding: 20px 24px; margin-bottom: 16px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); border-left: 4px solid #1976d2; }
  .section h2 { font-size: 18px; color: #1976d2; margin-bottom: 12px; border-bottom: 1px solid #e3f2fd; padding-bottom: 8px; }
  .recommendation { border-left-color: #4caf50; }
  .risk { border-left-color: #f44336; }
  .conclusion { border-left-color: #ff9800; }
  ul { padding-left: 20px; } li { margin-bottom: 6px; line-height: 1.5; }
  .label { font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; color: #888; font-weight: 600; margin-bottom: 4px; }
  p { line-height: 1.6; margin-bottom: 8px; }
  .metric-card { display: inline-block; background: #e3f2fd; border-radius: 8px; padding: 10px 16px; margin: 4px; text-align: center; }
  .metric-card .val { font-size: 20px; font-weight: 700; color: #1565c0; }
  .metric-card .lbl { font-size: 10px; text-transform: uppercase; color: #666; }
  hr { border: none; border-top: 1px solid #eee; margin: 12px 0; }
</style></head><body>
<div class="container">
<h1>${escapeHtml(modelName)}</h1>
${content}
</div>
</body></html>`
}

function downloadHTML(modelName: string, analysis: Record<string, any>) {
  const html = buildFullHTML(modelName, analysis)
  triggerDownload(html, `${modelName.replace(/\s+/g, '_')}.html`, 'text/html')
}

function downloadDOC(modelName: string, analysis: Record<string, any>) {
  const html = buildFullHTML(modelName, analysis)
  triggerDownload(html, `${modelName.replace(/\s+/g, '_')}.doc`, 'application/msword')
}

function downloadCSV(modelName: string, analysis: Record<string, any>) {
  const rows: string[][] = [['Раздел', 'Ключ', 'Значение']]

  function flatten(obj: any, section: string, prefix: string = '') {
    if (obj === null || obj === undefined) return
    if (typeof obj === 'object') {
      if (Array.isArray(obj)) {
        obj.forEach((item, idx) => {
          if (typeof item === 'object' && item !== null) {
            flatten(item, section, `${prefix}[${idx}]`)
          } else {
            rows.push([section, `${prefix}[${idx}]`, String(item)])
          }
        })
      } else {
        for (const [k, v] of Object.entries(obj)) {
          if (k.startsWith('_')) continue
          const fullKey = prefix ? `${prefix}.${k}` : k
          if (typeof v === 'object' && v !== null) {
            flatten(v, section, fullKey)
          } else {
            rows.push([section, fullKey.replace(/_/g, ' '), String(v ?? '')])
          }
        }
      }
    } else {
      rows.push([section, prefix, String(obj)])
    }
  }

  for (const [key, value] of Object.entries(analysis)) {
    if (key.startsWith('_')) continue
    flatten(value, key.replace(/_/g, ' '))
  }

  const csv = rows.map(r => r.map(c => `"${c.replace(/"/g, '""')}"`).join(',')).join('\n')
  triggerDownload(csv, `${modelName.replace(/\s+/g, '_')}.csv`, 'text/csv;charset=utf-8;')
}

export default function DotAnalysisPage() {
  const dispatch = useDispatch()
  const { currentAnalysis, isLoading, error } = useSelector((state: RootState) => state.dotAnalysis)
  const [caseDescription, setCaseDescription] = useState('')
  const [industry, setIndustry] = useState('')

  const handleAnalyze = async () => {
    if (!caseDescription.trim()) return
    dispatch(startAnalysis())
    try {
      const result = await dotAnalysisService.analyze({ caseDescription, industry })
      dispatch(analysisSuccess(result))
    } catch (err: any) {
      dispatch(analysisFailure(err.message || 'Ошибка анализа'))
    }
  }

  const raw = currentAnalysis
  const data = raw?.data?.data || raw?.data || raw || {}
  const analyses: any[] = data.analyses || []
  const selectedModels: any[] = data.selected_models || []
  const [expanded, setExpanded] = useState<string | false>(false)

  const handleAccordion = (panel: string) => (_: any, isExpanded: boolean) => {
    setExpanded(isExpanded ? panel : false)
  }

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 1, fontWeight: 700 }}>Dot Analysis</Typography>
      <Typography color="text.secondary" sx={{ mb: 4 }}>Подбор и применение маркетинговых фреймворков — из 130+ возможных под ваш кейс</Typography>

      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <TextField fullWidth multiline rows={5} label="Опишите ваш кейс" value={caseDescription} onChange={(e) => setCaseDescription(e.target.value)} sx={{ mb: 2 }} placeholder="Например: закупаю рекламу у блогеров для продажи нижнего белья через Ozon. Бюджет 300к, нужно понять какие каналы эффективнее и как масштабироваться..." />
              <TextField fullWidth label="Индустрия" value={industry} onChange={(e) => setIndustry(e.target.value)} sx={{ mb: 2 }} placeholder="селлеры Ozon, e-commerce, инфлюенс-маркетинг" />
              <Button variant="contained" size="large" fullWidth onClick={handleAnalyze} disabled={isLoading || !caseDescription.trim()}>
                {isLoading ? 'Анализирую...' : 'Подобрать и применить фреймворки'}
              </Button>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12}>
          {isLoading && <LinearProgress sx={{ mb: 2 }} />}
          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

          {analyses.length > 0 && (
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
              <Card sx={{ mb: 3, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
                <CardContent>
                  <Typography variant="h6" sx={{ mb: 2, fontWeight: 600, color: 'white' }}>Выбранные фреймворки</Typography>
                  <Grid container spacing={1.5}>
                    {selectedModels.map((m: any, i: number) => (
                      <Grid item xs={12} sm={6} md={3} key={i}>
                        <Paper elevation={0} sx={{ p: 1.5, bgcolor: 'rgba(255,255,255,0.15)', backdropFilter: 'blur(10px)', borderRadius: 2, height: '100%', border: '1px solid rgba(255,255,255,0.2)' }}>
                          <Chip label={m.category || 'Анализ'} size="small" sx={{ mb: 0.5, bgcolor: 'rgba(255,255,255,0.25)', color: 'white', fontWeight: 600 }} />
                          <Typography variant="subtitle2" sx={{ fontWeight: 600, color: 'white' }}>{m.name}</Typography>
                          <Typography variant="caption" sx={{ display: 'block', mt: 0.5, color: 'rgba(255,255,255,0.75)', lineHeight: 1.4 }}>{m.reason?.slice(0, 150)}</Typography>
                        </Paper>
                      </Grid>
                    ))}
                  </Grid>
                </CardContent>
              </Card>

              {analyses.map((a: any, i: number) => {
                const analysis = a.analysis || {}
                const isFallback = analysis._fallback === true
                const hasContent = Object.keys(analysis).length > 0

                return (
                  <Card key={i} sx={{ mb: 2, overflow: 'visible' }}>
                    <Accordion
                      expanded={expanded === `panel${i}`}
                      onChange={handleAccordion(`panel${i}`)}
                      sx={{ boxShadow: 'none', '&:before': { display: 'none' } }}
                    >
                      <AccordionSummary expandIcon={<ExpandMoreIcon />} sx={{ bgcolor: hasContent ? 'white' : '#f5f5f5', borderRadius: 1 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, width: '100%', pr: 2 }}>
                          <Chip label={a.category || 'Анализ'} size="small" color="primary" variant="outlined" />
                          <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>{a.name}</Typography>
                          {isFallback && (
                            <Chip label="На основе шаблона" size="small" color="warning" variant="outlined" sx={{ fontSize: 10 }} />
                          )}
                          <Box sx={{ flexGrow: 1 }} />
                          <Tooltip title="Открыть полный анализ в новой вкладке">
                            <IconButton
                              size="small"
                              onClick={(e) => {
                                e.stopPropagation()
                                openFullAnalysis(a.name, analysis)
                              }}
                            >
                              <OpenInNewIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </Box>
                      </AccordionSummary>
                      <AccordionDetails sx={{ pt: 2 }}>
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 1, fontStyle: 'italic' }}>{a.description}</Typography>
                        <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
                          <Button size="small" variant="outlined" startIcon={<DownloadIcon />}
                            onClick={(e) => { e.stopPropagation(); downloadHTML(a.name, analysis) }}>
                            HTML
                          </Button>
                          <Button size="small" variant="outlined"
                            onClick={(e) => { e.stopPropagation(); downloadDOC(a.name, analysis) }}>
                            DOC
                          </Button>
                          <Button size="small" variant="outlined"
                            onClick={(e) => { e.stopPropagation(); downloadCSV(a.name, analysis) }}>
                            CSV
                          </Button>
                        </Box>
                        <Divider sx={{ mb: 2 }} />

                        {hasContent ? (
                          Object.entries(analysis).map(([key, value]) => {
                            if (key.startsWith('_')) return null
                            return (
                              <Box key={key} sx={{ mb: 2.5, p: 1.5, bgcolor: SECTION_COLORS[key] || '#fafafa', borderRadius: 2 }}>
                                {renderAnalysisValue(key, value)}
                              </Box>
                            )
                          })
                        ) : (
                          <Typography variant="body2" color="text.secondary">Нет данных для отображения</Typography>
                        )}
                      </AccordionDetails>
                    </Accordion>
                  </Card>
                )
              })}
            </motion.div>
          )}
        </Grid>
      </Grid>
    </Box>
  )
}