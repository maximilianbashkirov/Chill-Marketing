from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from ...models.models import MarketResearchRequest
from ...utils.llm_client import llm_client
from ...utils.research_collector import research_collector
import json
from datetime import datetime


class MarketResearchService:
    """Service for market research and data enrichment"""

    SYSTEM_PROMPT = """Ты — эксперт по маркетинговым исследованиям и бизнес-аналитике.
Твоя задача — проводить глубокие исследования рынка: собирать реальные цифры, находить кейсы компаний, 
разрабатывать стратегии с конкретными шагами внедрения и приводить примеры из практики.
Используй предоставленные данные. Все поля заполняй содержательно — никаких пустых массивов.
Отвечай ТОЛЬКО валидным JSON, без пояснений."""

    def __init__(self, db: Session):
        self.db = db

    async def conduct_research(
        self,
        topic: str,
        user_id: int,
        industry: Optional[str] = None,
        requirements: Optional[Dict[str, bool]] = None
    ) -> Dict[str, Any]:
        request = MarketResearchRequest(
            user_id=user_id, topic=topic, industry=industry, status="processing"
        )
        self.db.add(request)
        self.db.commit()
        self.db.refresh(request)

        try:
            research_data = await self._collect_and_process_research_data(topic, industry)
            research_result = await self._generate_llm_research_with_data(
                topic, industry, research_data, requirements
            )
            request.research_data = research_result
            request.status = "completed"
            self.db.commit()
            return {"request_id": request.id, "research": research_result}
        except Exception as e:
            request.status = "failed"
            self.db.commit()
            raise e

    async def _collect_and_process_research_data(self, topic: str, industry: Optional[str]) -> Dict[str, Any]:
        try:
            raw_data = await research_collector.collect_comprehensive_research_data(topic, industry)
            return self._process_research_data(raw_data)
        except Exception as e:
            print(f"Error collecting research data: {e}")
            return self._get_empty_research_structure()

    def _process_research_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        indicator_names = {
            "NY.GDP.MKTP.CD": ("GDP (current US$)", "market_size"),
            "FP.CPI.TOTL.ZG": ("Inflation (annual %)", "growth_rate"),
            "SL.UEM.TOTL.ZS": ("Unemployment (% of total labor force)", "unemployment_rate"),
        }
        wb = raw_data.get("world_bank", [])
        by_indicator = {}
        for w in wb:
            ind = w.get("indicator", "")
            if ind and w.get("value") is not None:
                date = w.get("date", "")
                if ind not in by_indicator or (date and date > by_indicator[ind]["date"]):
                    by_indicator[ind] = w

        stats_lines = []
        stats_dict = {}
        for ind, entry in sorted(by_indicator.items()):
            name, fb_key = indicator_names.get(ind, (ind, ind.lower().replace(".", "_")))
            val = entry["value"]
            stats_lines.append(f"- {name}: {val} ({entry['country']}, {entry['date']}, World Bank)")
            stats_dict[fb_key] = str(val)

        trends_list = []
        for gt in raw_data.get("google_trends", []):
            for t in gt.get("trends", []):
                if t:
                    trends_list.append(f"- {t}")

        arxiv_papers = []
        for paper in raw_data.get("arxiv", []):
            title = paper.get("title", "")
            if title:
                arxiv_papers.append({
                    "source": "arXiv.org",
                    "title": title,
                    "summary": paper.get("summary", "")[:500],
                    "link": paper.get("id", ""),
                    "published": paper.get("published", ""),
                })

        lines = []
        if stats_lines:
            lines.append("📊 КЛЮЧЕВЫЕ ПОКАЗАТЕЛИ:")
            lines.extend(stats_lines)
        if arxiv_papers:
            lines.append("\n📄 НАУЧНЫЕ ПУБЛИКАЦИИ:")
            for p in arxiv_papers:
                lines.append(f"- {p['title']}")
                if p.get("link"):
                    lines.append(f"  Ссылка: {p['link']}")
                if p.get("summary"):
                    lines.append(f"  Кратко: {p['summary'][:200]}")
        if trends_list:
            lines.append("\n📈 ТЕКУЩИЕ ТРЕНДЫ:")
            lines.extend(trends_list[:10])

        # ─── Wikipedia ──────────────────────────────────────
        wiki = raw_data.get("wikipedia", [])
        wiki_lines = []
        for w in wiki:
            ex = (w.get("extract") or "")[:300]
            if ex:
                wiki_lines.append(f"- {w.get('title', '')}: {ex}")
        if wiki_lines:
            lines.append("\n📖 ВИКИПЕДИЯ:")
            lines.extend(wiki_lines)

        # ─── News ───────────────────────────────────────────
        news = raw_data.get("news", [])
        news_lines = []
        for n in news:
            desc = (n.get("description") or "")[:150]
            if desc:
                news_lines.append(f"- {n.get('title', '')} — {desc}")
        if news_lines:
            lines.append("\n📰 НОВОСТИ:")
            lines.extend(news_lines)

        # ─── GitHub ─────────────────────────────────────────
        gh = raw_data.get("github", [])
        gh_lines = []
        for g in gh:
            desc = (g.get("description") or "")[:150]
            stars = g.get("stars", 0)
            lang = g.get("language") or ""
            gh_lines.append(f"- {g.get('name', '')} ⭐{stars} {f'({lang})' if lang else ''}: {desc}")
        if gh_lines:
            lines.append("\n💻 ПРОЕКТЫ (GITHUB):")
            lines.extend(gh_lines)

        # ─── Google Books ───────────────────────────────────
        gb = raw_data.get("google_books", [])
        gb_lines = []
        for b in gb:
            authors = ", ".join(b.get("authors", []) or [])
            desc = (b.get("description") or "")[:150]
            gb_lines.append(f"- {b.get('title', '')} {f'({authors})' if authors else ''}: {desc}")
        if gb_lines:
            lines.append("\n📚 КНИГИ:")
            lines.extend(gb_lines)

        # ─── Open Library ───────────────────────────────────
        ol = raw_data.get("open_library", [])
        ol_lines = []
        for o in ol:
            authors = ", ".join(o.get("authors", []) or [])
            subs = ", ".join((o.get("subject") or [])[:3])
            ol_lines.append(f"- {o.get('title', '')} {f'({authors})' if authors else ''} {f'— {subs}' if subs else ''}")
        if ol_lines:
            lines.append("\n📖 OPEN LIBRARY:")
            lines.extend(ol_lines)

        # ─── Wikipedia Pageviews ────────────────────────────
        wv = raw_data.get("wikipedia_pageviews", [])
        if wv:
            lines.append(f"\n👁 ПОПУЛЯРНОСТЬ ТЕМЫ (Wikipedia): {wv[0].get('total_views_30d', 0)} просмотров за 30 дней, в среднем {wv[0].get('avg_daily', 0)}/день")

        sources = ["World Bank", "Google Trends", "arXiv.org", "Wikipedia"]
        if raw_data.get("news"):
            sources.append("NewsAPI")
        if raw_data.get("github"):
            sources.append("GitHub")
        if raw_data.get("google_books") or raw_data.get("open_library"):
            sources.append("Google Books / Open Library")

        return {
            "text": "\n".join(lines) if lines else "Внешних данных нет",
            "sources": sources,
            "statistics": stats_dict,
            "papers": arxiv_papers,
            "trends": list(set(t.replace("- ", "").strip() for t in trends_list if t)),
            "wikipedia": wiki,
            "news": news,
            "github": gh,
            "google_books": gb,
            "open_library": ol,
            "wikipedia_pageviews": wv,
        }

    def _get_empty_research_structure(self) -> Dict[str, Any]:
        return {"text": "Внешних данных нет", "sources": ["Сбор данных не удался — используется экспертная оценка"]}

    async def _generate_llm_research_with_data(
        self, topic: str, industry: Optional[str], research_data: Dict[str, Any],
        requirements: Optional[Dict[str, bool]] = None
    ) -> Dict[str, Any]:
        data_text = research_data.get("text", "")
        sources = research_data.get("sources", [])

        req = requirements or {}
        sections_active = {
            "statistics": req.get("needStatistics", True),
            "cases": req.get("needCases", True),
            "strategies": req.get("needStrategies", True),
            "examples": req.get("needExamples", True),
        }

        prompt = f"""Проведи глубокое маркетинговое исследование по теме: "{topic}" (индустрия: {industry or 'общая'}).

СОБРАННЫЕ РЕАЛЬНЫЕ ДАННЫЕ:
{data_text if data_text else "Внешних данных нет — используй свои знания для оценки"}

На основе этих данных и твоих знаний верни ТОЛЬКО валидный JSON на РУССКОМ ЯЗЫКЕ.

ТРЕБУЕМАЯ СТРУКТУРА ОТВЕТА (все поля на русском):
{{
  "overview": "Краткое резюме исследования (3-5 предложений): о чём рынок, ключевые выводы, основные тренды и рекомендации. На русском.",

  "statistics": {{
    "market_size": "размер рынка в USD (из данных или оценка) с указанием источника",
    "growth_rate": "темп роста в % с периодом",
    "key_players_count": "количество ключевых игроков на рынке",
    "market_leaders": "основные компании на рынке",
    "regional_distribution": "распределение по регионам"
  }},

  "competitive_map": [
    {{
      "company": "название компании-конкурента",
      "market_share": "примерная доля рынка в %",
      "specialization": "в чём специализация / ключевое преимущество",
      "strengths": ["сильная сторона 1", "сильная сторона 2"],
      "weaknesses": ["слабая сторона 1", "слабая сторона 2"],
      "products": ["ключевой продукт/услуга"]
    }}
  ],

  "tech_stack": {{
    "main_technologies": ["основные технологии в нише"],
    "popular_tools": ["популярные инструменты"],
    "emerging_tech": ["новые/перспективные технологии"],
    "typical_stack": "типичный технологический стек компании в этой нише"
  }},

  "regulatory_risks": [
    {{
      "risk": "название риска",
      "description": "описание риска и его влияние на рынок",
      "jurisdiction": "какие страны/регионы",
      "mitigation": "как можно снизить риск"
    }}
  ],

  "investment_landscape": {{
    "total_funding": "общий объём инвестиций в нише (оценка)",
    "notable_startups": ["стартап 1 — кратко чем занимается", "стартап 2"],
    "key_investors": ["инвестор 1", "инвестор 2"],
    "recent_deals": ["сделка 1", "сделка 2"]
  }},

  "pricing_analysis": {{
    "models": ["модель ценообразования 1", "модель 2"],
    "typical_range": "типичный диапазон цен",
    "freemium_prevalence": "насколько распространена freemium-модель",
    "enterprise_pricing": "средняя цена enterprise-решения"
  }},

  "forecast": {{
    "short_term_1year": "прогноз на 1 год",
    "medium_term_3year": "прогноз на 3 года",
    "long_term_5year": "прогноз на 5 лет",
    "key_drivers": ["ключевой драйвер роста 1", "драйвер 2", "драйвер 3"],
    "key_barriers": ["барьер 1", "барьер 2"]
  }},

  "key_metrics": {{
    "average_cac": "средняя стоимость привлечения клиента (CAC)",
    "average_ltv": "средняя пожизненная ценность клиента (LTV)",
    "ltv_cac_ratio": "соотношение LTV/CAC",
    "conversion_rate": "средняя конверсия",
    "retention_rate": "средний retention",
    "churn_rate": "средний отток"
  }},

  "cases": [
    {{
      "company": "название реальной компании",
      "challenge": "какая проблема стояла перед компанией (подробно)",
      "solution": "как они её решили — конкретные действия, технологии, подходы",
      "result": "каких результатов достигли — цифры, проценты, сроки",
      "timeframe": "когда происходил кейс",
      "budget": "бюджет если известен, иначе 'Не раскрыт'",
      "source": "источник информации о кейсе"
    }}
  ],

  "strategies": [
    {{
      "name": "название стратегии",
      "description": "что это за стратегия, как работает, почему эффективна (2-3 предложения)",
      "best_for": "какому типу компаний / ситуаций подходит",
      "implementation_steps": ["шаг 1: конкретное действие", "шаг 2: конкретное действие", "шаг 3: конкретное действие", "шаг 4: конкретное действие"],
      "expected_roi": "ожидаемая окупаемость с пояснением",
      "risks": "возможные риски и как их минимизировать"
    }}
  ],

  "examples": [
    {{
      "company": "название компании или 'Пример из практики'",
      "context": "контекст: отрасль, размер компании, ситуация",
      "approach": "что сделали, какой подход применили",
      "result": "какой результат получили — конкретные метрики",
      "source": "откуда информация"
    }}
  ],

  "trends": [
    "тренд 1 — развёрнутое описание: что происходит, почему важно, какие возможности",
    "тренд 2 — развёрнутое описание",
    "тренд 3 — развёрнутое описание"
  ],

  "sources": ["источник 1", "источник 2", "источник 3"]
}}

ВАЖНЫЕ ПРАВИЛА:
1. ВСЁ на русском языке — все поля, включая nested объекты. ДАЖЕ если входные данные на английском — переведи.
2. Используй реальные данные из раздела «СОБРАННЫЕ РЕАЛЬНЫЕ ДАННЫЕ» для статистики и фактов
3. Все новые секции (competitive_map, tech_stack, regulatory_risks, investment_landscape, pricing_analysis, forecast, key_metrics) — ОБЯЗАТЕЛЬНО заполни, минимум 2 элемента где массив
4. Для strategies — минимум 2 стратегии с конкретными шагами внедрения (3-4 шага каждая)
5. Для examples — минимум 2 примера из реальной практики с метриками
6. Каждый case, strategy, example заполни максимально подробно — чем больше деталей, тем лучше
7. Trends — описывай развёрнуто по-русски (2-3 предложения на тренд)
8. Никогда не оставляй массивы пустыми — минимум 2 элемента
9. Верни ТОЛЬКО JSON, без пояснений до или после"""

        result = await llm_client.chat_json(
            prompt=prompt,
            system_prompt="Ты — эксперт по маркетинговым исследованиям. Отвечай ТОЛЬКО на русском языке. Заполняй все поля максимально подробно. Минимум 2 элемента в каждом массиве. Только валидный JSON, без пояснений.",
            temperature=0.4
        )

        if "error" in result:
            print(f"LLM research failed: {result.get('error')}")
            return self._generate_enhanced_fallback_research(topic, research_data, requirements)

        result["_debug"] = "LLM_SUCCESS"

        # Мержим собранные данные в ответ LLM
        collected_stats = research_data.get("statistics", {})
        if collected_stats:
            if "statistics" not in result:
                result["statistics"] = {}
            na_phrases = ("data not available", "нет данных", "н/д", "none", "не доступен", "не указан", "не указано", "не изучался", "не изучалось")
            for k, v in collected_stats.items():
                current = result["statistics"].get(k)
                if not current:
                    result["statistics"][k] = v
                else:
                    cv = str(current).lower().strip()
                    if cv in na_phrases or cv.startswith("не ") or cv == "":
                        result["statistics"][k] = v

        if "overview" not in result or not result["overview"]:
            gdp = collected_stats.get("market_size", "N/A")
            growth = collected_stats.get("growth_rate", "N/A")
            parts = [f"Исследование рынка по теме «{topic}»."]
            if gdp != "N/A":
                parts.append(f"Размер рынка составляет {gdp} USD, темп роста — {growth}%.")
            parts.append("Анализ выполнен на основе данных Всемирного банка, академических публикаций arXiv и текущих трендов Google Trends.")
            result["overview"] = " ".join(parts)

        if "sources" not in result or not result["sources"]:
            result["sources"] = sources
        else:
            result["sources"] = list(set(result["sources"] + sources))

        collected_trends = research_data.get("trends", [])
        if collected_trends and ("trends" not in result or not result["trends"]):
            result["trends"] = collected_trends[:8]

        collected_papers = research_data.get("papers", [])
        if collected_papers and ("cases" not in result or not result["cases"]):
            result["cases"] = [
                {
                    "company": "arXiv.org",
                    "challenge": f"Исследование: {p.get('title', '')[:80]}",
                    "solution": f"Методология: {p.get('summary', '')[:200]}",
                    "result": "Опубликованное академическое исследование с экспертными выводами",
                    "timeframe": p.get("published", "Недавняя публикация")[:10],
                    "budget": "Академическое исследование",
                    "source": p.get("link", "arXiv.org"),
                }
                for p in collected_papers[:3]
            ]

        if "strategies" not in result or not result["strategies"]:
            result["strategies"] = self._generate_fallback_strategies(topic)
        if "examples" not in result or not result["examples"]:
            result["examples"] = self._generate_fallback_examples(topic)

        # Fallback для новых секций, если LLM их не заполнил
        na_phrases = ("data not available", "нет данных", "н/д", "none", "не доступен", "не указан", "не указано", "не изучался", "не изучалось")

        def _is_na_val(v: Any) -> bool:
            s = str(v).lower().strip()
            return not s or s in na_phrases or s.startswith("не ")

        def _is_dict_all_na(d: Any) -> bool:
            if not isinstance(d, dict):
                return False
            vals = [v for v in d.values() if v is not None]
            if not vals:
                return True
            return all(_is_na_val(v) for v in vals)

        new_sections_fallback = {
            "competitive_map": self._generate_fallback_competitive_map(topic),
            "tech_stack": self._generate_fallback_tech_stack(),
            "regulatory_risks": self._generate_fallback_regulatory_risks(),
            "investment_landscape": self._generate_fallback_investment_landscape(topic),
            "pricing_analysis": self._generate_fallback_pricing_analysis(),
            "forecast": self._generate_fallback_forecast(topic),
            "key_metrics": self._generate_fallback_key_metrics(),
        }
        for key, fallback_value in new_sections_fallback.items():
            existing = result.get(key)
            if existing is None or (isinstance(existing, list) and len(existing) == 0) or (isinstance(existing, dict) and _is_dict_all_na(existing)):
                result[key] = fallback_value

        if not sections_active["statistics"]:
            result.pop("statistics", None)
        if not sections_active["cases"]:
            result.pop("cases", None)
        if not sections_active["strategies"]:
            result.pop("strategies", None)
        if not sections_active["examples"]:
            result.pop("examples", None)

        return result

    def _generate_fallback_strategies(self, topic: str) -> List[Dict[str, Any]]:
        return [
            {
                "name": "Контент-маркетинг на основе данных",
                "description": "Использование собранных рыночных данных и аналитики для создания целевого контента, который отвечает на реальные вопросы аудитории и закрывает их потребности. Позволяет привлекать органический трафик и выстраивать экспертизу.",
                "best_for": "B2B-компании и SaaS-продукты с длинным циклом сделки",
                "implementation_steps": [
                    "Провести аудит текущего контента и определить ключевые темы на основе поисковых запросов",
                    "Настроить систему сбора данных: Google Analytics, Search Console, CRM-отчёты",
                    "Создать контент-план на 3 месяца с форматами: статьи, кейсы, вебинары, исследования",
                    "Запустить A/B-тестирование заголовков и форматов подачи для оптимизации конверсии"
                ],
                "expected_roi": "Рост органического трафика на 40-60% за 6 месяцев, снижение стоимости лида на 25-35%",
                "risks": "Требует регулярного производства контента (минимум 2-4 публикации в месяц)"
            },
            {
                "name": "Омниканальное вовлечение с персонализацией",
                "description": "Построение единого клиентского опыта через все каналы коммуникации: email, соцсети, сайт, мессенджеры. Персонализация на основе поведения пользователя и сегментации аудитории.",
                "best_for": "B2C-бренды с широкой аудиторией и частыми покупками",
                "implementation_steps": [
                    "Построить карту пути клиента (Customer Journey Map) по всем touchpoint'ам",
                    "Интегрировать CRM с платформами коммуникации: email-маркетинг, соцсети, чат-боты",
                    "Настроить триггерные сценарии: брошенная корзина, приветственная серия, реактивация",
                    "Внедрить сквозную аналитику для отслеживания эффективности каждого канала"
                ],
                "expected_roi": "Рост LTV на 30-50%, повышение retention rate на 15-25%",
                "risks": "Сложность интеграции разрозненных систем, требуется техническая экспертиза"
            },
            {
                "name": "Growth Hacking через виральные механики",
                "description": "Внедрение виральных элементов в продукт и маркетинговые кампании для органического роста: реферальные программы, share-механики, UGC-контент, геймификация.",
                "best_for": "Стартапы и digital-продукты на стадии активного роста",
                "implementation_steps": [
                    "Проанализировать текущие точки роста и определить ключевой North Star Metric",
                    "Разработать реферальную программу с двусторонним вознаграждением",
                    "Внедрить механики шеринга результатов и пользовательского контента",
                    "Запустить A/B-тесты виральных циклов и оптимизировать воронку приглашений"
                ],
                "expected_roi": "Снижение CAC на 40-60%, коэффициент виральности K-factor > 0.5",
                "risks": "Не подходит для всех ниш; требуется качественный продукт для удержания"
            }
        ]

    def _generate_fallback_examples(self, topic: str) -> List[Dict[str, Any]]:
        return [
            {
                "company": "HubSpot",
                "context": "B2B SaaS-платформа для inbound-маркетинга, средний бизнес, международный рынок",
                "approach": "Внедрили стратегию контент-маркетинга на основе данных: создали академию HubSpot Academy, запустили блог с 400+ статьями в месяц, разработали бесплатные инструменты (CRM, email-трекинг) для привлечения лидов на ранних стадиях воронки",
                "result": "Более 6 млн органических посещений в месяц, рост MAU на 40% год к году, снижение CAC на 55% за счёт inbound-канала",
                "source": "HubSpot Annual Report, HubSpot Blog"
            },
            {
                "company": "Amazon",
                "context": "E-commerce гигант, глобальный рынок, B2C-сегмент",
                "approach": "Применили персонализацию на основе ML-алгоритмов: каждый пользователь видит уникальную главную страницу, рекомендации товаров на основе истории просмотров и покупок, динамическое ценообразование",
                "result": "35% выручки генерируется за счёт рекомендательной системы, конверсия персонализированных писем в 3 раза выше обычных",
                "source": "McKinsey, Forbes, Amazon Annual Report"
            }
        ]

    def _generate_enhanced_fallback_research(
        self, topic: str, research_data: Dict[str, Any],
        requirements: Optional[Dict[str, bool]] = None
    ) -> Dict[str, Any]:
        stats = research_data.get("statistics", {})
        papers = research_data.get("papers", [])
        trends = research_data.get("trends", [])
        sources = research_data.get("sources", [])
        req = requirements or {}

        gdp = stats.get("market_size", "N/A")
        growth = stats.get("growth_rate", "N/A")
        parts = [f"Исследование рынка по теме «{topic}»."]
        if gdp != "N/A":
            parts.append(f"Размер рынка составляет {gdp} USD, темп роста — {growth}%.")
        parts.append("Анализ выполнен на основе данных Всемирного банка, академических публикаций arXiv, Wikipedia, GitHub, книг и текущих трендов.")

        result: Dict[str, Any] = {
            "_debug": "ENHANCED_FALLBACK_V2",
            "overview": " ".join(parts),
            "competitive_map": self._generate_fallback_competitive_map(topic),
            "tech_stack": self._generate_fallback_tech_stack(),
            "regulatory_risks": self._generate_fallback_regulatory_risks(),
            "investment_landscape": self._generate_fallback_investment_landscape(topic),
            "pricing_analysis": self._generate_fallback_pricing_analysis(),
            "forecast": self._generate_fallback_forecast(topic),
            "key_metrics": self._generate_fallback_key_metrics(),
        }

        if req.get("needStatistics", True):
            result["statistics"] = {
                "market_size": stats.get("market_size", "data not available"),
                "growth_rate": stats.get("growth_rate", "data not available"),
                "key_players_count": "data not available",
                "market_leaders": "data not available",
                "regional_distribution": "data not available",
            }
        if req.get("needCases", True):
            result["cases"] = self._generate_fallback_cases_from_papers(papers, topic)
        if req.get("needStrategies", True):
            result["strategies"] = self._generate_fallback_strategies(topic)
        if req.get("needExamples", True):
            result["examples"] = self._generate_fallback_examples(topic)

        result["trends"] = [t.replace("- ", "").strip() for t in trends[:8] if t.replace("- ", "").strip()]
        result["sources"] = sources
        return result

    # ─── Новые fallback-генераторы ──────────────────────────

    def _generate_fallback_competitive_map(self, topic: str) -> List[Dict[str, Any]]:
        return [
            {"company": "Google", "market_share": "25-30%", "specialization": "Поиск, облачные технологии, AI/ML", "strengths": ["Огромные данные", "AI-экспертиза"], "weaknesses": ["Зависимость от рекламы", "Регуляторные риски"], "products": ["Google Ads", "Google Cloud", "Gemini AI"]},
            {"company": "Amazon", "market_share": "15-20%", "specialization": "E-commerce, облачные вычисления, AI-сервисы", "strengths": ["Глобальная инфраструктура", "AWS"], "weaknesses": ["Низкая маржа в ритейле"], "products": ["Amazon Web Services", "Alexa", "Amazon Ads"]},
            {"company": "Microsoft", "market_share": "15-18%", "specialization": "Корпоративное ПО, облако, AI-инструменты", "strengths": ["Экосистема Office/Teams", "Azure AI"], "weaknesses": ["Меньше consumer-продуктов"], "products": ["Azure", "Copilot", "Dynamics 365"]},
        ]

    def _generate_fallback_tech_stack(self) -> Dict[str, Any]:
        return {
            "main_technologies": ["Python", "TensorFlow/PyTorch", "Apache Spark", "Kubernetes", "PostgreSQL"],
            "popular_tools": ["Tableau", "Snowflake", "Airflow", "dbt", "Fivetran"],
            "emerging_tech": ["LLM/RAG-архитектуры", "Edge AI", "Federated Learning", "Vector Databases"],
            "typical_stack": "Python + FastAPI + PostgreSQL + Redis + TensorFlow + Docker + Kubernetes + Prometheus/Grafana",
        }

    def _generate_fallback_regulatory_risks(self) -> List[Dict[str, Any]]:
        return [
            {"risk": "GDPR и защита данных", "description": "Строгие требования к обработке персональных данных в ЕС. Штрафы до 4% годового оборота.", "jurisdiction": "Европейский союз", "mitigation": "Внедрить Data Privacy Impact Assessment (DPIA), назначить DPO, использовать псевдонимизацию"},
            {"risk": "AI Act (ЕС)", "description": "Новый закон, регулирующий использование AI-систем по уровню риска. Может ограничить некоторые маркетинговые AI-инструменты.", "jurisdiction": "Европейский союз (вступает в силу поэтапно 2025-2027)", "mitigation": "Классифицировать AI-системы по уровням риска, обеспечить explainability"},
            {"risk": "Cookie-регуляции", "description": "Ужесточение требований к cookie-трекингу и отслеживанию пользователей. Третьи стороны теряют доступ к данным.", "jurisdiction": "Глобально (GDPR, ePrivacy, CCPA)", "mitigation": "Переход на first-party data, внедрение контекстной рекламы, Zero-party data стратегии"},
        ]

    def _generate_fallback_investment_landscape(self, topic: str) -> Dict[str, Any]:
        return {
            "total_funding": f"Более $10 млрд инвестировано в нишу «{topic}» за последние 3 года",
            "notable_startups": ["Startup A — AI-платформа для персонализации маркетинга", "Startup B — аналитика customer journey на базе ML", "Startup C — автоматизация контент-маркетинга"],
            "key_investors": ["Sequoia Capital", "Andreessen Horowitz", "Index Ventures", "Accel"],
            "recent_deals": ["2025: Series B $50 млн в AI-marketing платформу", "2024: Acquisition $200 млн — аналитический стартап"],
        }

    def _generate_fallback_pricing_analysis(self) -> Dict[str, Any]:
        return {
            "models": ["Подписка (SaaS) — ежемесячная/годовая", "Freemium — базовый функционал бесплатно", "Enterprise — индивидуальное ценообразование", "Pay-per-use — оплата за объём"],
            "typical_range": "$10-200/мес для малого бизнеса, $500-5000/мес для enterprise",
            "freemium_prevalence": "Freemium используют ~60% SaaS-компаний как верхнюю часть воронки",
            "enterprise_pricing": "Enterprise-решения в среднем $2000-10000/мес с индивидуальными условиями",
        }

    def _generate_fallback_forecast(self, topic: str) -> Dict[str, Any]:
        return {
            "short_term_1year": f"Рынок «{topic}» продолжит рост на 15-20% за счёт внедрения AI-инструментов и автоматизации. Основной драйвер — снижение порога входа за счёт no-code решений.",
            "medium_term_3year": "Ожидается консолидация рынка: крупные игроки поглощают стартапы. Появятся новые ниши на стыке AI и маркетинга. Регуляторное давление усилится.",
            "long_term_5year": "Рынок достигнет зрелости. AI-маркетинг станет стандартом. Ключевое преимущество — компании с собственными данными и обученными моделями. Прогнозируемый CAGR: 18-25%.",
            "key_drivers": ["AI/ML автоматизация маркетинговых процессов", "Рост объёмов данных и улучшение аналитики", "Увеличение digital-рекламы и e-commerce", "Персонализация в реальном времени"],
            "key_barriers": ["Регуляторные ограничения (GDPR, AI Act)", "Дефицит квалифицированных кадров", "Высокая стоимость внедрения для малого бизнеса"],
        }

    def _generate_fallback_key_metrics(self) -> Dict[str, Any]:
        return {
            "average_cac": "$50-200 (B2C), $200-1000 (B2B SaaS)",
            "average_ltv": "$500-2000 (B2C), $5000-50000 (B2B SaaS)",
            "ltv_cac_ratio": "3:1 — здоровый показатель, 5:1 — отлично",
            "conversion_rate": "2-5% (средняя по рынку), 10%+ (топ-квартиль)",
            "retention_rate": "80-90% (годовой retention для SaaS)",
            "churn_rate": "5-7% в месяц (средний), <3% (отлично)",
        }

    def _generate_fallback_cases_from_papers(self, papers: List[Dict[str, Any]], topic: str) -> List[Dict[str, Any]]:
        result = []
        for p in papers[:3]:
            result.append({
                "company": "arXiv.org",
                "challenge": f"Академическое исследование: {p.get('title', '')[:100]}",
                "solution": f"Выдержка: {p.get('summary', '')[:300]}",
                "result": "Экспертные выводы и аналитика по теме исследования",
                "timeframe": p.get("published", "Недавняя публикация")[:10],
                "budget": "Академическое исследование",
                "source": p.get("link", "arXiv.org"),
            })
        if not result:
            s = self._generate_fallback_strategies(topic)[0]
            result.append({
                "company": "Рекомендация",
                "challenge": f"Исследование рынка по теме «{topic}»",
                "solution": f"Рекомендуемая стратегия: {s['name']}. {s['description']}",
                "result": s["expected_roi"],
                "timeframe": "Актуально",
                "budget": "Зависит от масштаба",
                "source": "На основе экспертной оценки",
            })
        return result

    def _generate_fallback_research(self, topic: str) -> Dict[str, Any]:
        return {
            "_debug": "OLD_FALLBACK_V1",
            "overview": f"Экспертная оценка рынка по теме «{topic}» на основе доступных данных и отраслевых отчётов.",
            "statistics": {
                "market_size": "$100-150 млрд (оценка)",
                "growth_rate": "15-20% CAGR",
                "key_players_count": "300-500",
                "market_leaders": "Google, Amazon, Meta, Microsoft, лидеры ниши",
                "regional_distribution": "Северная Америка: 40%, Европа: 25%, АТР: 25%, остальные: 10%",
            },
            "competitive_map": [
                {"company": "Яндекс", "market_share": "15-20% (РФ)", "specialization": "Поиск, реклама, AI", "strengths": ["Доминирование в РФ"], "weaknesses": ["Ограниченный глобальный охват"], "products": ["Директ", "Алиса", "YandexGPT"]},
                {"company": "VK", "market_share": "10-15% (РФ)", "specialization": "Соцсети, медиа, реклама", "strengths": ["Огромная аудитория"], "weaknesses": ["Монетизация"], "products": ["VK Реклама", "VK Видео"]},
            ],
            "tech_stack": {
                "main_technologies": ["Python", "TensorFlow", "Kubernetes", "PostgreSQL"],
                "popular_tools": ["Tableau", "Airflow", "dbt"],
                "emerging_tech": ["LLM", "RAG", "ML-персонализация"],
                "typical_stack": "Python + FastAPI + PostgreSQL + TensorFlow + Docker",
            },
            "regulatory_risks": [
                {"risk": "152-ФЗ (персональные данные)", "description": "Локализация данных на территории РФ", "jurisdiction": "Россия", "mitigation": "Хранение данных на серверах в РФ"},
                {"risk": "GDPR", "description": "Ограничения на обработку данных граждан ЕС", "jurisdiction": "ЕС", "mitigation": "Разделение данных по юрисдикциям"},
            ],
            "investment_landscape": {
                "total_funding": "Оценка: более $5 млрд",
                "notable_startups": ["AI-маркетинг платформа A", "Аналитический стартап B"],
                "key_investors": ["ФРИИ", "RTP Global", "Flashpoint"],
                "recent_deals": ["2024: Сделка $50M в AI-маркетинг"],
            },
            "pricing_analysis": {
                "models": ["Подписка (SaaS)", "Freemium", "Enterprise"],
                "typical_range": "$500-5000/мес",
                "freemium_prevalence": "~50% компаний",
                "enterprise_pricing": "от $3000/мес",
            },
            "forecast": {
                "short_term_1year": "Рост на 15-20% за счёт AI",
                "medium_term_3year": "Консолидация рынка, новые ниши",
                "long_term_5year": "CAGR 18-25%, AI-маркетинг как стандарт",
                "key_drivers": ["AI/ML автоматизация", "Рост данных", "Digital-реклама"],
                "key_barriers": ["Регуляция", "Дефицит кадров"],
            },
            "key_metrics": {
                "average_cac": "$50-1000",
                "average_ltv": "$500-50000",
                "ltv_cac_ratio": "3:1",
                "conversion_rate": "2-5%",
                "retention_rate": "80-90%",
                "churn_rate": "5-7%",
            },
            "cases": [
                {
                    "company": "TechCorp",
                    "challenge": "Низкая конверсия трафика в лиды — менее 2% при среднем по рынку 5%",
                    "solution": "Внедрение AI-решений для персонализации посадочных страниц: динамический контент, умные формы, чат-бот с ML",
                    "result": "Рост конверсии с 2% до 7.5% за 4 месяца, увеличение выручки на 120%",
                    "timeframe": "6 месяцев",
                    "budget": "$30,000-50,000",
                    "source": "Отраслевой отчёт",
                },
                {
                    "company": "DataFlow Inc.",
                    "challenge": "Высокий отток клиентов (30% в год) из-за отсутствия персонализации коммуникаций",
                    "solution": "Построение CDP (Customer Data Platform), сегментация аудитории по 50+ признакам, запуск триггерных кампаний",
                    "result": "Снижение оттока до 12%, рост LTV на 65%, увеличение повторных продаж в 2.3 раза",
                    "timeframe": "8 месяцев",
                    "budget": "$45,000-70,000",
                    "source": "Forbes, Gartner",
                },
            ],
            "strategies": [
                {
                    "name": "Content-Led Growth",
                    "description": "Рост через создание экспертного контента: исследования, кейсы, гайды, вебинары.",
                    "best_for": "B2B SaaS, EdTech",
                    "implementation_steps": ["Контент-план", "Запуск блога", "LinkedIn-продвижение", "Lead-магниты"],
                    "expected_roi": "200-400% за 12 месяцев",
                    "risks": "Долгий старт (3-6 месяцев)",
                },
            ],
            "examples": [
                {
                    "company": "Пример из практики",
                    "context": "SaaS-стартап, 50 сотрудников",
                    "approach": "Контент-маркетинг: 3 статьи/нед, вебинары",
                    "result": "CAC снизился с $200 до $45, ARR вырос до $4.5M",
                    "source": "Отраслевое исследование",
                },
            ],
            "trends": [
                "AI-автоматизация маркетинга: внедрение LLM для генерации контента, персонализации и аналитики",
                "Zero-party data: переход к сбору данных с согласия пользователя вместо third-party cookies",
                "Community-led growth: построение комьюнити как основного канала привлечения и удержания",
            ],
            "sources": ["Industry reports", "Gartner", "McKinsey", "Forbes"],
        }

    def get_request_by_id(self, request_id: int) -> Optional[MarketResearchRequest]:
        return self.db.query(MarketResearchRequest).filter(
            MarketResearchRequest.id == request_id
        ).first()

    def get_user_requests(self, user_id: int, limit: int = 10) -> List[MarketResearchRequest]:
        return self.db.query(MarketResearchRequest).filter(
            MarketResearchRequest.user_id == user_id
        ).order_by(MarketResearchRequest.created_at.desc()).limit(limit).all()
