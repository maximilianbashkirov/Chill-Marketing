import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from ...models.models import DotAnalysisRequest
from ...utils.marketing_models import MarketingModelsLibrary
from ...utils.llm_client import llm_client

logger = logging.getLogger(__name__)


class DotAnalysisService:
    """Service for selecting and applying marketing models using 2-step LLM pipeline"""

    SYSTEM_PROMPT = """Ты — эксперт по маркетинговым моделям и стратегическому анализу.
Твоя задача — выбирать наиболее подходящие фреймворки под конкретный бизнес-кейс и применять их.
Отвечай ТОЛЬКО на русском языке. Все JSON поля заполняй на русском.
Только валидный JSON, без пояснений до или после."""

    SELECT_PROMPT = """Дан кейс клиента: "{case_context}"
Индустрия: {industry}

Вот список маркетинговых фреймворков с оценкой релевантности:

{models_text}

Выбери 3-4 НАИБОЛЕЕ ПОДХОДЯЩИХ фреймворка для анализа этого кейса.
Учитывай индустрию, описание кейса и специализацию каждого фреймворка.

Для КАЖДОГО выбранного фреймворка укажи reason — развёрнутое описание (4-5 предложений):
- Почему этот фреймворк подходит для данного кейса
- Какие именно аспекты бизнеса он поможет проанализировать
- Какие конкретные KPI или метрики нужно оценить
- Какой результат даст применение (рост продаж, оптимизация расходов и т.п.)

Верни JSON:
{{
  "selected": [
    {{
      "key": "ТОЧНЫЙ_КЛЮЧ_ИЗ_СПИСКА_ВЫШЕ_В_КВАДРАТНЫХ_СКОБКАХ",
      "reason": "Развёрнутое обоснование выбора (4-5 предложений на русском, с конкретными отсылками к кейсу)"
    }}
  ]
}}

ВАЖНО: ключ в поле "key" должен быть ТОЧНО таким же, как в квадратных скобках [KEY] в списке выше.
Не используй название фреймворка — используй его ключ.
Выбери 3-4, не больше. Только существующие ключи из списка выше."""

    def __init__(self, db: Session):
        self.db = db
        self.models_library = MarketingModelsLibrary()

    async def analyze_case(
        self,
        case_context: str,
        industry: str,
        user_id: int
    ) -> Dict[str, Any]:
        request = DotAnalysisRequest(
            user_id=user_id,
            case_context=case_context,
            status="processing"
        )
        self.db.add(request)
        self.db.commit()
        self.db.refresh(request)

        try:
            # Step 1: keyword matching → top 15
            relevant = self.models_library.find_relevant_models(f"{case_context} {industry}")
            top_models = relevant[:15] if len(relevant) >= 15 else relevant

            # Step 2: LLM selects 3-4 from top 15
            selected_keys = await self._llm_select_models(case_context, industry, top_models)

            # Step 3: LLM analyzes each selected model in detail
            analyses = await self._llm_analyze_all(case_context, industry, selected_keys)

            request.selected_models = [m["key"] for m in selected_keys]
            request.detailed_analysis = analyses
            request.status = "completed"
            self.db.commit()

            return {
                "request_id": request.id,
                "industry": industry,
                "selected_models": [
                    {
                        "key": m["key"],
                        "name": m["model"]["name"],
                        "category": m["model"]["category"],
                        "description": m["model"]["description"],
                        "reason": m.get("reason", ""),
                    }
                    for m in selected_keys
                ],
                "analyses": analyses,
            }
        except Exception as e:
            request.status = "failed"
            self.db.commit()
            raise e

    async def _llm_select_models(
        self, case_context: str, industry: str, models: List[Dict]
    ) -> List[Dict]:
        """LLM выбирает 3-4 фреймворка из списка"""
        models_text = self.models_library.get_models_for_llm_prompt(models)

        prompt = self.SELECT_PROMPT.format(
            case_context=case_context,
            industry=industry,
            models_text=models_text,
        )

        result = await llm_client.chat_json(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
            temperature=0.4,
        )

        if "error" in result:
            # Fallback: берём топ-4 по keyword scoring
            return [
                {"key": m["key"], "model": m["model"], "reason": "Автоматический выбор на основе ключевых слов"}
                for m in models[:4]
            ]

        selected = result.get("selected", [])
        if not selected:
            return [
                {"key": m["key"], "model": m["model"], "reason": "Автоматический выбор"}
                for m in models[:4]
            ]

        # Мапим выбранные ключи к полным данным модели
        model_map = {m["key"]: m for m in models}
        enriched = []
        for s in selected[:4]:
            key = s.get("key", "")
            if key in model_map:
                enriched.append({
                    "key": key,
                    "model": model_map[key]["model"],
                    "reason": s.get("reason", ""),
                })

        # Если LLM вернула меньше 3 — дополняем из топа
        if len(enriched) < 3:
            existing_keys = {e["key"] for e in enriched}
            for m in models:
                if m["key"] not in existing_keys:
                    enriched.append({
                        "key": m["key"],
                        "model": m["model"],
                        "reason": "Дополнительная рекомендация",
                    })
                    if len(enriched) >= 4:
                        break

        return enriched[:4]

    async def _llm_analyze_all(
        self, case_context: str, industry: str, selected: List[Dict]
    ) -> List[Dict]:
        """Параллельные individual LLM-вызовы для каждого фреймворка"""
        templates = self.models_library.get_model_templates([s["key"] for s in selected])

        async def analyze_one(s: Dict) -> Dict:
            model = s["model"]
            template = templates.get(s["key"], "{}")
            reason = s.get("reason", "")
            analysis = await self._llm_analyze_single(
                case_context, industry, model, template, reason
            )
            return {
                "key": s["key"],
                "name": model["name"],
                "category": model.get("category", ""),
                "description": model["description"],
                "analysis": analysis,
                "template_structure": template,
            }

        tasks = [analyze_one(s) for s in selected]
        return await asyncio.gather(*tasks)

    async def _llm_analyze_single(
        self, case_context: str, industry: str,
        model: Dict[str, Any], template: str, reason: str
    ) -> Dict[str, Any]:
        """LLM применяет один фреймворк к кейсу"""
        prompt = f"""Примени фреймворк "{model['name']}" к следующему кейсу.
Сделай максимально подробный и развёрнутый анализ.

Кейс: {case_context}
Индустрия: {industry}
Описание фреймворка: {model['description']}
Почему выбран: {reason}

ВАЖНЕЙШИЕ ТРЕБОВАНИЯ:
1. ЗАПРЕЩЕНО использовать дефисы вместо пробелов: пиши «увеличить бюджет для блогера 1», а не «увеличить-бюджет-для-блогера-1». Никаких слогов, транслита, кодирования.

2. Заполни ВСЕ поля структуры — никаких пустых массивов, null или прочерков.

3. Минимум 3-5 элементов в каждом массиве, для ключевых (рекомендации, каналы, метрики) — 5-8.

4. Конкретные цифры: рубли, проценты, сроки в месяцах/днях, названия инструментов и каналов. ЗАПРЕЩЕНО использовать подчёркивания в числах (пиши 1200000, а не 1_200_000).

5. Каждую рекомендацию распиши: действие → как реализовать → ожидаемый эффект (цифры) → сроки → бюджет.

ВСЁ на русском языке, естественно, без шаблонных фраз.

Требуемая структура JSON:
{template}

Только валидный JSON, без пояснений."""

        result = await llm_client.chat_json(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
            temperature=0.4,
            max_tokens=4000,
        )

        if "error" in result:
            logger.warning(f"Individual analysis for '{model['name']}' failed: {result.get('error')}")
            return self._generate_fallback_analysis(case_context, model, reason)

        return result

    def _generate_fallback_analysis(
        self, case_context: str, model: Dict[str, Any], reason: str
    ) -> Dict[str, Any]:
        """Генерация подробного шаблонного анализа при ошибке LLM"""
        name = model["name"]
        desc = model.get("description", "")
        return {
            "_fallback": True,
            "model_name": name,
            "description": desc,
            "reason": reason,
            "case_context": case_context,
            "findings": [
                f"На основе вашего кейса: {case_context[:150]}...",
                f"Фреймворк {name} позволяет структурировать анализ проблемной области",
                f"Индустрия: {model.get('category', 'не указана')} — специфичные метрики и тренды учтены",
                f"Ключевая задача: {desc[:200]}",
            ],
            "metrics": {
                "current_state": "Требуется сбор исходных данных",
                "target_metrics": model.get("metrics", []),
                "kpi_list": [
                    "Конверсия",
                    "Средний чек (AOV)",
                    "Стоимость привлечения клиента (CAC)",
                    "Пожизненная ценность (LTV)",
                    "ROAS / ROMI",
                ],
            },
            "recommendations": [
                {
                    "action": f"Провести {name}",
                    "description": f"Детальный анализ по методологии {name}. {desc[:150]}",
                    "expected_effect": "Структурирование проблем и точек роста",
                    "timeline": "1-2 недели",
                },
                {
                    "action": "Сбор данных для анализа",
                    "description": "Собрать статистику по продажам, расходам, трафику, конверсиям за последние 3-6 месяцев",
                    "expected_effect": "Фактологическая база для принятия решений",
                    "timeline": "3-5 дней",
                },
                {
                    "action": "Разработка плана действий",
                    "description": "На основе результатов анализа сформировать дорожную карту с конкретными шагами, сроками и ответственными",
                    "expected_effect": "Прозрачный план с измеримыми результатами",
                    "timeline": "1 неделя",
                },
                {
                    "action": "Внедрение и мониторинг",
                    "description": "Реализовать предложенные мероприятия, настроить отслеживание KPI и регулярную отчётность",
                    "expected_effect": "Рост эффективности бизнес-процессов",
                    "timeline": "2-4 недели",
                },
            ],
            "risks": [
                "Неполнота исходных данных может снизить точность анализа",
                "Изменения рыночной ситуации могут потребовать корректировки плана",
                "Недостаточная вовлечённость команды в процесс изменений",
            ],
            "conclusion": f"Для вашего кейса рекомендуется применить {name}. "
                          f"Этот анализ поможет {desc[:200].lower()}. "
                          f"Рекомендуется начать со сбора данных и первичного аудита текущей ситуации — "
                          f"это займёт 1-2 недели и позволит получить объективную картину для принятия решений.",
        }

    def get_request_by_id(self, request_id: int) -> Optional[DotAnalysisRequest]:
        return self.db.query(DotAnalysisRequest).filter(
            DotAnalysisRequest.id == request_id
        ).first()

    def get_user_requests(self, user_id: int, limit: int = 10) -> List[DotAnalysisRequest]:
        return self.db.query(DotAnalysisRequest).filter(
            DotAnalysisRequest.user_id == user_id
        ).order_by(DotAnalysisRequest.created_at.desc()).limit(limit).all()

    def get_all_models(self) -> List[Dict[str, Any]]:
        return self.models_library.get_all_models()
