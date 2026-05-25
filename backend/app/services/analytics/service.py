from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from ...models.models import AnalyticsRequest, MarketingCase
from ...utils.vector_store import vector_db
from ...utils.marketing_models import MarketingModelsLibrary
from ...utils.llm_client import llm_client
from ...utils.llm_schemas import AnalyticsResponse, CompetitorAnalysisResponse, SWOTAnalysisResponse, AudienceAnalysisResponse


class AnalyticsService:
    """Service for marketing idea analytics"""
    
    SYSTEM_PROMPT = """Ты - экспертный маркетинговый аналитик с 15-летним опытом в маркетинге и PR.
Твоя задача - анализировать маркетинговые идеи и давать профессиональные рекомендации.
Анализируй: сильные стороны, слабые стороны, вероятность успеха, рекомендации."""

    def __init__(self, db: Session):
        self.db = db
    
    async def analyze_idea(self, idea_description: str, user_id: int, analysis_type: str = "idea") -> Dict[str, Any]:
        """Analyze a marketing idea or perform other analysis types"""
        if not idea_description or not idea_description.strip():
            idea_description = f"Анализ типа: {analysis_type}"
        
        print(f"DEBUG analyze_idea: analysis_type={analysis_type}, idea={idea_description[:50]}...")
        
        request = AnalyticsRequest(
            user_id=user_id,
            idea_description=idea_description,
            status="processing"
        )
        
        try:
            self.db.add(request)
            self.db.commit()
            self.db.refresh(request)
        except Exception as e:
            self.db.rollback()
            print(f"Error creating request: {e}")
            raise e
        
        try:
            if analysis_type == "competitor":
                analysis_result = await self._analyze_competitor(idea_description)
            elif analysis_type == "swot":
                analysis_result = await self._analyze_swot(idea_description)
            elif analysis_type == "audience":
                analysis_result = await self._analyze_audience(idea_description)
            else:
                analysis_result = await self._generate_llm_analysis(idea_description)
            
            request.analysis_result = analysis_result.model_dump()
            request.status = "completed"
            self.db.commit()
            
            return {
                "request_id": request.id,
                "analysis": analysis_result.model_dump(),
                "analysis_type": analysis_type
            }
        except Exception as e:
            request.status = "failed"
            self.db.commit()
            raise e
    
    async def _analyze_competitor(self, competitor_info: str) -> CompetitorAnalysisResponse:
        """Deep competitor analysis with metrics and positioning"""
        print(f"DEBUG: _analyze_competitor called with: {competitor_info[:100]}...")
        
        # Simplified but comprehensive prompt
        prompt = f"""Проанализируй компанию и верни JSON с полями: company_info, business_metrics, market_position, products_services, pricing, marketing_channels, online_presence, strengths, weaknesses, opportunities, threats, recommendations.

Для каждого поля возвращай структурированные данные. Если данные недоступны - пиши "нет данных".

Пример формата:
{{
  "company_info": {{"name": "X", "founded_year": "X", "headquarters": "X"}},
  "business_metrics": {{"revenue": "нет данных", "employees_count": "нет данных"}},
  "market_position": {{"segment": "B2B", "positioning": "премиум"}},
  "products_services": [{{"name": "X", "description": "X"}}],
  "pricing": {{"model": "подписка"}},
  "marketing_channels": ["website", "social"],
  "online_presence": {{"website": "x.com"}},
  "strengths": ["X"],
  "weaknesses": ["X"],
  "opportunities": ["X"],
  "threats": ["X"],
  "recommendations": ["X"]
}}

Компания: {competitor_info}

Верни ТОЛЬКО валидный JSON.

{{
  "company_info": {{
    "name": "Название компании",
    "founded_year": "Год основания",
    "headquarters": "Штаб-квартира",
    "ownership": "Собственность (частная/гос/корпорация)",
    "legal_form": "Юр. форма (ООО, АО и тд)",
    "registration_info": "Регистрационные данные"
  }},
  "business_metrics": {{
    "revenue": "Оборот (годовой)",
    "revenue_currency": "Валюта",
    "employees_count": "Количество сотрудников",
    "employees_range": "Диапазон (1-10, 11-50, 51-200, 201-500, 500+)",
    "branches_count": "Количество офисов/филиалов",
    "franchise_count": "Франчайзинговых точек",
    "market_share": "Доля рынка",
    "annual_growth": "Годовой рост %",
    "profitability": "Прибыльность"
  }},
  "market_position": {{
    "segment": "Сегмент рынка",
    "positioning": "Позиционирование",
    "target_audience": "Целевая аудитория",
    "unique_sellingProposition": "УТП",
    "competitive_advantage": "Конкурентное преимущество"
  }},
  "products_services": [
    {{"name": "Название", "description": "Описание", "price_range": "Ценовой диапазон", "popularity": "Популярность"}}
  ],
  "pricing": {{
    "model": "Ценовая модель",
    "average_check": "Средний чек",
    "discounts": "Система скидок",
    "payment_terms": "Условия оплаты"
  }},
  "marketing_channels": ["Онлайн", "ТВ", "Наружная реклама", "Партнерства"],
  "online_presence": {{
    "website": "Основной сайт",
    "website_traffic": "Трафик (мес)",
    "seo_rating": "SEO рейтинг",
    "social_media": {{"platform": "подписчики"}},
    "app_downloads": "Загрузок приложения",
    "reviews_rating": "Рейтинг отзывов"
  }},
  "strengths": ["Сильная сторона 1", "Сильная сторона 2"],
  "weaknesses": ["Слабая сторона 1", "Слабая сторона 2"],
  "opportunities": ["Возможность для вас 1", "Возможность 2"],
  "threats": ["Угроза от конкурента 1", "Угроза 2"],
  "recommendations": ["Рекомендация по позиционированию 1", "Рекомендация 2"]
}}

Информация о конкуренте: {competitor_info}

Ответь ТОЛЬКО валидным JSON без дополнительного текста. Заполняй ВСЕ поля найденной информацией. Если данные недоступны - пиши "данные недоступны"."""

        try:
            result = await llm_client.chat_parse(
                prompt=prompt,
                response_model=CompetitorAnalysisResponse,
                system_prompt="Ты эксперт по конкурентному анализу. Верни подробный JSON.",
                strict=False,
                temperature=0.3
            )
            print(f"DEBUG: Competitor LLM returned type: {type(result)}")
            print(f"DEBUG: Competitor result keys: {result.model_dump().keys() if result else 'None'}")
            return result
        except Exception as e:
            print(f"Competitor analysis LLM error: {e}")
            import traceback
            traceback.print_exc()
            return self._fallback_competitor()
    
    async def _analyze_swot(self, business_info: str) -> SWOTAnalysisResponse:
        """Generate detailed SWOT analysis for a business"""
        prompt = f"""Проведи детальный стратегический анализ бизнеса. Входные данные могут быть:
- Названием компании/бренда (например "Apple", "Яндекс", "Сбербанк")
- Описанием продукта/услуги (например "Онлайн-курсы английского для взрослых")
- Описанием проекта/бизнеса

Твоя задача - определить что это за бизнес и провести полный анализ. Верни JSON:

{{
  "business_description": "Краткое описание что это за бизнес, продукт, целевая аудитория",
  "strengths": [
    {{"title": "Сильная сторона", "description": "Конкретное описание", "impact": "высокий/средний/низкий", "category": "ресурсы/компетенции/продукт/рынок"}}
  ],
  "weaknesses": [
    {{"title": "Слабая сторона", "description": "Конкретное описание", "impact": "высокий/средний/низкий", "category": "ресурсы/процессы/продукт/рынок"}}
  ],
  "opportunities": [
    {{"title": "Возможность", "description": "Конкретная возможность", "timeline": "краткосрочный/среднесрочный/долгосрочный", "potential": "высокий/средний/низкий"}}
  ],
  "threats": [
    {{"title": "Угроза", "description": "Конкретная угроза", "likelihood": "высокая/средняя/низкая", "severity": "критическая/высокая/умеренная"}}
  ],
  "strategies": {{
    "S-O (используем сильные для возможностей)": ["Стратегия"],
    "W-O (преодолеваем слабости для возможностей)": ["Стратегия"],
    "S-T (используем сильные против угроз)": ["Стратегия"],
    "W-T (защищаемся от угроз при слабостях)": ["Стратегия"]
  }},
  "key_insights": ["Главный вывод 1", "Главный вывод 2"],
  "recommendations": ["Конкретная рекомендация 1", "Конкретная рекомендация 2"],
  "pest_factors": {{
    "Political (Политика)": ["Фактор 1", "Фактор 2"],
    "Economic (Экономика)": ["Фактор 1", "Фактор 2"],
    "Social (Социум)": ["Фактор 1", "Фактор 2"],
    "Technological (Технологии)": ["Фактор 1", "Фактор 2"]
  }},
  "kpis": [
    {{"name": "KPI название", "description": "Что измеряет", "target": "Целевое значение", "current": "Текущее (оцени)"}}
  ],
  "competitor_comparison": [
    {{"metric": "Метрика (цена/качество/скорость/сервис)", "your_position": "Ваша позиция", "competitor_advantage": "Преимущество конкурента", "action": "Что делать"}}
  ]
}}

ВАЖНО: Входные данные - это ОПИСАНИЕ БИЗНЕСА/ПРОДУКТА, а не название компании.
Пример входа: "Онлайн-курсы английского языка для взрослых 25-45 лет, занятия через Zoom, подписка 2990 руб/мес"
НЕ надо писать "данные недоступны" - сделай обоснованный анализ на основе описания.

Бизнес для анализа: {business_info}

Верни ТОЛЬКО валидный JSON."""

        try:
            result = await llm_client.chat_parse(
                prompt=prompt,
                response_model=SWOTAnalysisResponse,
                system_prompt="Ты эксперт по стратегическому маркетинговому анализу. Проведи детальный анализ на основе описания продукта/бизнеса.",
                strict=False,
                temperature=0.4
            )
            print(f"DEBUG: SWOT LLM returned type: {type(result)}, keys: {result.model_dump().keys() if result else 'None'}")
            return result
        except Exception as e:
            print(f"SWOT analysis LLM error: {e}")
            import traceback
            traceback.print_exc()
            return self._fallback_swot()
    
    async def _analyze_audience(self, product_info: str) -> AudienceAnalysisResponse:
        """Analyze and segment target audience"""
        prompt = f"""Проведи детальную сегментацию целевой аудитории на основе описания продукта/услуги. Верни JSON:

{{
  "product_description": "Краткое описание продукта",
  "total_addressable_market": "Общий объем целевой аудитории (размер, сегменты)",
  "segments": [
    {{
      "name": "Название сегмента (например Молодежь 18-25)",
      "size": "Размер в % или абсолютных числах",
      "description": "Описание кто это",
      "age_range": "Возрастной диапазон",
      "income_level": "Уровень дохода",
      "online_behavior": "Как ведут себя онлайн"
    }}
  ],
  "primary_persona": {{
    "name": "Главная персона",
    "demographics": "Демография",
    "goals": "Цели и желания",
    "frustrations": "Боли и разочарования",
    "values": "Ценности"
  }},
  "behavioral_traits": ["Поведенческая черта 1", "Поведенческая черта 2"],
  "pain_points": ["Боль 1", "Боль 2", "Боль 3"],
  "motivations": ["Мотивация 1", "Мотивация 2"],
  "preferred_channels": ["Канал 1", "Канал 2", "Канал 3"],
  "decision_factors": ["Фактор принятия решения 1", "Фактор 2"],
  "key_insights": ["Ключевой инсайт 1", "Ключевой инсайт 2"],
  "recommendations": ["Рекомендация 1", "Рекомендация 2"]
}}

Продукт для анализа: {product_info}

Верни ТОЛЬКО валидный JSON."""

        try:
            result = await llm_client.chat_parse(
                prompt=prompt,
                response_model=AudienceAnalysisResponse,
                system_prompt="Ты эксперт по маркетинговым исследованиям и сегментации аудитории. Проводи детальный анализ ЦА на основе продукта.",
                strict=False,
                temperature=0.4
            )
            print(f"DEBUG: Audience LLM returned type: {type(result)}, keys: {result.model_dump().keys() if result else 'None'}")
            return result
        except Exception as e:
            print(f"Audience analysis LLM error: {e}")
            import traceback
            traceback.print_exc()
            return self._fallback_audience()
    
    def _fallback_competitor(self) -> CompetitorAnalysisResponse:
        return CompetitorAnalysisResponse(
            company_info={
                "name": "Данные недоступны",
                "founded_year": "данные недоступны",
                "headquarters": "данные недоступны",
                "ownership": "данные недоступны",
                "legal_form": "данные недоступны",
                "registration_info": "данные недоступны"
            },
            business_metrics={
                "revenue": "данные недоступны",
                "revenue_currency": "RUB",
                "employees_count": "данные недоступны",
                "employees_range": "данные недоступны",
                "branches_count": "данные недоступны",
                "franchise_count": "данные недоступны",
                "market_share": "данные недоступны",
                "annual_growth": "данные недоступны",
                "profitability": "данные недоступны"
            },
            market_position={
                "segment": "данные недоступны",
                "positioning": "данные недоступны",
                "target_audience": "данные недоступны",
                "unique_sellingProposition": "данные недоступны",
                "competitive_advantage": "данные недоступны"
            },
            products_services=[
                {"name": "Требует уточнения", "description": "данные недоступны", "price_range": "данные недоступны", "popularity": "данные недоступны"}
            ],
            pricing={
                "model": "данные недоступны",
                "average_check": "данные недоступны",
                "discounts": "данные недоступны",
                "payment_terms": "данные недоступны"
            },
            marketing_channels=["Telegram", "Instagram", "Сайт"],
            online_presence={
                "website": "данные недоступны",
                "website_traffic": "данные недоступны",
                "seo_rating": "данные недоступны",
                "social_media": {},
                "app_downloads": "данные недоступны",
                "reviews_rating": "данные недоступны"
            },
            strengths=["Сильный бренд", "Широкая дистрибуция", "Финансовые ресурсы"],
            weaknesses=["Высокие цены", "Медленная инновация", "Слабый digital"],
            opportunities=["Нишевый рынок", "Digital-каналы", "Ценовая конкуренция"],
            threats=["Большие игроки", "Новые технологии", "Регуляторные изменения"],
            recommendations=["Фокусироваться на нишевом рынке", "Использовать digital-каналы", "Предлагать лучшую ценность"]
        )
    
    def _fallback_swot(self) -> SWOTAnalysisResponse:
        return SWOTAnalysisResponse(
            business_description="Описание бизнеса недоступно",
            strengths=[
                {"title": "Уникальный продукт", "description": "Инновационное решение на рынке", "impact": "высокий", "category": "продукт"},
                {"title": "Команда экспертов", "description": "Опытная команда с глубокой экспертизой", "impact": "высокий", "category": "компетенции"},
                {"title": "Гибкость", "description": "Быстрая адаптация к изменениям", "impact": "средний", "category": "процессы"}
            ],
            weaknesses=[
                {"title": "Ограниченный бюджет", "description": "Недостаток ресурсов для масштабирования", "impact": "высокий", "category": "ресурсы"},
                {"title": "Маленькая доля рынка", "description": "Низкая узнаваемость бренда", "impact": "средний", "category": "рынок"},
                {"title": "Слабая дистрибуция", "description": "Ограниченные каналы продаж", "impact": "высокий", "category": "процессы"}
            ],
            opportunities=[
                {"title": "Рост рынка", "description": "Увеличение спроса на продукт", "timeline": "среднесрочный", "potential": "высокий"},
                {"title": "Новые технологии", "description": "Возможность внедрения инноваций", "timeline": "долгосрочный", "potential": "средний"},
                {"title": "Партнерства", "description": "Возможность стратегических альянсов", "timeline": "краткосрочный", "potential": "высокий"}
            ],
            threats=[
                {"title": "Конкуренты", "description": "Усиление конкуренции на рынке", "likelihood": "высокая", "severity": "высокая"},
                {"title": "Экономическая ситуация", "description": "Нестабильность экономики", "likelihood": "средняя", "severity": "критическая"},
                {"title": "Регуляторные изменения", "description": "Новые требования и ограничения", "likelihood": "низкая", "severity": "умеренная"}
            ],
            strategies={
                "S-O (сильные стороны + возможности)": [
                    "Использовать экспертизу команды для захвата растущего рынка",
                    "Инвестировать в инновации для усиления конкурентного преимущества"
                ],
                "W-O (слабые стороны + возможности)": [
                    "Найти стратегических партнеров для расширения дистрибуции",
                    "Привлечь инвестиции для масштабирования"
                ],
                "S-T (сильные стороны + угрозы)": [
                    "Использовать гибкость для быстрой адаптации к изменениям",
                    "Усилить позиционирование против конкурентов"
                ],
                "W-T (слабые стороны + угрозы)": [
                    "Диверсифицировать каналы продаж",
                    "Создать финансовую подушку безопасности"
                ]
            },
            key_insights=[
                "Основной фокус на S-O стратегиях для максимизации сильных сторон",
                "Критически важно решить проблему ограниченного бюджета",
                "Мониторинг конкурентов должен быть приоритетом"
            ],
            recommendations=[
                "Провести детальное исследование рынка",
                "Разработать финансовую стратегию роста",
                "Создать план партнерств и расширения дистрибуции"
            ],
            pest_factors={
                "Political (Политика)": ["Государственное регулирование отрасли", "Налоговая политика"],
                "Economic (Экономика)": ["Инфляция и курс валют", "Уровень доходов населения"],
                "Social (Социум)": ["Изменение потребительских предпочтений", "Тренды на здоровый образ жизни"],
                "Technological (Технологии)": ["Развитие digital-каналов", "Автоматизация процессов"]
            },
            kpis=[
                {"name": "Выручка", "description": "Общий доход от продаж", "target": "Рост 20% YoY", "current": "Оценить текущее"},
                {"name": "Конверсия", "description": "Процент лидов в клиентов", "target": "5-10%", "current": "Оценить текущее"},
                {"name": "CAC", "description": "Стоимость привлечения клиента", "target": "Уменьшение на 15%", "current": "Оценить текущее"},
                {"name": "LTV", "description": "Пожизненная ценность клиента", "target": "Рост 30%", "current": "Оценить текущее"}
            ],
            competitor_comparison=[
                {"metric": "Цена", "your_position": "Средний сегмент", "competitor_advantage": "Могут быть дешевле", "action": "Сделать акцент на качестве"},
                {"metric": "Качество", "your_position": "Высокое", "competitor_advantage": "Разное", "action": "Усилить позиционирование"},
                {"metric": "Скорость доставки", "your_position": "Средняя", "competitor_advantage": "Есть быстрее", "action": "Оптимизировать логистику"},
                {"metric": "Сервис", "your_position": "Хороший", "competitor_advantage": "Разный", "action": "Инвестировать в поддержку"}
            ]
        )
    
    def _fallback_audience(self) -> AudienceAnalysisResponse:
        return AudienceAnalysisResponse(
            product_description="Описание продукта недоступно",
            total_addressable_market="Требует уточнения на основе исследования",
            segments=[
                {"name": "Основной сегмент", "size": "40%", "description": "Главная целевая аудитория", "age_range": "25-45", "income_level": "средний", "online_behavior": "Активно используют соцсети"},
                {"name": "Вторичный сегмент", "size": "30%", "description": "Дополнительная аудитория", "age_range": "18-24", "income_level": "ниже среднего", "online_behavior": "Очень активны в интернете"},
                {"name": "Потенциальный сегмент", "size": "30%", "description": "Перспективная аудитория", "age_range": "45-60", "income_level": "высокий", "online_behavior": "Умеренная активность"}
            ],
            primary_persona={
                "name": "Основная персона",
                "demographics": "Женщины и мужчины 25-45 лет, средний доход, городские жители",
                "goals": "Решение конкретной проблемы, экономия времени, улучшение качества жизни",
                "frustrations": "Нехватка времени, сложность выбора, низкое качество существующих решений",
                "values": "Качество, удобство, экономия времени, надежность"
            },
            behavioral_traits=["Ищут отзывы перед покупкой", "Сравнивают цены", "Реагируют на рекомендации", "Ценят персональный подход"],
            pain_points=["Нет времени на исследование", "Сложно найти надежное решение", "Высокие цены", "Плохой сервис"],
            motivations=["Экономия денег", "Экономия времени", "Улучшение качества жизни", "Статус"],
            preferred_channels=["Instagram", "Telegram", "Google", "YouTube"],
            decision_factors=["Цена", "Качество", "Отзывы", "Рекомендации", "Бренд"],
            key_insights=[
                "Основной фокус на возраст 25-45 лет",
                "Ключевой мотиватор - экономия времени",
                "Важны отзывы и рекомендации"
            ],
            recommendations=[
                "Создать детальные персоны для каждого сегмента",
                "Провести интервью с представителями ЦА",
                "Использовать таргетированную рекламу по сегментам",
                "Создать контент для разных этапов воронки"
            ]
        )
    
    async def _generate_llm_analysis(self, idea: str) -> AnalyticsResponse:
        """Generate analysis using GigaChat with structured output"""
        prompt = f"""Проанализируй маркетинговую идею и верни JSON с полной оценкой:

{{
  "success_probability": 0.75,
  "strengths": ["Сильная сторона 1", "Сильная сторона 2"],
  "weaknesses": ["Слабая сторона 1", "Слабая сторона 2"],
  "recommendations": ["Рекомендация 1", "Рекомендация 2"],
  "similar_cases": [],
  "suggested_models": ["AARRR", "4P"],
  "ai_summary": "Резюме: краткая оценка актуальности, перспективности и потенциала идеи на рынке в 2-3 предложениях",
  "propagation_suggestions": ["Как продвигать 1", "Как масштабировать 2", "Каналы охвата 3"]
}}

Формула успеха учитывает: уникальность идеи, размер целевой аудитории, конкурентность рынка, реализуемость, финансовую перспективу.

Идея: {idea}

Верни ТОЛЬКО валидный JSON."""

        try:
            result = await llm_client.chat_parse(
                prompt=prompt,
                response_model=AnalyticsResponse,
                system_prompt=self.SYSTEM_PROMPT,
                strict=True,
                temperature=0.5
            )
            return result
        except Exception as e:
            print(f"Analytics LLM error: {e}")
            return self._generate_fallback_analysis()
    
    def _generate_fallback_analysis(self) -> AnalyticsResponse:
        """Fallback analysis when LLM fails"""
        return AnalyticsResponse(
            success_probability=0.7,
            strengths=[
                "Инновационный подход к решению проблемы",
                "Потенциал для дифференциации на рынке",
                "Возможность масштабирования",
                "Соответствие трендам рынка"
            ],
            weaknesses=[
                "Требует значительных инвестиций в маркетинг",
                "Высокая конкуренция в нише",
                "Сложность привлечения целевой аудитории"
            ],
            recommendations=[
                "Провести A/B тестирование на малой аудитории",
                "Сфокусироваться на уникальном торговом предложении",
                "Использовать контент-маркетинг для привлечения",
                "Внедрить реферальную программу",
                "Партнерство с лидерами мнений в нише"
            ],
            similar_cases=[],
            suggested_models=["AARRR", "4P", "GTM", "SWOT"],
            ai_summary="Идея имеет потенциал на рынке. Ключевые факторы успеха - уникальность решения и соответствие текущим трендам. Рекомендуется протестировать на малой аудитории перед масштабированием.",
            propagation_suggestions=[
                "Запустить контент-маркетинг в социальных сетях",
                "Использовать партнерские программы с лидерами мнений",
                "Внедрить реферальную систему для органического роста",
                "Тестировать платную рекламу на узкую аудиторию"
            ]
        )
    
    def get_request_by_id(self, request_id: int) -> Optional[AnalyticsRequest]:
        """Get analytics request by ID"""
        return self.db.query(AnalyticsRequest).filter(
            AnalyticsRequest.id == request_id
        ).first()
    
    def get_user_requests(self, user_id: int, limit: int = 10) -> List[AnalyticsRequest]:
        """Get all analytics requests for a user"""
        return self.db.query(AnalyticsRequest).filter(
            AnalyticsRequest.user_id == user_id
        ).order_by(AnalyticsRequest.created_at.desc()).limit(limit).all()
    
    async def find_similar_cases(self, idea_description: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Find similar marketing cases from database"""
        # TODO: Will implement vector search with embeddings later
        # For now, return empty list
        return []
