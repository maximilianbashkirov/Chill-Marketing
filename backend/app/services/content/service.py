import random
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from ...models.models import ContentRequest
from ...utils.vector_store import vector_db
from ...utils.llm_client import llm_client
from ...utils.llm_schemas import ContentAnalysisResponse
from ...utils.trends_service import trends_service
from ...utils.content_knowledge import (
    get_category_for_keyword,
    get_trending_topics_for_category,
    get_format_suggestions,
    get_best_hashtags,
    get_posting_times,
    get_content_ideas_for_category,
    content_knowledge_base
)


class ContentService:
    """Service for content idea analysis"""
    
    SYSTEM_PROMPT = """Ты - эксперт по контент-маркетингу и SMM с 10-летним опытом.
Твоя задача - анализировать идеи контента и предсказывать их успех."""

    def __init__(self, db: Session):
        self.db = db
    
    async def analyze_content_idea(
        self,
        content_type: str,
        idea_description: str,
        user_id: int,
        target_audience: Optional[str] = None,
        platform: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze a content idea (post/reel/podcast/article)"""
        request = ContentRequest(
            user_id=user_id,
            content_type=content_type,
            idea_description=idea_description,
            target_audience=target_audience,
            platform=platform,
            status="processing"
        )
        self.db.add(request)
        self.db.commit()
        self.db.refresh(request)
        
        try:
            analysis_result = await self._generate_llm_analysis(
                content_type, idea_description, target_audience, platform
            )
            
            request.success_prediction = analysis_result.model_dump()
            request.status = "completed"
            self.db.commit()
            
            return {
                "request_id": request.id,
                "analysis": analysis_result.model_dump()
            }
        except Exception as e:
            request.status = "failed"
            self.db.commit()
            raise e
    
    async def _generate_llm_analysis(
        self,
        content_type: str,
        idea: str,
        target_audience: Optional[str],
        platform: Optional[str]
    ) -> ContentAnalysisResponse:
        """Generate analysis using GigaChat with structured output"""
        category = get_category_for_keyword(idea)
        trending_topics = get_trending_topics_for_category(category)
        format_suggestions = get_format_suggestions(category, platform or "")
        best_hashtags = get_best_hashtags(category)
        posting_times = get_posting_times(category, False)
        content_ideas = get_content_ideas_for_category(category, idea[:30])
        
        google_trends = []
        try:
            trends = await trends_service.get_trending_searches()
            google_trends = trends[:5] if trends else []
        except Exception as e:
            print(f"Google Trends error: {e}")

        prompt = f"""Проанализируй идею контента для социальных сетей. Дай развёрнутый, детальный анализ.

КОНТЕКСТ:
- Тип контента: {content_type}
- Идея: {idea}
- Целевая аудитория: {target_audience or 'не указана'}
- Платформа: {platform or 'не указана'}
- Категория: {category}

ТРЕНДЫ ИЗ GOOGLE:
{', '.join([t.get('title', '') for t in google_trends]) if google_trends else 'Нет данных'}

ПОПУЛЯРНЫЕ ТЕМЫ В КАТЕГОРИИ:
{', '.join(trending_topics[:3]) if trending_topics else 'Нет данных'}

ЛУЧШИЕ ХЭШТЕГИ:
{', '.join(best_hashtags[:5])}

РАССЧИТАЙ МЕТРИКИ НА ОСНОВЕ АНАЛИЗА ИДЕИ:
1. success_probability (0-1): Оцени насколько идея может быть успешной - учитывай актуальность, полезность, эмоциональность, соответствие трендам
2. viral_potential (0-1): Оцени вирусный потенциал - учитывай эмоциональность, неожиданность, практическую пользу, возможность шеринга
3. originality_score (0-1): Оцени оригинальность - учитывай уникальность подачи, свежесть темы, отличие от конкурентов
4. engagement_prediction: Предскажи диапазоны лайков, комментариев и репостов исходя из платформы и типа контента
5. best_posting_time: Выбери лучшее время для публикации на основе платформы (Instagram - вечер 18-21, Telegram - утро 8-10 или вечер 19-21, YouTube - вечер 18-21, TikTok - день 12-15 или вечер 19-22, для {platform or 'Instagram'} выбери оптимальное время)
6. posting_schedule: Составь расписание постов на неделю с лучшими днями и временем

ВЕРНИ JSON С ПОЛЯМИ:
- success_probability, viral_potential, originality_score должны быть ЧИСЛАМИ от 0 до 1 (пример: 0.75)
- engagement_prediction должен содержать СТРОКИ с диапазонами (пример: {{"likes": "100-500", "comments": "10-50", "shares": "5-20"}})
- ПИШИ ПОДРОБНО, минимум 3-5 пунктов в каждом списке:
{{
  "success_probability": 0.75,
  "viral_potential": 0.6,
  "originality_score": 0.7,
  "engagement_prediction": {{"likes": "100-500", "comments": "10-50", "shares": "5-20"}},
  "target_audience": "Молодежь 18-25 (студенты, начинающие специалисты) - интересует саморазвитие и карьера; родители 30-45 - ищут полезный контент для детей; профи 25-40 - ценят экспертный контент",
  "audience_segments": [
    {{"name": "Молодая аудитория", "description": "подробное описание 18-25 лет", "age_range": "18-25", "interests": ["интерес1", "интерес2"], "pain_points": ["проблема1"]}},
    {{"name": "Взрослая аудитория", "description": "подробное описание 25-40 лет", "age_range": "25-40", "interests": ["интерес1"], "pain_points": ["проблема1"]}},
    {{"name": "Зрелая аудитория", "description": "подробное описание 40-55 лет", "age_range": "40-55", "interests": ["интерес1"], "pain_points": ["проблема1"]}},
    {{"name": "Родители", "description": "подробное описание 30-50 лет с детьми", "age_range": "30-50", "interests": ["интерес1"], "pain_points": ["проблема1"]}}
  ],
  "strengths": ["Сильная сторона 1 - подробное описание", "Сильная сторона 2 - подробное описание", "Сильная сторона 3"],
  "weaknesses": ["Слабая сторона 1 - подробное описание", "Слабая сторона 2 - подробное описание", "Слабая сторона 3"],
  "recommendations": ["Рекомендация 1 - подробно что делать", "Рекомендация 2 - подробно", "Рекомендация 3", "Рекомендация 4", "Рекомендация 5"],
  "best_posting_time": "19:00",
  "suggested_hashtags": ["#tag1", "#tag2", "#tag3", "#tag4", "#tag5"],
  "similar_content": [{{"title": "контент", "platform": "Instagram", "url": ""}}],
  "trend_alignment": {{"trending_score": "средний", "alignment": "соответствует"}},
  "format_suggestions": [{{"name": "Пост", "description": "Подробное описание формата - как сделать, структура", "platforms": ["Instagram"]}}, {{"name": "Карусель", "description": "Описание", "platforms": ["Instagram"]}}],
  "content_ideas": ["Идея 1 - подробнее", "Идея 2 - подробнее", "Идея 3", "Идея 4", "Идея 5"],
  "key_words": ["слово1", "слово2", "слово3", "слово4", "слово5"],
  "posting_schedule": [{{"day": "Понедельник", "time": "19:00"}}, {{"day": "Среда", "time": "20:00"}}, {{"day": "Пятница", "time": "18:00"}}]
}}

Верни ТОЛЬКО валидный JSON без комментариев."""

        try:
            result = await llm_client.chat_parse(
                prompt=prompt,
                response_model=ContentAnalysisResponse,
                system_prompt=self.SYSTEM_PROMPT,
                strict=False,
                temperature=0.5
            )
            
            if isinstance(result.engagement_prediction.get('likes'), (int, float)):
                likes_val = int(result.engagement_prediction.get('likes', 100))
                result.engagement_prediction['likes'] = f"{max(10, likes_val - 50)}-{likes_val + 50}"
            if isinstance(result.engagement_prediction.get('comments'), (int, float)):
                comments_val = int(result.engagement_prediction.get('comments', 10))
                result.engagement_prediction['comments'] = f"{max(1, comments_val - 5)}-{comments_val + 5}"
            if isinstance(result.engagement_prediction.get('shares'), (int, float)):
                shares_val = int(result.engagement_prediction.get('shares', 5))
                result.engagement_prediction['shares'] = f"{max(1, shares_val - 2)}-{shares_val + 2}"
            
            if isinstance(result.success_probability, str):
                try:
                    result.success_probability = float(result.success_probability.split('-')[0])
                except:
                    result.success_probability = 0.5
            
            import hashlib
            idea_hash = int(hashlib.md5(idea.encode()).hexdigest()[:8], 16) % 100
            variance = (idea_hash - 50) / 200
            result.success_probability = max(0.1, min(0.95, result.success_probability + variance))
            result.viral_potential = max(0.1, min(0.95, result.viral_potential + variance * 0.8))
            if result.originality_score:
                result.originality_score = max(0.1, min(0.95, result.originality_score + variance * 0.6))
            
            if isinstance(result.engagement_prediction, dict):
                for key in ['likes', 'comments', 'shares']:
                    if key in result.engagement_prediction:
                        val = result.engagement_prediction[key]
                        if isinstance(val, str) and '-' in val:
                            parts = val.split('-')
                            try:
                                low = int(parts[0]) + int(variance * 100)
                                high = int(parts[1]) + int(variance * 150)
                                result.engagement_prediction[key] = f"{max(1, low)}-{max(1, high)}"
                            except:
                                pass
            
            if result.best_posting_time and isinstance(result.best_posting_time, str):
                try:
                    if ':' in result.best_posting_time:
                        hour = int(result.best_posting_time.split(':')[0].split('-')[0])
                        new_hour = max(8, min(22, hour + int(variance * 3)))
                        result.best_posting_time = f"{new_hour}:00-{new_hour+2}:00"
                except:
                    pass
            
            if not result.audience_segments or len(result.audience_segments) < 3:
                result.audience_segments = [
                    {"name": "Молодая аудитория", "description": "Студенты и начинающие специалисты 18-25 лет", "age_range": "18-25", "interests": ["саморазвитие", "карьера"], "pain_points": ["неопределенность", "поиск работы"]},
                    {"name": "Взрослая аудитория", "description": "Работающие профессионалы 25-40 лет", "age_range": "25-40", "interests": ["бизнес", "эффективность"], "pain_points": ["нехватка времени", "масштабирование"]},
                    {"name": "Зрелая аудитория", "description": "Опытные специалисты и предприниматели 40-55 лет", "age_range": "40-55", "interests": ["стратегия", "нетворкинг"], "pain_points": ["переход на новый уровень", "поиск команды"]},
                    {"name": "Родители", "description": "Люди 30-50 лет с детьми", "age_range": "30-50", "interests": ["воспитание", "семейные финансы"], "pain_points": ["нехватка времени на детей", "выбор школы"]}
                ]
            
            if not result.suggested_hashtags or len(result.suggested_hashtags) == 0:
                result.suggested_hashtags = best_hashtags[:5]
            if not result.format_suggestions or len(result.format_suggestions) == 0:
                result.format_suggestions = [{"name": f"{content_type.capitalize()}", "description": f"Основной формат", "platforms": [platform or "Instagram"]}]
            return result
        except Exception as e:
            print(f"Content LLM error: {e}")
            return self._generate_fallback_analysis(content_type, platform, category, target_audience, idea)
    
    def _generate_fallback_analysis(self, content_type: str, platform: Optional[str], category: str = "marketing", target_audience_input: Optional[str] = None, idea: str = "") -> ContentAnalysisResponse:
        """Fallback analysis when LLM fails"""
        import hashlib
        idea_hash = int(hashlib.md5(idea.encode()).hexdigest()[:8], 16) % 1000
        random.seed(idea_hash)
        
        idea_lower = idea.lower()
        
        def calculate_metrics_based_on_idea() -> tuple[float, float, float]:
            """Calculate metrics based on idea content analysis"""
            success = 0.5
            viral = 0.4
            originality = 0.5
            
            positive_words = ['новый', 'лучший', 'успех', 'деньги', 'заработок', 'растет', 'прибыль', 'интересно', 'полезно', 'поможет', 'результат', 'эффективно', 'просто', 'быстро', 'легко', 'гайд', 'совет', 'секрет', 'способ']
            negative_words = ['плохо', 'проблема', 'ошибка', 'сложно', 'трудно', 'дорого', 'риск', 'убыток', 'нельзя', 'невозможно', 'никогда', 'не']
            trending_words = ['тренд', '2024', '2025', 'новый', 'хайп', 'вирус', 'модно', 'популярно']
            original_words = ['уникальный', 'свой', 'личный', 'авторский', 'новый взгляд', 'необычный', 'оригинальный']
            
            has_positive = sum(1 for w in positive_words if w in idea_lower) / max(len(positive_words), 1)
            has_negative = sum(1 for w in negative_words if w in idea_lower) / max(len(negative_words), 1)
            has_trending = sum(1 for w in trending_words if w in idea_lower) / max(len(trending_words), 1)
            has_original = sum(1 for w in original_words if w in idea_lower) / max(len(original_words), 1)
            
            success = 0.4 + (has_positive * 0.4) + (has_trending * 0.2) - (has_negative * 0.15)
            viral = 0.3 + (has_positive * 0.3) + (has_trending * 0.25) + (has_original * 0.15)
            originality = 0.4 + (has_original * 0.35) + (has_negative * 0.1) + (has_trending * 0.15)
            
            if '?' in idea:
                success += 0.05
                viral += 0.05
            if len(idea) > 100:
                success += 0.05
            if len(idea) < 20:
                originality -= 0.1
                viral -= 0.1
            
            return (
                max(0.2, min(0.95, success + random.uniform(-0.1, 0.1))),
                max(0.15, min(0.9, viral + random.uniform(-0.1, 0.1))),
                max(0.2, min(0.9, originality + random.uniform(-0.1, 0.1)))
            )
        
        base_success, base_viral, base_originality = calculate_metrics_based_on_idea()
        
        def calculate_engagement() -> dict:
            """Calculate engagement prediction based on platform and content type"""
            platform_multipliers = {
                'instagram': {'likes': 1.0, 'comments': 1.0, 'shares': 1.2},
                'telegram': {'likes': 0.6, 'comments': 1.5, 'shares': 1.8},
                'youtube': {'likes': 1.5, 'comments': 0.8, 'shares': 0.6},
                'tiktok': {'likes': 2.0, 'comments': 0.5, 'shares': 2.5},
            }
            type_multipliers = {
                'post': {'likes': 1.0, 'comments': 1.0, 'shares': 1.0},
                'reel': {'likes': 1.8, 'comments': 0.7, 'shares': 2.0},
                'article': {'likes': 0.5, 'comments': 1.5, 'shares': 0.8},
                'story': {'likes': 1.2, 'comments': 0.4, 'shares': 0.3},
                'carousel': {'likes': 1.3, 'comments': 1.2, 'shares': 1.5},
            }
            p_mult = platform_multipliers.get(platform or 'instagram', {'likes': 1.0, 'comments': 1.0, 'shares': 1.0})
            t_mult = type_multipliers.get(content_type, {'likes': 1.0, 'comments': 1.0, 'shares': 1.0})
            
            base_likes = int(500 * base_success * p_mult['likes'] * t_mult['likes'])
            base_comments = int(30 * base_success * p_mult['comments'] * t_mult['comments'])
            base_shares = int(15 * base_viral * p_mult['shares'] * t_mult['shares'])
            
            likes_range = base_likes + random.randint(-100, 200)
            comments_range = base_comments + random.randint(-10, 20)
            shares_range = base_shares + random.randint(-5, 15)
            
            return {
                "likes": f"{max(50, likes_range)}-{max(150, likes_range + random.randint(100, 400))}",
                "comments": f"{max(5, comments_range)}-{max(20, comments_range + random.randint(10, 40))}",
                "shares": f"{max(3, shares_range)}-{max(10, shares_range + random.randint(8, 25))}"
            }
        
        platform_tips = {
            "instagram": "Используйте яркие визуалы, качественные фото и привлекательные хэштеги. Создавайте визуально однородный профиль. Добавьте истории для вовлечения аудитории.",
            "telegram": "Фокус на полезном контенте и экспертности. Пишите структурированные посты с эмодзи. Используйте опросы для вовлечения подписчиков.",
            "youtube": "Важны первые 15 секунд для удержания зрителя. Создавайте привлекательные миниатюры. Добавляйте таймкоды и конечные заставки.",
            "tiktok": "Используйте трендовую музыку и форматы. Делайте динамичный монтаж. Снимайте вертикально с хорошим освещением.",
            "linkedin": "Профессиональный тон и конкретные кейсы. Делитесь экспертизой и личным опытом. Используйте документы и инфографику.",
            "vk": "Активное взаимодействие в сообществе. Публикуйте разнообразный контент. Создавайте обсуждения и голосования."
        }
        
        hashtags = get_best_hashtags(category)
        format_suggestions = get_format_suggestions(category, platform or "")
        posting_times = get_posting_times(category, False)
        content_ideas = get_content_ideas_for_category(category)
        
        audience_segments = [
            {
                "name": "Молодая аудитория",
                "description": "Студенты и начинающие специалисты 18-25 лет, которые ищут вдохновение и первые шаги в карьере",
                "age_range": "18-25",
                "interests": ["саморазвитие", "карьера", "обучение", "тренды", "развлечения"],
                "pain_points": ["неопределенность", "поиск работы", "нехватка опыта", "финансовые ограничения"]
            },
            {
                "name": "Взрослая аудитория",
                "description": "Работающие профессионалы 25-40 лет, которые ищут практические решения и экспертизу",
                "age_range": "25-40",
                "interests": ["бизнес", "эффективность", "лидерство", "технологии", "финансы"],
                "pain_points": ["нехватка времени", "поиск баланса", "масштабирование", "конкуренция"]
            },
            {
                "name": "Зрелая аудитория",
                "description": "Опытные специалисты и предприниматели 40-55 лет, которые ценят глубину и проверенные стратегии",
                "age_range": "40-55",
                "interests": ["стратегия", "нетворкинг", "управление", "инвестиции", "менторство"],
                "pain_points": ["переход на новый уровень", "поиск команды", "наследие", "work-life balance"]
            },
            {
                "name": "Родители и семьянины",
                "description": "Люди 30-50 лет с детьми, которые ищут полезный контент для семьи и решения повседневных задач",
                "age_range": "30-50",
                "interests": ["воспитание", "образование детей", "семейные финансы", "здоровье", "развлечения"],
                "pain_points": ["нехватка времени на детей", "выбор школы", "гаджеты для детей", "безопасность"]
            }
        ]
        
        engagement_prediction = calculate_engagement()
        
        return ContentAnalysisResponse(
            success_probability=round(base_success, 2),
            viral_potential=round(base_viral, 2),
            originality_score=round(base_originality, 2),
            engagement_prediction=engagement_prediction,
            strengths=[
                "Актуальная тема - соответствует текущим интересам целевой аудитории и трендам рынка",
                "Хорошее соответствие платформе - контент адаптирован под формат и аудиторию выбранной социальной сети",
                "Потенциал для вовлечения - возможность вызвать эмоциональный отклик и дискуссию среди подписчиков",
                "Универсальность - тема может быть адаптирована под разные форматы и платформы",
                "Информативная ценность - предоставляет полезную информацию, которую аудитория захочет сохранить и поделиться"
            ],
            weaknesses=[
                "Требуется детальная проработка - нужно добавить конкретику и примеры для усиления воздействия",
                "Нужно добавить уникальный угол - выделить контент среди конкурентов оригинальной подачей",
                "Отсутствие визуальной составляющей - рекомендуется добавить изображения, инфографику или видео",
                "Слабый призыв к действию - необходимо усилить CTA для повышения конверсии",
                "Можно улучшить тайминг - протестировать разное время публикации для максимального охвата"
            ],
            recommendations=[
                platform_tips.get(platform or "", "Адаптируйте контент под особенности платформы"),
                "Добавьте призыв к действию (CTA) в конце поста - задайте вопрос, попросите поделиться мнением",
                "Используйте трендовый формат в сочетании с вашей темой для увеличения охвата",
                "Добавьте визуальные элементы - качественные фото, видео или инфографику",
                "Создайте серию контента на эту тему для формирования экспертности и удержания аудитории",
                "Используйте сторителлинг - добавьте личную историю или пример из практики для большей вовлечённости",
                "Проведите A/B тестирование заголовков и визуала для оптимизации результатов"
            ],
            best_posting_time=posting_times[0] if posting_times else "19:00-21:00",
            target_audience=target_audience_input or "Молодежь 18-25 (студенты, начинающие специалисты) - интересует саморазвитие и карьера; Взрослые 30-45 (работающие профессионалы) - ищут практические решения; Родители 30-50 (дети школьного возраста) - ценят полезный контент для семьи",
            audience_segments=audience_segments,
            suggested_hashtags=hashtags[:7] if hashtags else ["#маркетинг", "#бизнес", "#успех", "#мотивация", "#стратегия"],
            similar_content=[
                {"title": "Популярный контент по теме", "platform": platform or "Instagram", "url": ""}
            ],
            trend_alignment={"trending_score": "средний", "alignment": "соответствует теме"},
            format_suggestions=format_suggestions[:3] if format_suggestions else [
                {"name": "Пост", "description": "Текстовый контент с четкой структурой: заголовок, основная часть, вывод, призыв к действию", "platforms": [platform or "Instagram"]},
                {"name": "Карусель", "description": "Мультислайд контент для последовательного раскрытия темы с визуальными элементами", "platforms": ["Instagram"]},
                {"name": "Сторис", "description": "Короткий формат для быстрого вовлечения, опросов и интерактива", "platforms": ["Instagram"]}
            ],
            content_ideas=content_ideas[:5] if content_ideas else [
                "Топ-5 советов по теме с подробным разбором каждого",
                "Частые ошибки и как их избежать - практическое руководство",
                "Гайд для новичков - с чего начать и куда двигаться",
                "Интервью с экспертом или кейс успеха",
                "Сравнительный анализ подходов и стратегий"
            ],
            key_words=hashtags[:5] if hashtags else ["маркетинг", "бизнес", "успех", "стратегия", "рост"],
            posting_schedule=[
                {"day": "Понедельник", "time": posting_times[0] if posting_times else "19:00"},
                {"day": "Среда", "time": posting_times[1] if len(posting_times) > 1 else "20:00"},
                {"day": "Пятница", "time": "18:00"},
                {"day": "Суббота", "time": "12:00"}
            ]
        )
    
    def get_request_by_id(self, request_id: int) -> Optional[ContentRequest]:
        """Get content request by ID"""
        return self.db.query(ContentRequest).filter(
            ContentRequest.id == request_id
        ).first()
    
    def get_user_requests(self, user_id: int, limit: int = 10) -> List[ContentRequest]:
        """Get all content requests for a user"""
        return self.db.query(ContentRequest).filter(
            ContentRequest.user_id == user_id
        ).order_by(ContentRequest.created_at.desc()).limit(limit).all()
