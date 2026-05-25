function download(filename: string, content: string, mime: string) {
  const blob = new Blob([content], { type: mime })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url; a.download = filename
  document.body.appendChild(a); a.click()
  document.body.removeChild(a); a.remove()
  URL.revokeObjectURL(url)
}

function pick(o: any, ...paths: string[]): any {
  for (const p of paths) {
    const v = p.split('.').reduce((acc, k) => acc?.[k], o)
    if (v != null) return v
  }
  return undefined
}

function sections(data: any): { title: string; body: string }[] {
  const r = pick(data, 'research', 'data.research') || data || {}
  const out: { title: string; body: string }[] = []

  if (r.overview) out.push({ title: 'Обзор', body: r.overview })

  if (r.statistics?.length) {
    out.push({
      title: 'Статистика',
      body: r.statistics.map((s: any) => `${s.metric}: ${s.value} (${s.source}, ${s.year})`).join('\n'),
    })
  }

  if (r.cases?.length) {
    out.push({
      title: 'Кейсы',
      body: r.cases.map((c: any) => {
        let t = `Компания: ${c.company}`
        if (c.description) t += `\n${c.description}`
        if (c.results) t += `\nРезультат: ${c.results}`
        if (c.source) t += `\nИсточник: ${c.source}`
        return t
      }).join('\n---\n'),
    })
  }

  if (r.strategies?.length) {
    out.push({
      title: 'Стратегии',
      body: r.strategies.join('\n---\n'),
    })
  }

  if (r.examples?.length) {
    out.push({
      title: 'Примеры из практики',
      body: r.examples.map((e: any) => {
        let t = e.title || ''
        if (e.context) t += `\nКонтекст: ${e.context}`
        if (e.description) t += `\n${e.description}`
        if (e.outcome) t += `\nРезультат: ${e.outcome}`
        if (e.source) t += `\nИсточник: ${e.source}`
        return t
      }).join('\n---\n'),
    })
  }

  if (r.trends?.length) {
    out.push({ title: 'Тренды', body: r.trends.join('\n') })
  }

  if (r.competitive_map?.length) {
    out.push({
      title: 'Конкурентная карта',
      body: r.competitive_map.map((c: any) => {
        let t = `Компания: ${c.company}`
        if (c.market_share) t += `\nДоля рынка: ${c.market_share}`
        if (c.specialization) t += `\nСпециализация: ${c.specialization}`
        if (c.strengths?.length) t += `\nСильные стороны: ${c.strengths.join(', ')}`
        if (c.weaknesses?.length) t += `\nСлабые стороны: ${c.weaknesses.join(', ')}`
        if (c.products?.length) t += `\nПродукты: ${c.products.join(', ')}`
        return t
      }).join('\n---\n'),
    })
  }

  if (r.tech_stack) {
    const t = r.tech_stack
    const parts: string[] = []
    if (t.main_technologies?.length) parts.push(`Основные технологии: ${t.main_technologies.join(', ')}`)
    if (t.popular_tools?.length) parts.push(`Популярные инструменты: ${t.popular_tools.join(', ')}`)
    if (t.emerging_tech?.length) parts.push(`Новые технологии: ${t.emerging_tech.join(', ')}`)
    if (t.typical_stack) parts.push(`Типичный стек: ${t.typical_stack}`)
    if (parts.length) out.push({ title: 'Технологический стек', body: parts.join('\n') })
  }

  if (r.regulatory_risks?.length) {
    out.push({
      title: 'Регуляторные риски',
      body: r.regulatory_risks.map((rr: any) => {
        let t = rr.risk || ''
        if (rr.description) t += `\n${rr.description}`
        if (rr.jurisdiction) t += `\nЮрисдикция: ${rr.jurisdiction}`
        if (rr.mitigation) t += `\nСмягчение: ${rr.mitigation}`
        return t
      }).join('\n---\n'),
    })
  }

  if (r.investment_landscape) {
    const il = r.investment_landscape
    const parts: string[] = []
    if (il.total_funding) parts.push(`Всего инвестиций: ${il.total_funding}`)
    if (il.notable_startups?.length) parts.push(`Стартапы: ${il.notable_startups.join('; ')}`)
    if (il.key_investors?.length) parts.push(`Инвесторы: ${il.key_investors.join(', ')}`)
    if (il.recent_deals?.length) parts.push(`Последние сделки: ${il.recent_deals.join('; ')}`)
    if (parts.length) out.push({ title: 'Инвестиционный ландшафт', body: parts.join('\n') })
  }

  if (r.pricing_analysis) {
    const pa = r.pricing_analysis
    const parts: string[] = []
    if (pa.models?.length) parts.push(`Модели:\n  ${pa.models.join('\n  ')}`)
    if (pa.typical_range) parts.push(`Типичный диапазон: ${pa.typical_range}`)
    if (pa.freemium_prevalence) parts.push(`Freemium: ${pa.freemium_prevalence}`)
    if (pa.enterprise_pricing) parts.push(`Enterprise: ${pa.enterprise_pricing}`)
    if (parts.length) out.push({ title: 'Ценовой анализ', body: parts.join('\n') })
  }

  if (r.forecast) {
    const f = r.forecast
    const parts: string[] = []
    if (f.short_term_1year) parts.push(`1 год: ${f.short_term_1year}`)
    if (f.medium_term_3year) parts.push(`3 года: ${f.medium_term_3year}`)
    if (f.long_term_5year) parts.push(`5 лет: ${f.long_term_5year}`)
    if (f.key_drivers?.length) parts.push(`Драйверы роста: ${f.key_drivers.join(', ')}`)
    if (f.key_barriers?.length) parts.push(`Барьеры: ${f.key_barriers.join(', ')}`)
    if (parts.length) out.push({ title: 'Прогноз 3-5 лет', body: parts.join('\n') })
  }

  if (r.key_metrics) {
    const km = r.key_metrics
    const parts: string[] = []
    const labels: Record<string, string> = {
      average_cac: 'CAC', average_ltv: 'LTV', ltv_cac_ratio: 'LTV/CAC',
      conversion_rate: 'Конверсия', retention_rate: 'Retention', churn_rate: 'Отток',
    }
    for (const [k, label] of Object.entries(labels)) {
      const v = (km as any)[k]
      if (v) parts.push(`${label}: ${v}`)
    }
    if (parts.length) out.push({ title: 'Ключевые метрики', body: parts.join('\n') })
  }

  if (r.sources?.length) {
    out.push({ title: 'Источники', body: r.sources.join('\n') })
  }

  return out
}

function escapeCSV(v: any): string {
  const s = String(v ?? '')
  return s.includes(',') || s.includes('"') || s.includes('\n') ? `"${s.replace(/"/g, '""')}"` : s
}

export function exportHTML(data: any, topic: string) {
  const secs = sections(data)
  const rows = secs.map(s => `
    <div style="margin-bottom:24px">
      <h2 style="color:#6366f1;margin:0 0 8px">${s.title}</h2>
      <div style="white-space:pre-wrap;line-height:1.6">${s.body}</div>
    </div>`).join('')

  download(
    `research-${topic}.html`,
    `<!DOCTYPE html><html lang="ru"><head><meta charset="UTF-8">
      <title>Исследование: ${topic}</title>
      <style>body{font-family:Inter,sans-serif;max-width:800px;margin:40px auto;padding:0 20px;color:#1e293b}
      h1{color:#4f46e5;border-bottom:2px solid #e2e8f0;padding-bottom:12px}</style>
    </head><body>
      <h1>Маркетинговое исследование: ${topic}</h1>
      ${rows}
    </body></html>`,
    'text/html',
  )
}

export function exportCSV(data: any, topic: string) {
  const secs = sections(data)
  const csv = secs.map(s => {
    const lines = s.body.split('\n').map(l => escapeCSV(l))
    return [`"${s.title}"`, ...lines].join('\n')
  }).join('\n\n')

  download(`research-${topic}.csv`, '\uFEFF' + csv, 'text/csv;charset=utf-8')
}

export function exportXLSX(data: any, topic: string) {
  const secs = sections(data)
  const rows = secs.flatMap(s => [
    [`[${s.title}]`, '', '', ''],
    ...s.body.split('\n').map(l => [l, '', '', '']),
    ['', '', '', ''],
  ])

  const table = rows.map(r => `<tr>${r.map(c => `<td>${escapeCSV(c)}</td>`).join('')}</tr>`).join('')
  const html = `<html xmlns:o="urn:schemas-microsoft-com:office:office"
    xmlns:x="urn:schemas-microsoft-com:office:excel"><head><meta charset="UTF-8">
    <style>td{mso-number-format:"\\@";padding:4px 8px}</style>
  </head><body><table>${table}</table></body></html>`

  download(`research-${topic}.xls`, html, 'application/vnd.ms-excel')
}

export function exportDOC(data: any, topic: string) {
  const secs = sections(data)
  const rows = secs.map(s => `
    <h2 style="color:#6366f1">${s.title}</h2>
    <p style="white-space:pre-wrap;line-height:1.6">${s.body.replace(/\n/g, '<br>')}</p>
  `).join('')

  download(
    `research-${topic}.doc`,
    `<!DOCTYPE html><html lang="ru"><head><meta charset="UTF-8">
      <title>Исследование: ${topic}</title>
      <style>body{font-family:Inter,sans-serif;max-width:800px;margin:40px auto;color:#1e293b}
      h1{color:#4f46e5;border-bottom:2px solid #e2e8f0}</style>
    </head><body>
      <h1>Маркетинговое исследование: ${topic}</h1>
      ${rows}
    </body></html>`,
    'application/msword',
  )
}
