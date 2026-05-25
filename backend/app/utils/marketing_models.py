from typing import List, Dict, Any


TEMPLATES: Dict[str, str] = {}

def _t(key: str, t: str) -> str:
    TEMPLATES[key] = t
    return t

# ── Шаблоны вывода для LLM ──────────────────────────────────────
# (определяются здесь же для удобства)

TEMPLATES_RAW = {
    "SWOT": _t("SWOT", """{
  "strengths": [
    "внутренняя сильная сторона 1 — подробное описание, цифры",
    "ключевое преимущество перед конкурентами",
    "уникальные ресурсы и компетенции"
  ],
  "weaknesses": [
    "внутренняя слабость 1 — влияние на бизнес, цифры",
    "ограничения и недостатки текущей модели"
  ],
  "opportunities": [
    "внешняя возможность 1 — потенциал роста, ёмкость",
    "рыночные тренды и новые сегменты"
  ],
  "threats": [
    "внешняя угроза 1 — уровень влияния, вероятность",
    "действия конкурентов, изменения регуляторики"
  ],
  "conclusion": "Общий вывод: как использовать сильные стороны и возможности, минимизируя слабости и угрозы",
  "strategy_matrix": {
    "so_strategies": ["стратегия 1: использовать сильные стороны для реализации возможностей"],
    "wo_strategies": ["стратегия 1: преодолеть слабости за счёт возможностей"],
    "st_strategies": ["стратегия 1: использовать сильные стороны для нейтрализации угроз"],
    "wt_strategies": ["стратегия 1: минимизировать слабости и избегать угроз"]
  },
  "recommendations": [
    {"action": "что сделать", "priority": "высокий/средний/низкий", "timeline": "срок", "expected_effect": "ожидаемый результат с цифрами", "budget": "бюджет"}
  ]
}"""),
    "PESTLE": _t("PESTLE", """{
  "political": ["политический фактор 1", ...],
  "economic": ["экономический фактор 1", ...],
  "social": ["социальный фактор 1", ...],
  "technological": ["технологический фактор 1", ...],
  "legal": ["правовой фактор 1", ...],
  "environmental": ["экологический фактор 1", ...],
  "conclusion": "Общий вывод",
  "key_risks": ["основной риск 1", ...]
}"""),
    "AARRR": _t("AARRR", """{
  "acquisition": {
    "channels": [
      {"channel": "канал 1", "visitors": "число", "cost": "руб", "cac": "руб", "conversion_to_activation": "%", "quality_score": "оценка"}
    ],
    "total_cost": "общий бюджет на привлечение",
    "avg_cac": "средняя стоимость привлечения",
    "recommendations": [
      {"action": "что сделать", "expected_effect": "эффект с цифрами", "timeline": "срок", "priority": "приоритет"}
    ]
  },
  "activation": {
    "definition": "что считается успешной активацией",
    "current_rate": "текущий % активации",
    "target_rate": "целевой %",
    "funnel_steps": ["шаг 1 — конверсия X%", "шаг 2 — конверсия Y%"],
    "dropoff_points": ["где и сколько теряем"],
    "recommendations": [
      {"action": "что изменить", "expected_impact": "рост активации на X%", "effort": "усилия"}
    ]
  },
  "retention": {
    "current_rate": "текущий % удержания",
    "target_rate": "целевой %",
    "cohort_analysis": "анализ когорт: retention по неделям/месяцам",
    "churn_rate": "% оттока",
    "lifetime": "средний срок жизни клиента",
    "recommendations": [
      {"action": "что внедрить для повышения удержания", "expected_effect": "снижение оттока на X%", "timeline": "срок"}
    ]
  },
  "revenue": {
    "arpu": "средний доход с пользователя",
    "ltv": "LTV в рублях",
    "ltv_cac_ratio": "соотношение",
    "avg_check": "средний чек",
    "repeat_purchase_rate": "% повторных покупок",
    "revenue_breakdown": {"product_1": "доля", "product_2": "доля"},
    "recommendations": [
      {"action": "как увеличить LTV", "expected_effect": "рост на X%", "timeline": "срок"}
    ]
  },
  "referral": {
    "virality_coefficient": "K-фактор",
    "current_referral_rate": "% клиентов, которые приводят друзей",
    "recommended_program": "описание реферальной программы",
    "recommendations": [
      {"action": "как усилить виральность", "expected_effect": "рост K-фактора на X"}
    ]
  },
  "bottlenecks": [
    {"stage": "Acquisition/Activation/...", "issue": "описание проблемы", "impact": "влияние на бизнес", "priority": "приоритет"}
  ]
}"""),
    "JTBD": _t("JTBD", """{
  "main_job": "Основная работа, которую нанимают клиент",
  "functional_jobs": ["функциональная задача 1", ...],
  "emotional_jobs": ["эмоциональная задача 1", ...],
  "social_jobs": ["социальная задача 1", ...],
  "pains": ["боль 1", ...],
  "gains": ["желаемый результат 1", ...],
  "context": "Контекст использования",
  "competitors_for_job": ["конкурентный способ решения 1", ...],
  "recommendations": ["рекомендация 1 по улучшению", ...]
}"""),
    "CJM": _t("CJM", """{
  "stages": [
    {
      "stage": "Осознание",
      "description": "как клиент узнаёт о продукте",
      "touchpoints": ["точка контакта 1 — описание", "точка контакта 2 — описание"],
      "channels": ["канал 1", "канал 2"],
      "customer_goal": "что хочет клиент на этом этапе",
      "pain_points": ["боль 1 — описание", "боль 2 — влияние на конверсию"],
      "emotion": "нейтрально/позитивно/негативно",
      "satisfaction": "оценка 1-10",
      "opportunities": ["как улучшить этап", "потенциал роста конверсии на X%"],
      "metrics": {"dropoff": "% потерь", "time_spent": "среднее время", "conversion_to_next": "%"},
      "recommendations": [
        {"action": "что внедрить", "expected_impact": "эффект", "effort": "низкий/средний/высокий", "priority": "приоритет"}
      ]
    }
  ],
  "overall_journey_summary": "Общее описание пути клиента, ключевые инсайты",
  "critical_moments": [
    {"moment": "момент истины 1", "importance": "почему это критично", "current_state": "как сейчас", "gap": "разрыв с идеалом"}
  ],
  "recommendations": [
    {"action": "глобальная рекомендация 1", "expected_effect": "влияние на весь путь", "timeline": "срок", "budget": "бюджет"}
  ]
}"""),
    "4P": _t("4P", """{
  "product": {"description": "текущий продукт", "strengths": [...], "weaknesses": [...], "recommendations": [...]},
  "price": {"strategy": "текущая ценовая стратегия", "range": "диапазон", "elasticity": "...", "recommendations": [...]},
  "place": {"channels": ["канал 1", ...], "coverage": "...", "recommendations": [...]},
  "promotion": {"channels": ["канал 1", ...], "budget": "...", "effectiveness": "...", "recommendations": [...]}
}"""),
    "BCG": _t("BCG", """{
  "stars": ["продукт 1 — высокая доля + высокий рост", ...],
  "cash_cows": ["продукт 1 — высокая доля + низкий рост", ...],
  "question_marks": ["продукт 1 — низкая доля + высокий рост", ...],
  "dogs": ["продукт 1 — низкая доля + низкий рост", ...],
  "recommendations": {"stars": [...], "cash_cows": [...], "question_marks": [...], "dogs": [...]}
}"""),
    "KANO": _t("KANO", """{
  "must_be": ["обязательная характеристика 1", ...],
  "performance": ["линейная характеристика 1", ...],
  "attractive": ["привлекающая характеристика 1", ...],
  "indifferent": ["неважная характеристика 1", ...],
  "reverse": ["вызывающая недовольство 1", ...],
  "prioritization": ["что внедрить в первую очередь", ...]
}"""),
    "UNIT_ECONOMICS": _t("UNIT_ECONOMICS", """{
  "cac": {
    "current_value": "CAC в рублях",
    "breakdown": {"реклама": "руб", "зарплаты_отдела": "руб", "софт": "руб", "прочее": "руб"},
    "by_channel": [
      {"channel": "канал 1", "cac": "руб", "share": "%", "trend": "динамика за месяц"}
    ],
    "target_cac": "целевой CAC",
    "recommendations": [
      {"action": "как снизить CAC", "expected_reduction": "экономия X руб", "timeline": "срок"}
    ]
  },
  "ltv": {
    "current_value": "LTV в рублях",
    "calculation_period": "период расчёта (12/24/36 мес)",
    "avg_check": "средний чек",
    "purchase_frequency": "покупок в месяц/год",
    "retention_rate": "% удержания",
    "gross_margin": "% маржи",
    "by_cohort": "LTV по когортам: значения",
    "projected_ltv": "прогнозный LTV при оптимизации",
    "recommendations": [
      {"action": "как увеличить LTV", "expected_effect": "рост на X руб", "timeline": "срок"}
    ]
  },
  "ltv_cac_ratio": {
    "current": "текущее значение",
    "target": "целевое значение (3+: здоровый бизнес)",
    "assessment": "оценка: отлично/хорошо/требует улучшения/критично"
  },
  "payback_period": {
    "current": "срок окупаемости CAC в месяцах",
    "target": "целевой срок",
    "assessment": "оценка"
  },
  "margin": {
    "current_value": "текущая маржинальность %",
    "by_product": [{"product": "товар 1", "margin": "%", "revenue_share": "%"}],
    "target_margin": "целевая маржинальность",
    "recommendations": [
      {"action": "как повысить маржинальность", "expected_effect": "рост на X п.п.", "timeline": "срок"}
    ]
  },
  "unit_economics_summary": "Развёрнутый вывод: прибыльно/убыточно, что менять в первую очередь",
  "scenarios": [
    {"name": "оптимистичный", "cac": "руб", "ltv": "руб", "ltv_cac": "X", "conditions": "при каких условиях"},
    {"name": "реалистичный", "cac": "руб", "ltv": "руб", "ltv_cac": "X", "conditions": ""},
    {"name": "пессимистичный", "cac": "руб", "ltv": "руб", "ltv_cac": "X", "conditions": ""}
  ]
}"""),
    "LEAN_CANVAS": _t("LEAN_CANVAS", """{
  "problem": ["проблема клиента 1", ...],
  "customer_segments": ["сегмент 1", ...],
  "unique_value_proposition": "УТП",
  "solution": ["решение 1", ...],
  "channels": ["канал 1", ...],
  "revenue_streams": ["источник дохода 1", ...],
  "cost_structure": ["статья расхода 1", ...],
  "key_metrics": ["метрика 1", ...],
  "unfair_advantage": "нечестное преимущество"
}"""),
    "BLUE_OCEAN": _t("BLUE_OCEAN", """{
  "eliminate": ["что исключить из отрасли 1", ...],
  "reduce": ["что снизить 1", ...],
  "raise": ["что повысить 1", ...],
  "create": ["что создать нового 1", ...],
  "strategy_canvas": "Описание текущей и желаемой кривой ценности",
  "blue_ocean_move": "Главная стратегическая рекомендация"
}"""),
    "HOOK_MODEL": _t("HOOK_MODEL", """{
  "trigger": {"external": ["внешний триггер 1", ...], "internal": ["внутренний триггер 1", ...]},
  "action": "целевое действие пользователя",
  "variable_reward": ["награда 1 — предсказуемая?", "награда 2 — неожиданная?"],
  "investment": ["что пользователь вкладывает (время, данные, деньги)", ...],
  "habit_potential": "Оценка потенциала формирования привычки",
  "recommendations": [...]
}"""),
    "FOGG": _t("FOGG", """{
  "motivation": {"level": "высокая/средняя/низкая", "factors": [...], "recommendations": [...]},
  "ability": {"level": "высокая/средняя/низкая", "barriers": [...], "recommendations": [...]},
  "prompt": {"current_triggers": [...], "recommendations": [...]},
  "behavior_formula_analysis": "Анализ B=MAP для текущего кейса",
  "recommendations": ["как повысить мотивацию", "как упростить действие", "как усилить триггеры"]
}"""),
    "BRAND_PRISM": _t("BRAND_PRISM", """{
  "physique": "Физические характеристики бренда",
  "personality": "Характер бренда",
  "culture": "Культура и ценности",
  "relationship": "Отношения с клиентом",
  "reflection": "Типичный пользователь (отражение)",
  "self_image": "Самоощущение пользователя",
  "brand_identity_gap": "Разрыв между текущим и желаемым восприятием",
  "recommendations": [...]
}"""),
    "RFM": _t("RFM", """{
  "segments": [
    {"name": "Чемпионы", "description": "...", "count": "...", "strategy": "..."},
    {"name": "Лояльные", "description": "...", "strategy": "..."},
    {"name": "Спящие", "description": "...", "strategy": "..."},
    {"name": "Уходящие", "description": "...", "strategy": "..."},
    {"name": "Новые", "description": "...", "strategy": "..."}
  ],
  "overall_strategy": "Стратегия работы с сегментами"
}"""),
    "COHORT": _t("COHORT", """{
  "cohorts": [
    {"period": "янв.2025", "retention_day_1": "...", "retention_day_7": "...", "retention_day_30": "..."},
    {"period": "фев.2025", ...}
  ],
  "insights": ["инсайт 1 по удержанию", ...],
  "recommendations": [...]
}"""),
    "PORTER_5": _t("PORTER_5", """{
  "rivalry": {"intensity": "высокая/средняя/низкая", "factors": [...], "recommendations": [...]},
  "new_entrants": {"threat": "...", "barriers": [...], "recommendations": [...]},
  "substitutes": {"threat": "...", "substitutes": [...], "recommendations": [...]},
  "suppliers": {"power": "...", "factors": [...], "recommendations": [...]},
  "buyers": {"power": "...", "factors": [...], "recommendations": [...]},
  "overall_attractiveness": "Привлекательность отрасли"
}"""),
    "ANSOFF": _t("ANSOFF", """{
  "market_penetration": {"current_strategy": "...", "opportunities": [...], "recommendations": [...]},
  "market_development": {"new_markets": [...], "recommendations": [...]},
  "product_development": {"new_products": [...], "recommendations": [...]},
  "diversification": {"options": [...], "risks": [...], "recommendations": [...]},
  "recommended_direction": "Рекомендуемый вектор роста"
}"""),
    "VRIO": _t("VRIO", """{
  "resources": [
    {"resource": "ресурс 1", "valuable": true/false, "rare": true/false, "costly_to_imitate": true/false, "organized": true/false, "competitive_implication": "..."},
    ...
  ],
  "sustained_advantage": ["устойчивое конкурентное преимущество 1", ...],
  "recommendations": [...]
}"""),
    "STP": _t("STP", """{
  "segmentation": [
    {"segment": "сегмент 1", "criteria": "...", "size": "...", "characteristics": [...]},
    ...
  ],
  "targeting": {"selected_segments": [...], "targeting_strategy": "концентрированный/дифференцированный", "rationale": "..."},
  "positioning": {"positioning_statement": "Заявление о позиционировании", "differentiators": [...], "brand_promise": "..."}
}"""),
    "BUSINESS_MODEL_CANVAS": _t("BUSINESS_MODEL_CANVAS", """{
  "customer_segments": ["сегмент 1", ...],
  "value_propositions": ["ценностное предложение 1", ...],
  "channels": ["канал 1", ...],
  "customer_relationships": ["тип отношений 1", ...],
  "revenue_streams": ["источник дохода 1", ...],
  "key_resources": ["ключевой ресурс 1", ...],
  "key_activities": ["ключевая активность 1", ...],
  "key_partnerships": ["ключевой партнёр 1", ...],
  "cost_structure": ["статья расходов 1", ...],
  "recommendations": ["рекомендация 1 по бизнес-модели", ...]
}"""),
    "NPS": _t("NPS", """{
  "current_nps": "текущий NPS или оценка",
  "promoters": {"share": "%", "characteristics": [...], "retention_strategy": "..."},
  "passives": {"share": "%", "characteristics": [...], "conversion_strategy": "..."},
  "detractors": {"share": "%", "characteristics": [...], "recovery_strategy": "..."},
  "drivers": {"key_factors": ["фактор 1", ...], "improvement_areas": [...]},
  "recommendations": [...]
}"""),
    "CHURN": _t("CHURN", """{
  "current_churn_rate": "текущий %",
  "churn_reasons": ["причина 1", ...],
  "churn_segments": [
    {"segment": "сегмент 1", "churn_rate": "...", "characteristics": [...], "strategy": "..."}
  ],
  "early_warning_signals": ["сигнал 1", ...],
  "prevention_strategies": ["стратегия удержания 1", ...],
  "win_back_strategy": ["стратегия возврата 1", ...]
}"""),
    "SOSTAC": _t("SOSTAC", """{
  "situation": {"current_state": "...", "key_findings": [...]},
  "objectives": {"smart_goals": [{"goal": "...", "kpi": "...", "deadline": "..."}]},
  "strategy": {"target_audience": "...", "positioning": "...", "channels": [...]},
  "tactics": {"actions": [{"tactic": "...", "timeline": "...", "owner": "..."}]},
  "action": {"implementation_plan": [{"step": "...", "resources": "...", "deadline": "..."}]},
  "control": {"kpis": [...], "review_frequency": "...", "success_criteria": [...]}
}"""),
    "VPC": _t("VPC", """{
  "customer_profile": {
    "customer_jobs": ["задача 1", ...],
    "pains": ["боль 1", ...],
    "gains": ["желаемый результат 1", ...]
  },
  "value_map": {
    "products_services": ["продукт 1", ...],
    "pain_relievers": ["решение боли 1", ...],
    "gain_creators": ["создание выгоды 1", ...]
  },
  "fit_analysis": "Анализ соответствия между профилем и картой ценности",
  "recommendations": [...]
}"""),
    "BALANCED_SCORECARD": _t("BALANCED_SCORECARD", """{
  "financial": {"objectives": [...], "measures": [...], "targets": [...], "initiatives": [...]},
  "customer": {"objectives": [...], "measures": [...], "targets": [...], "initiatives": [...]},
  "internal_process": {"objectives": [...], "measures": [...], "targets": [...], "initiatives": [...]},
  "learning_growth": {"objectives": [...], "measures": [...], "targets": [...], "initiatives": [...]},
  "strategy_map": "Описание стратегической карты"
}"""),
    "GROWTH_LOOPS": _t("GROWTH_LOOPS", """{
  "current_loops": [
    {"name": "петля 1", "trigger": "...", "action": "...", "reward": "...", "effectiveness": "..."},
    ...
  ],
  "new_loop_opportunities": [
    {"name": "...", "mechanism": "...", "expected_impact": "...", "effort": "..."}
  ],
  "recommendations": [...]
}"""),
    "MMM": _t("MMM", """{
  "channel_effectiveness": [
    {
      "channel": "канал 1",
      "spend": "бюджет, руб",
      "impressions": "показы",
      "clicks": "клики",
      "ctr": "%",
      "conversions": "конверсии",
      "revenue": "выручка, руб",
      "roas": "ROAS",
      "contribution": "% вклада в общие продажи",
      "marginal_efficiency": "предельная эффективность при доп. рубле",
      "saturation_point": "точка насыщения, руб",
      "trend": "динамика эффективности"
    }
  ],
  "budget_optimization": {
    "current_split": "текущее распределение бюджета по каналам с цифрами",
    "recommended_split": "рекомендуемое распределение с обоснованием",
    "expected_improvement": "ожидаемый прирост эффективности, %",
    "reallocation_rationale": "почему именно так перераспределить — анализ"
  },
  "saturation_points": [
    {"channel": "канал 1", "current_spend": "руб", "saturation_at": "руб", "gap": "руб до насыщения"}
  ],
  "recommendations": [
    {"action": "что сделать с бюджетом", "channel": "канал", "spend_change": "изменение бюджета, руб", "expected_roas_change": "изменение ROAS", "expected_revenue_impact": "влияние на выручку, руб", "timeline": "срок внедрения"}
  ]
}"""),
    "SELLER_ANALYTICS": _t("SELLER_ANALYTICS", """{
  "marketplace_performance": [
    {
      "platform": "Ozon/Wildberries/Yandex Market",
      "revenue": "выручка за период, руб",
      "orders": "количество заказов",
      "aov": "средний чек, руб",
      "commission": "комиссия площадки, %",
      "logistics_costs": "затраты на логистику, руб",
      "profitability": "чистая прибыльность, %",
      "dynamics": "динамика месяц к месяцу, %",
      "rating": "рейтинг магазина",
      "reviews": "количество отзывов"
    }
  ],
  "assortment_analysis": {
    "top_products": [
      {"name": "товар 1", "revenue": "руб", "margin": "%", "units_sold": "шт", "growth": "динамика %"}
    ],
    "low_performers": [
      {"name": "товар 1", "reason": "почему не продаётся", "stock": "остатки", "recommendation": "что делать"}
    ],
    "gaps": ["категория 1, которую не представлена", "потенциальный спрос"],
    "seasonality": "анализ сезонности категорий"
  },
  "pricing_analysis": {
    "current_pricing": "текущая ценовая политика, диапазон цен",
    "competitor_pricing": "цены конкурентов на аналоги",
    "price_elasticity": "оценка эластичности спроса",
    "margin_analysis": "маржа по ценовым сегментам",
    "recommendations": [
      {"action": "оптимизация цены", "expected_effect": "рост маржи/продаж на X%", "timeline": "срок", "risk": "риски"}
    ]
  },
  "advertising_effectiveness": {
    "campaigns": [
      {"name": "кампания 1", "channel": "канал", "budget": "руб", "spent": "факт руб", "impressions": "показы", "clicks": "клики", "ctr": "%", "conversions": "конверсии", "cr": "%", "acos": "%", "roas": "X", "revenue": "выручка руб", "profit": "прибыль руб"}
    ],
    "total_stats": {"budget": "руб", "revenue": "руб", "roas": "X", "acos": "%"},
    "best_campaigns": "анализ лучших кампаний и why",
    "worst_campaigns": "анализ провальных кампаний и why",
    "recommendations": [
      {"action": "перераспределение бюджета", "expected_effect": "рост ROAS на X%", "timeline": "срок"}
    ]
  },
  "logistics": {
    "fulfillment_type": "FBS/FBO/DBS",
    "current_costs": "текущие затраты на логистику, руб",
    "cost_per_order": "стоимость доставки одного заказа",
    "delivery_times": "сроки доставки по регионам",
    "returns_rate": "% возвратов",
    "recommendations": [
      {"action": "как оптимизировать логистику", "expected_savings": "экономия X руб/мес", "timeline": "срок"}
    ]
  },
  "financial_summary": {
    "total_revenue": "общая выручка",
    "total_costs": "общие затраты",
    "net_profit": "чистая прибыль",
    "margin": "общая маржинальность",
    "monthly_growth": "среднемесячный рост"
  },
  "recommendations": [
    {"action": "стратегическая рекомендация 1", "category": "ассортимент/цены/реклама/логистика", "priority": "приоритет", "expected_effect": "эффект с цифрами", "timeline": "срок", "implementation_steps": ["шаг 1", "шаг 2"]}
  ]
}"""),
    "KOL_ANALYSIS": _t("KOL_ANALYSIS", """{
  "current_kols": [
    {
      "name": "блогер 1",
      "platform": "Instagram/YouTube/TG",
      "audience_size": "размер аудитории",
      "engagement_rate": "средний ER, %",
      "cost_per_post": "стоимость интеграции, руб",
      "total_spent": "всего потрачено, руб",
      "estimated_orders": "примерное количество заказов",
      "estimated_revenue": "примерная выручка, руб",
      "estimated_roi": "ROI, %",
      "conversion_to_purchase": "% конверсии из просмотра в покупку",
      "content_format": "формат (обзор/сторис/пост/подкаст)",
      "quality_score": "оценка 1-10"
    }
  ],
  "kol_selection_criteria": [
    {"criterion": "критерий 1", "weight": "важность 1-10", "current_assessment": "оценка текущей базы"}
  ],
  "recommended_kols": [
    {
      "name": "блогер X",
      "platform": "рекомендуемая платформа",
      "rationale": "почему подходит: аудитория, вовлечение, ниша",
      "expected_reach": "ожидаемый охват",
      "estimated_cost": "ориентировочная стоимость интеграции",
      "expected_roi": "прогнозный ROI",
      "priority": "приоритет (1-10)",
      "notes": "дополнительные рекомендации"
    }
  ],
  "campaign_strategy": {
    "format": "рекомендуемый формат интеграций",
    "timeline": "график кампаний по неделям/месяцам",
    "budget_allocation": "распределение бюджета по блогерам с обоснованием",
    "content_guidelines": "рекомендации по контенту",
    "kpis": ["KPI 1", "KPI 2"],
    "reporting": "как и когда замерять результаты"
  },
  "performance_benchmarks": {
    "avg_er_by_tier": {"micro": "ER%", "mid": "ER%", "macro": "ER%", "mega": "ER%"},
    "avg_cpm": "средний CPM по платформам",
    "avg_conversion": "средняя конверсия"
  },
  "recommendations": [
    {"action": "конкретная рекомендация", "rationale": "обоснование с цифрами", "expected_effect": "ожидаемый результат", "timeline": "срок внедрения", "budget": "необходимый бюджет", "priority": "приоритет"}
  ]
}"""),
    "OKR": _t("OKR", """{
  "objectives": [
    {"objective": "Цель 1", "key_results": [{"kr": "Ключевой результат 1", "current": "...", "target": "..."}]},
    ...
  ],
  "alignment": "Как цели связаны со стратегией компании",
  "recommendations": [...]
}"""),
    "MARKETING_STRATEGY": _t("MARKETING_STRATEGY", """{
  "market_analysis": {"size": "...", "growth": "...", "trends": [...]},
  "target_audience": {"segments": [...], "personas": [...]},
  "positioning": {"unique_value": "...", "differentiators": [...]},
  "channels": [
    {"channel": "канал 1", "strategy": "...", "budget": "...", "expected_roi": "..."}
  ],
  "budget": {"total": "...", "by_channel": {...}, "by_campaign": {...}},
  "kpis": {"metrics": [...], "targets": {...}},
  "timeline": {"phases": [...], "milestones": [...]},
  "risks": [...]
}"""),
    "PERSONA": _t("PERSONA", """{
  "personas": [
    {
      "name": "Персонаж 1",
      "demographics": {"age": "...", "location": "...", "income": "...", "role": "..."},
      "goals": ["цель 1", ...],
      "pains": ["боль 1", ...],
      "behaviors": ["поведение 1", ...],
      "channels": ["канал 1", ...],
      "brands_used": ["бренд 1", ...],
      "quote": "Цитата от лица персонажа"
    }
  ],
  "recommendations": ["как работать с каждой персоной", ...]
}"""),
}


class MarketingModelsLibrary:
    """Библиотека маркетинговых фреймворков для Dot Analysis (~130 моделей)"""

    MODELS = {
        # ========== 1. СТРАТЕГИЧЕСКИЕ ==========
        "SWOT": {
            "name": "SWOT-анализ",
            "description": "Анализ сильных и слабых сторон, возможностей и угроз. Базовый стратегический инструмент",
            "category": "Стратегические",
            "use_cases": ["стратегическое планирование", "анализ конкурентов", "оценка рынка", "бизнес-план"],
            "metrics": ["качественная оценка"],
            "keywords": ["сильные стороны", "слабые стороны", "возможности", "угрозы", "конкурент", "позиция"],
            "template": TEMPLATES.get("SWOT", "")
        },
        "PESTLE": {
            "name": "PESTLE-анализ",
            "description": "Макроэкономический анализ: политические, экономические, социальные, технологические, правовые и экологические факторы",
            "category": "Стратегические",
            "use_cases": ["выход на рынок", "оценка рисков", "долгосрочное планирование", "инвестиции"],
            "metrics": ["качественная оценка"],
            "keywords": ["политика", "экономика", "социум", "технологии", "экология", "право", "макро", "внешняя среда"],
            "template": TEMPLATES.get("PESTLE", "")
        },
        "PORTER_5": {
            "name": "5 сил Портера",
            "description": "Анализ конкурентной среды: угроза новых игроков, заменителей, власть поставщиков и покупателей, rivalry",
            "category": "Стратегические",
            "use_cases": ["анализ отрасли", "конкурентная стратегия", "вход на рынок", "оценка привлекательности"],
            "metrics": ["качественная оценка"],
            "keywords": ["конкуренция", "отрасль", "рынок", "поставщики", "покупатели", "барьеры", "заменители"],
            "template": TEMPLATES.get("PORTER_5", "")
        },
        "BCG": {
            "name": "Матрица BCG",
            "description": "Портфельный анализ: звёзды, дойные коровы, вопросительные знаки, собаки. Распределение ресурсов",
            "category": "Стратегические",
            "use_cases": ["портфель продуктов", "распределение инвестиций", "стратегия развития"],
            "metrics": ["доля рынка", "рост рынка"],
            "keywords": ["портфель", "продукты", "звезды", "коровы", "собаки", "вопросительные", "доля рынка"],
            "template": TEMPLATES.get("BCG", "")
        },
        "ANSOFF": {
            "name": "Матрица Ансоффа",
            "description": "Стратегии роста: проникновение, развитие рынка, развитие продукта, диверсификация",
            "category": "Стратегические",
            "use_cases": ["стратегия роста", "новые рынки", "новые продукты", "масштабирование"],
            "metrics": ["рост выручки", "доля рынка"],
            "keywords": ["рост", "новый рынок", "новый продукт", "диверсификация", "проникновение", "масштабирование"],
            "template": TEMPLATES.get("ANSOFF", "")
        },
        "GE_MCKINSEY": {
            "name": "GE-McKinsey Matrix",
            "description": "Двумерная матрица: привлекательность рынка vs конкурентная сила бизнеса. 9 клеток стратегий",
            "category": "Стратегические",
            "use_cases": ["портфельный анализ", "приоритизация", "инвестиционные решения"],
            "metrics": ["привлекательность рынка", "конкурентоспособность"],
            "keywords": ["привлекательность", "конкурентоспособность", "портфель", "инвестиции", "приоритет"],
            "template": TEMPLATES.get("BCG", "")
        },
        "SPACE": {
            "name": "SPACE-анализ",
            "description": "Стратегическая оценка: финансовая сила, конкурентное преимущество, стабильность среды, сила отрасли",
            "category": "Стратегические",
            "use_cases": ["стратегическая позиция", "агрессивная/консервативная стратегия"],
            "metrics": ["финансовые показатели", "конкурентные показатели"],
            "keywords": ["стратегическая позиция", "агрессивная", "консервативная", "оборонительная", "конкурентная"],
            "template": TEMPLATES.get("SWOT", "")
        },
        "VRIO": {
            "name": "VRIO-анализ",
            "description": "Оценка ресурсов: ценность, редкость, сложность копирования, организованность. Поиск устойчивых преимуществ",
            "category": "Стратегические",
            "use_cases": ["конкурентное преимущество", "анализ ресурсов", "core competencies"],
            "metrics": ["качественная оценка"],
            "keywords": ["ресурс", "компетенция", "преимущество", "ценность", "редкость", "копирование"],
            "template": TEMPLATES.get("VRIO", "")
        },
        "TOWS": {
            "name": "TOWS-матрица",
            "description": "Расширенный SWOT: стратегии SO, WO, ST, WT. Связь внутренних и внешних факторов",
            "category": "Стратегические",
            "use_cases": ["стратегическое планирование", "генерация стратегий"],
            "metrics": ["качественная оценка"],
            "keywords": ["стратегия", "so", "wo", "st", "wt", "комбинация", "факторы"],
            "template": TEMPLATES.get("SWOT", "")
        },
        "M7S": {
            "name": "McKinsey 7S",
            "description": "7 элементов организации: strategy, structure, systems, skills, staff, style, shared values",
            "category": "Стратегические",
            "use_cases": ["организационный анализ", "управление изменениями", "M&A"],
            "metrics": ["качественная оценка"],
            "keywords": ["организация", "структура", "система", "навыки", "персонал", "стиль", "ценности"],
            "template": TEMPLATES.get("SWOT", "")
        },
        "VALUE_CHAIN": {
            "name": "Цепочка ценности Портера",
            "description": "Анализ цепочки создания ценности: основные и вспомогательные активности бизнеса",
            "category": "Стратегические",
            "use_cases": ["операционная эффективность", "конкурентное преимущество", "оптимизация затрат"],
            "metrics": ["затраты", "добавленная ценность"],
            "keywords": ["цепочка", "ценность", "активности", "операции", "логистика", "производство", "маркетинг"],
            "template": TEMPLATES.get("SWOT", "")
        },
        "BALANCED_SCORECARD": {
            "name": "Balanced Scorecard (ССП)",
            "description": "Сбалансированная система показателей: финансы, клиенты, процессы, развитие",
            "category": "Стратегические",
            "use_cases": ["стратегический контроль", "KPI", "управление эффективностью"],
            "metrics": ["финансовые", "клиентские", "процессные", "развитие"],
            "keywords": ["kpi", "показатели", "стратегия", "эффективность", "финансы", "процессы", "обучение"],
            "template": TEMPLATES.get("BALANCED_SCORECARD", "")
        },
        "SCENARIO": {
            "name": "Сценарный анализ",
            "description": "Прогнозирование нескольких сценариев развития: оптимистичный, пессимистичный, базовый",
            "category": "Стратегические",
            "use_cases": ["долгосрочное планирование", "управление рисками", "стратегия"],
            "metrics": ["вероятность", "влияние"],
            "keywords": ["сценарий", "прогноз", "риск", "неопределенность", "планирование", "будущее"],
            "template": TEMPLATES.get("SWOT", "")
        },

        # ========== 2. КЛИЕНТСКИЕ ==========
        "JTBD": {
            "name": "Jobs To Be Done (JTBD)",
            "description": "Анализ 'работ', которые клиент нанимает продукт выполнить. Фокус на задаче, а не на продукте",
            "category": "Клиентские",
            "use_cases": ["разработка продукта", "сегментация", "позиционирование", "инновации"],
            "metrics": ["product-market fit", "удовлетворенность"],
            "keywords": ["задача", "работа", "нанимать", "job", "потребность", "мотивация", "контекст"],
            "template": TEMPLATES.get("JTBD", "")
        },
        "CJM": {
            "name": "Customer Journey Map (CJM)",
            "description": "Карта пути клиента от осознания потребности до лояльности. Точки контакта, эмоции, боли",
            "category": "Клиентские",
            "use_cases": ["UX/UI", "оптимизация конверсии", "омниканальность", "сервис"],
            "metrics": ["конверсия", "удовлетворенность", "CSAT"],
            "keywords": ["путь", "клиент", "точки контакта", "touchpoint", "опыт", "customer journey", "cjm"],
            "template": TEMPLATES.get("CJM", "")
        },
        "AARRR": {
            "name": "AARRR (Пиратские метрики)",
            "description": "Воронка роста: Acquisition, Activation, Retention, Revenue, Referral. Модель для product-led growth",
            "category": "Клиентские",
            "use_cases": ["startup", "продукт", "воронка", "рост", "мобильное приложение", "SaaS"],
            "metrics": ["CAC", "LTV", "Churn", "Conversion", "K-factor"],
            "keywords": ["воронка", "рост", "удержание", "монетизация", "рефералы", "активация", "привлечение"],
            "template": TEMPLATES.get("AARRR", "")
        },
        "EMPATHY_MAP": {
            "name": "Карта эмпатии",
            "description": "Глубокое понимание клиента: что видит, слышит, чувствует, говорит, делает. Боли и выгоды",
            "category": "Клиентские",
            "use_cases": ["исследование аудитории", "персонажи", "продукт"],
            "metrics": ["качественная оценка"],
            "keywords": ["эмпатия", "клиент", "чувства", "мысли", "видит", "слышит", "говорит", "делает", "боль"],
            "template": TEMPLATES.get("VPC", "")
        },
        "VPC": {
            "name": "Value Proposition Canvas",
            "description": "Соответствие профиля клиента (задачи, боли, выгоды) и карты ценности (продукты, решатели болей, создатели выгод)",
            "category": "Клиентские",
            "use_cases": ["позиционирование", "продукт", "УТП", "ценностное предложение"],
            "metrics": ["product-market fit"],
            "keywords": ["ценность", "предложение", "утп", "боль", "выгода", "задача", "клиент", "продукт"],
            "template": TEMPLATES.get("VPC", "")
        },
        "PERSONA": {
            "name": "Персонажи (User Personas)",
            "description": "Создание архетипов пользователей: демография, цели, боли, поведение, каналы",
            "category": "Клиентские",
            "use_cases": ["таргетинг", "контент", "продукт", "сегментация"],
            "metrics": ["качественная оценка"],
            "keywords": ["персона", "архетип", "аудитория", "сегмент", "демография", "пользователь"],
            "template": TEMPLATES.get("PERSONA", "")
        },
        "NPS": {
            "name": "Net Promoter Score (NPS)",
            "description": "Измерение лояльности через готовность рекомендовать. Промоутеры, пассивы, детракторы",
            "category": "Клиентские",
            "use_cases": ["лояльность", "удовлетворенность", "бенчмаркинг", "опросы"],
            "metrics": ["NPS", "% промоутеров", "% детракторов"],
            "keywords": ["лояльность", "рекомендация", "nps", "промоутер", "детрактор", "удовлетворенность"],
            "template": TEMPLATES.get("NPS", "")
        },
        "CSAT": {
            "name": "CSAT (Customer Satisfaction)",
            "description": "Оценка удовлетворённости клиента по 5-балльной шкале после конкретного взаимодействия",
            "category": "Клиентские",
            "use_cases": ["сервис", "поддержка", "качество", "опросы"],
            "metrics": ["CSAT score"],
            "keywords": ["удовлетворенность", "оценка", "csat", "сервис", "поддержка"],
            "template": TEMPLATES.get("NPS", "")
        },
        "CES": {
            "name": "Customer Effort Score (CES)",
            "description": "Измерение лёгкости взаимодействия с компанией. Чем меньше усилий — тем выше лояльность",
            "category": "Клиентские",
            "use_cases": ["сервис", "UX", "поддержка", "онбординг"],
            "metrics": ["CES score"],
            "keywords": ["усилие", "легкость", "сервис", "взаимодействие", "ces"],
            "template": TEMPLATES.get("NPS", "")
        },
        "5WHYS": {
            "name": "5 Почему (5 Whys)",
            "description": "Метод поиска коренных причин проблемы через последовательные вопросы 'почему?'",
            "category": "Клиентские",
            "use_cases": ["проблемы клиентов", "отток", "низкая конверсия", "качество"],
            "metrics": ["качественная оценка"],
            "keywords": ["почему", "причина", "проблема", "корень", "отток", "конверсия"],
            "template": TEMPLATES.get("SWOT", "")
        },
        "MOT": {
            "name": "Moments of Truth (MoT)",
            "description": "Ключевые моменты истины: zero moment, first moment, second moment — точки формирования впечатления",
            "category": "Клиентские",
            "use_cases": ["бренд", "сервис", "UX", "удержание"],
            "metrics": ["удовлетворенность", "конверсия"],
            "keywords": ["момент истины", "впечатление", "первый опыт", "решение", "покупка"],
            "template": TEMPLATES.get("CJM", "")
        },

        # ========== 3. МАРКЕТИНГ-МИКС ==========
        "4P": {
            "name": "4P Marketing Mix",
            "description": "Классический маркетинг-микс: Product, Price, Place, Promotion. Анализ и синхронизация элементов",
            "category": "Маркетинг-микс",
            "use_cases": ["стратегия", "запуск продукта", "позиционирование", "розница"],
            "metrics": ["доля рынка", "ценовая эластичность", "охват"],
            "keywords": ["продукт", "цена", "дистрибуция", "продвижение", "маркетинг-микс", "4p", "7p"],
            "template": TEMPLATES.get("4P", "")
        },
        "7P": {
            "name": "7P Marketing Mix",
            "description": "Расширенный маркетинг-микс: 4P + People, Process, Physical Evidence. Для сферы услуг",
            "category": "Маркетинг-микс",
            "use_cases": ["услуги", "сервис", "HoReCa", "B2B"],
            "metrics": ["качество сервиса", "удовлетворенность"],
            "keywords": ["люди", "процесс", "окружение", "услуга", "сервис", "7p"],
            "template": TEMPLATES.get("4P", "")
        },
        "SOSTAC": {
            "name": "SOSTAC",
            "description": "Фреймворк стратегического планирования: Situation, Objectives, Strategy, Tactics, Action, Control",
            "category": "Маркетинг-микс",
            "use_cases": ["цифровой маркетинг", "стратегия", "план", "KPI"],
            "metrics": ["KPI", "ROI"],
            "keywords": ["sostac", "стратегия", "план", "цели", "тактика", "контроль", "digital"],
            "template": TEMPLATES.get("SOSTAC", "")
        },
        "STP": {
            "name": "STP (Segmentation, Targeting, Positioning)",
            "description": "Сегментирование, выбор целевых сегментов и позиционирование. Основа маркетинговой стратегии",
            "category": "Маркетинг-микс",
            "use_cases": ["сегментация", "позиционирование", "выход на рынок", "бренд"],
            "metrics": ["доля сегмента", "рост"],
            "keywords": ["сегмент", "таргет", "позиционирование", "stp", "аудитория", "целевая"],
            "template": TEMPLATES.get("STP", "")
        },
        "AIDA": {
            "name": "AIDA (Attention, Interest, Desire, Action)",
            "description": "Классическая модель воронки: Внимание → Интерес → Желание → Действие",
            "category": "Маркетинг-микс",
            "use_cases": ["реклама", "копирайтинг", "воронка", "лендинг"],
            "metrics": ["конверсия", "CTR", "CR"],
            "keywords": ["внимание", "интерес", "желание", "действие", "aida", "воронка"],
            "template": TEMPLATES.get("AARRR", "")
        },
        "RACE": {
            "name": "RACE Framework",
            "description": "Digital-стратегия: Reach, Act, Convert, Engage. Цикл привлечения и удержания",
            "category": "Маркетинг-микс",
            "use_cases": ["digital-маркетинг", "контент", "SEO", "SMM"],
            "metrics": ["reach", "engagement", "conversion"],
            "keywords": ["reach", "act", "convert", "engage", "race", "digital", "цифровой"],
            "template": TEMPLATES.get("SOSTAC", "")
        },
        "INBOUND": {
            "name": "Inbound Marketing",
            "description": "Привлечение через полезный контент: Attract → Convert → Close → Delight",
            "category": "Маркетинг-микс",
            "use_cases": ["B2B", "контент-маркетинг", "SEO", "блог"],
            "metrics": ["трафик", "лиды", "конверсия"],
            "keywords": ["inbound", "контент", "привлечение", "лид", "blog", "сео"],
            "template": TEMPLATES.get("AARRR", "")
        },
        "FLYWHEEL": {
            "name": "Flywheel (Маховик)",
            "description": "Модель роста через счастье клиентов: Attract → Engage → Delight. Замена воронки",
            "category": "Маркетинг-микс",
            "use_cases": ["рост", "клиентоцентричность", "удержание", "рефералы"],
            "metrics": ["NPS", "LTV", "CAC"],
            "keywords": ["маховик", "flywheel", "счастье", "удержание", "рекомендации", "рост"],
            "template": TEMPLATES.get("AARRR", "")
        },
        "PESO": {
            "name": "PESO Model",
            "description": "Медиа-стратегия: Paid, Earned, Shared, Owned media. Интеграция каналов коммуникации",
            "category": "Маркетинг-микс",
            "use_cases": ["PR", "медиа", "контент", "интегрированные коммуникации"],
            "metrics": ["reach", "engagement", "share of voice"],
            "keywords": ["peso", "медиа", "paid", "earned", "shared", "owned", "коммуникация"],
            "template": TEMPLATES.get("MMM", "")
        },
        "DAGMAR": {
            "name": "DAGMAR",
            "description": "Модель измерения эффективности рекламы: Awareness → Comprehension → Conviction → Action",
            "category": "Маркетинг-микс",
            "use_cases": ["реклама", "коммуникация", "KPI рекламы"],
            "metrics": ["осведомленность", "понимание", "убежденность", "действие"],
            "keywords": ["реклама", "коммуникация", "dagmar", "осведомленность", "убеждение"],
            "template": TEMPLATES.get("AIDA", "")
        },

        # ========== 4. БРЕНД ==========
        "BRAND_PRISM": {
            "name": "Призма бренда Капферера",
            "description": "6 граней идентичности бренда: физика, личность, культура, отношения, отражение, самоощущение",
            "category": "Бренд",
            "use_cases": ["бренд-стратегия", "позиционирование", "айдентика"],
            "metrics": ["качественная оценка"],
            "keywords": ["бренд", "идентичность", "призма", "капферер", "личность", "культура"],
            "template": TEMPLATES.get("BRAND_PRISM", "")
        },
        "CBBE": {
            "name": "CBBE Пирамида Келлера",
            "description": "Customer-Based Brand Equity: Salience → Performance/Imagery → Judgments/Feelings → Resonance",
            "category": "Бренд",
            "use_cases": ["капитал бренда", "стратегия", "измерение"],
            "metrics": ["осведомленность", "ассоциации", "лояльность"],
            "keywords": ["бренд", "капитал", "пирамида", "келлер", "резонанс", "лояльность"],
            "template": TEMPLATES.get("BRAND_PRISM", "")
        },
        "BRAND_ARCHETYPES": {
            "name": "Архетипы бренда (Jung/Mark-Pearson)",
            "description": "12 архетипов: Герой, Бунтарь, Мудрец, Заботливый, Творец, Шут, Искатель и др.",
            "category": "Бренд",
            "use_cases": ["позиционирование", "бренд-стратегия", "коммуникация"],
            "metrics": ["качественная оценка"],
            "keywords": ["архетип", "бренд", "персонаж", "миф", "юнг", "марк-пирсон"],
            "template": TEMPLATES.get("BRAND_PRISM", "")
        },
        "BRAND_PLATFORM": {
            "name": "Бренд-платформа",
            "description": "Целостная платформа бренда: миссия, видение, ценности, характер, позиционирование, УТП",
            "category": "Бренд",
            "use_cases": ["бренд", "стратегия", "бренд-бук"],
            "metrics": ["качественная оценка"],
            "keywords": ["бренд-платформа", "миссия", "видение", "ценности", "утп", "позиционирование"],
            "template": TEMPLATES.get("BRAND_PRISM", "")
        },
        "AAKER_EQUITY": {
            "name": "Модель капитала бренда Аакера",
            "description": "5 активов: осведомленность, лояльность, воспринимаемое качество, ассоциации, другие активы",
            "category": "Бренд",
            "use_cases": ["оценка бренда", "стратегия", "M&A"],
            "metrics": ["осведомленность", "лояльность", "качество"],
            "keywords": ["аакер", "капитал", "equity", "осведомленность", "лояльность", "ассоциации"],
            "template": TEMPLATES.get("BRAND_PRISM", "")
        },
        "BRAND_PERSONALITY": {
            "name": "Личность бренда (Aaker)",
            "description": "5 измерений: искренность, возбуждение, компетентность, изысканность, прочность",
            "category": "Бренд",
            "use_cases": ["бренд", "коммуникация", "тональность"],
            "metrics": ["качественная оценка"],
            "keywords": ["личность", "характер", "искренность", "возбуждение", "компетентность"],
            "template": TEMPLATES.get("BRAND_PRISM", "")
        },
        "BRAND_TOUCHPOINTS": {
            "name": "Колесо касаний бренда",
            "description": "Карта всех точек контакта с брендом: до покупки, во время, после. Оценка впечатлений",
            "category": "Бренд",
            "use_cases": ["бренд", "сервис", "UX", "омниканальность"],
            "metrics": ["удовлетворенность", "качество контакта"],
            "keywords": ["касание", "точка контакта", "бренд", "впечатление", "touchpoint"],
            "template": TEMPLATES.get("CJM", "")
        },
        "LOVE_BRAND": {
            "name": "Love Brand (Любовь к бренду)",
            "description": "3 компонента: загадка (Mystery), чувственность (Sensuality), близость (Intimacy)",
            "category": "Бренд",
            "use_cases": ["лояльность", "эмоциональный бренд", "премиум"],
            "metrics": ["лояльность", "NPS"],
            "keywords": ["любовь", "эмоция", "загадка", "чувственность", "близость", "привязанность"],
            "template": TEMPLATES.get("BRAND_PRISM", "")
        },

        # ========== 5. ПРОДУКТ / ИННОВАЦИИ ==========
        "KANO": {
            "name": "Модель Кано",
            "description": "Классификация характеристик: must-be, performance, attractive, indifferent, reverse",
            "category": "Продукт",
            "use_cases": ["приоритизация", "продукт", "фичи", "удовлетворенность"],
            "metrics": ["удовлетворенность", "важность"],
            "keywords": ["кано", "фича", "характеристика", "must-be", "performance", "attractive", "приоритет"],
            "template": TEMPLATES.get("KANO", "")
        },
        "LEAN_CANVAS": {
            "name": "Lean Canvas",
            "description": "Одностраничный бизнес-план: проблема, решение, УТП, сегменты, каналы, доходы, расходы, метрики",
            "category": "Продукт",
            "use_cases": ["стартап", "бизнес-модель", "MVP", "идея"],
            "metrics": ["качественная оценка"],
            "keywords": ["lean", "canvas", "стартап", "mvp", "бизнес-модель", "проблема", "решение"],
            "template": TEMPLATES.get("LEAN_CANVAS", "")
        },
        "BUSINESS_MODEL_CANVAS": {
            "name": "Business Model Canvas",
            "description": "9 блоков бизнес-модели: сегменты, ценность, каналы, отношения, доходы, ресурсы, активности, партнёры, расходы",
            "category": "Продукт",
            "use_cases": ["бизнес-модель", "стратегия", "инновации"],
            "metrics": ["качественная оценка"],
            "keywords": ["biz model", "canvas", "бизнес-модель", "ценность", "доходы", "расходы"],
            "template": TEMPLATES.get("BUSINESS_MODEL_CANVAS", "")
        },
        "BLUE_OCEAN": {
            "name": "Голубой океан (Blue Ocean)",
            "description": "Создание нового рынка через ERRC-сетку: Eliminate, Reduce, Raise, Create",
            "category": "Продукт",
            "use_cases": ["инновации", "дифференциация", "новый рынок"],
            "metrics": ["ценность", "инновационность"],
            "keywords": ["голубой океан", "errс", "инновация", "дифференциация", "создать", "исключить"],
            "template": TEMPLATES.get("BLUE_OCEAN", "")
        },
        "DESIGN_THINKING": {
            "name": "Design Thinking",
            "description": "5 этапов: Empathize → Define → Ideate → Prototype → Test. Human-centered подход",
            "category": "Продукт",
            "use_cases": ["инновации", "продукт", "UX", "решение проблем"],
            "metrics": ["качественная оценка"],
            "keywords": ["дизайн", "мышление", "эмпатия", "прототип", "тест", "идея", "human-centered"],
            "template": TEMPLATES.get("VPC", "")
        },
        "PLC": {
            "name": "Жизненный цикл продукта (PLC)",
            "description": "Стадии: внедрение, рост, зрелость, спад. Стратегии на каждом этапе",
            "category": "Продукт",
            "use_cases": ["продукт", "портфель", "маркетинг-стратегия"],
            "metrics": ["продажи", "прибыль"],
            "keywords": ["жизненный цикл", "продукт", "рост", "зрелость", "спад", "внедрение"],
            "template": TEMPLATES.get("BCG", "")
        },
        "DIFFUSION_INNOVATION": {
            "name": "Диффузия инноваций (Rogers)",
            "description": "5 категорий пользователей: новаторы, ранние последователи, раннее большинство, позднее большинство, отстающие",
            "category": "Продукт",
            "use_cases": ["внедрение", "продукт", "маркетинг", "инновации"],
            "metrics": ["скорость принятия", "проникновение"],
            "keywords": ["инновация", "диффузия", "принятие", "новаторы", "большинство", "rogers"],
            "template": TEMPLATES.get("PERSONA", "")
        },
        "CHASM": {
            "name": "Пересечение пропасти (Crossing the Chasm)",
            "description": "Стратегия перехода от ранних последователей к раннему большинству (разрыв внедрения)",
            "category": "Продукт",
            "use_cases": ["стартап", "продукт", "масштабирование", "GTM"],
            "metrics": ["проникновение", "рост"],
            "keywords": ["пропасть", "chasm", "ранние", "большинство", "moore", "внедрение", "разрыв"],
            "template": TEMPLATES.get("ANSOFF", "")
        },
        "RICE": {
            "name": "RICE Prioritization",
            "description": "Приоритизация фич: Reach, Impact, Confidence, Effort. Score для каждой гипотезы",
            "category": "Продукт",
            "use_cases": ["приоритет", "продукт", "фичи", "бэклог"],
            "metrics": ["RICE score"],
            "keywords": ["rice", "приоритет", "фича", "гипотеза", "оценка", "impact"],
            "template": TEMPLATES.get("SWOT", "")
        },
        "MOSCOW": {
            "name": "MoSCoW",
            "description": "Приоритизация: Must have, Should have, Could have, Won't have. Для продуктов и проектов",
            "category": "Продукт",
            "use_cases": ["приоритет", "продукт", "проект", "scope"],
            "metrics": ["качественная оценка"],
            "keywords": ["moscow", "must", "should", "could", "wont", "приоритет", "scope"],
            "template": TEMPLATES.get("SWOT", "")
        },
        "OPPORTUNITY_SOLUTION_TREE": {
            "name": "Opportunity Solution Tree",
            "description": "Дерево: Opportunity → Solution → Experiment. Связь возможностей с решениями и экспериментами",
            "category": "Продукт",
            "use_cases": ["продукт", "инновации", "гипотезы", "эксперименты"],
            "metrics": ["качественная оценка"],
            "keywords": ["opportunity", "solution", "дерево", "гипотеза", "эксперимент"],
            "template": TEMPLATES.get("LEAN_CANVAS", "")
        },

        # ========== 6. DIGITAL-АНАЛИТИКА ==========
        "FUNNEL": {
            "name": "Воронка продаж / Funnel Analytics",
            "description": "Анализ воронки: каждый этап от трафика до покупки. Конверсии, отсев, узкие места",
            "category": "Digital-аналитика",
            "use_cases": ["e-commerce", "SaaS", "воронка", "оптимизация конверсии"],
            "metrics": ["CAC", "CR", "LTV"],
            "keywords": ["воронка", "funnel", "конверсия", "отсев", "этап", "лид", "покупка"],
            "template": TEMPLATES.get("AARRR", "")
        },
        "COHORT": {
            "name": "Когортный анализ",
            "description": "Анализ поведения групп пользователей по времени первой покупки/регистрации. Retention, LTV",
            "category": "Digital-аналитика",
            "use_cases": ["SaaS", "e-commerce", "удержание", "LTV"],
            "metrics": ["retention", "LTV"],
            "keywords": ["когорта", "cohort", "удержание", "retention", "ltv", "время"],
            "template": TEMPLATES.get("COHORT", "")
        },
        "RFM": {
            "name": "RFM-анализ",
            "description": "Recency, Frequency, Monetary. Сегментация клиентов по ценности для CRM и маркетинга",
            "category": "Digital-аналитика",
            "use_cases": ["CRM", "email", "лояльность", "сегментация"],
            "metrics": ["recency", "frequency", "monetary"],
            "keywords": ["rfm", "сегментация", "ценность", "лояльность", "повторные", "crm"],
            "template": TEMPLATES.get("RFM", "")
        },
        "CHURN": {
            "name": "Анализ оттока (Churn Analysis)",
            "description": "Причины и паттерны оттока клиентов. Раннее предупреждение и стратегии удержания",
            "category": "Digital-аналитика",
            "use_cases": ["SaaS", "подписки", "удержание", "CAC"],
            "metrics": ["churn rate", "LTV", "CAC"],
            "keywords": ["отток", "churn", "удержание", "retention", "уход", "клиент"],
            "template": TEMPLATES.get("CHURN", "")
        },
        "UNIT_ECONOMICS": {
            "name": "Юнит-экономика",
            "description": "CAC, LTV, маржинальность, срок окупаемости. Понятно ли бизнес сходится на единицу",
            "category": "Digital-аналитика",
            "use_cases": ["стартап", "e-commerce", "SaaS", "реклама"],
            "metrics": ["CAC", "LTV", "LTV/CAC", "Margins"],
            "keywords": ["юнит", "экономика", "cac", "ltv", "окупаемость", "маржинальность"],
            "template": TEMPLATES.get("UNIT_ECONOMICS", "")
        },
        "MMM": {
            "name": "Marketing Mix Modeling (MMM)",
            "description": "Статистический анализ эффективности каналов и оптимизация медиа-микса",
            "category": "Digital-аналитика",
            "use_cases": ["медиа", "реклама", "бюджет", "ROAS"],
            "metrics": ["ROAS", "ROI", "доля канала"],
            "keywords": ["mmm", "медиа-микс", "канал", "эффективность", "реклама", "бюджет"],
            "template": TEMPLATES.get("MMM", "")
        },
        "ATTRIBUTION": {
            "name": "Атрибуция (Attribution Modeling)",
            "description": "Распределение ценности конверсии по каналам: first-click, last-click, linear, time-decay, data-driven",
            "category": "Digital-аналитика",
            "use_cases": ["реклама", "каналы", "CPA", "ROAS"],
            "metrics": ["ROAS", "CPA", "доля канала"],
            "keywords": ["атрибуция", "attribution", "канал", "конверсия", "click", "модель"],
            "template": TEMPLATES.get("MMM", "")
        },
        "CRO": {
            "name": "Conversion Rate Optimization (CRO)",
            "description": "Системная оптимизация конверсии: гипотезы → A/B тесты → внедрение → измерение",
            "category": "Digital-аналитика",
            "use_cases": ["e-commerce", "лендинг", "воронка", "A/B тест"],
            "metrics": ["CR", "AOV"],
            "keywords": ["cro", "конверсия", "ab тест", "гипотеза", "лендинг", "оптимизация"],
            "template": TEMPLATES.get("AARRR", "")
        },
        "HEATMAP": {
            "name": "Хитмап-анализ (Heatmap)",
            "description": "Визуальный анализ поведения на сайте: клики, скроллы, движения мыши. Выявление проблем UX",
            "category": "Digital-аналитика",
            "use_cases": ["UX", "сайт", "лендинг", "конверсия"],
            "metrics": ["CTR", "вовлеченность"],
            "keywords": ["хитмап", "тепловая карта", "клик", "скролл", "ux", "поведение"],
            "template": TEMPLATES.get("CJM", "")
        },
        "ROAS": {
            "name": "ROAS / ROI анализ",
            "description": "Return on Advertising Spend. Эффективность рекламных инвестиций по каналам и кампаниям",
            "category": "Digital-аналитика",
            "use_cases": ["реклама", "бюджет", "эффективность"],
            "metrics": ["ROAS", "ROI", "CPA"],
            "keywords": ["roas", "roi", "реклама", "доход", "расход", "эффективность", "окупаемость"],
            "template": TEMPLATES.get("MMM", "")
        },

        # ========== 7. ФИНАНСЫ ==========
        "BREAK_EVEN": {
            "name": "Точка безубыточности (Break-even)",
            "description": "Расчёт объёма продаж, при котором доходы = расходам. Анализ порога рентабельности",
            "category": "Финансы",
            "use_cases": ["стартап", "бизнес-план", "ценообразование"],
            "metrics": ["BE point", "запас прочности"],
            "keywords": ["безубыточность", "break-even", "точка", "порог", "рентабельность", "постоянные", "переменные"],
            "template": TEMPLATES.get("UNIT_ECONOMICS", "")
        },
        "NPV_IRR": {
            "name": "NPV/IRR анализ",
            "description": "Net Present Value и Internal Rate of Return. Оценка инвестиционных проектов",
            "category": "Финансы",
            "use_cases": ["инвестиции", "проект", "окупаемость"],
            "metrics": ["NPV", "IRR", "PI"],
            "keywords": ["npv", "irr", "инвестиции", "дисконт", "денежный поток", "окупаемость"],
            "template": TEMPLATES.get("UNIT_ECONOMICS", "")
        },
        "P_L": {
            "name": "P&L (Прибыли и убытки)",
            "description": "Анализ отчёта о прибылях и убытках: выручка, себестоимость, валовая/операционная/чистая прибыль",
            "category": "Финансы",
            "use_cases": ["финансы", "бюджет", "управленческая отчётность"],
            "metrics": ["выручка", "EBITDA", "чистая прибыль"],
            "keywords": ["pnl", "прибыль", "убыток", "выручка", "себестоимость", "ebitda"],
            "template": TEMPLATES.get("UNIT_ECONOMICS", "")
        },
        "CASH_FLOW": {
            "name": "Cash Flow анализ",
            "description": "Движение денежных средств: операционный, инвестиционный, финансовый потоки",
            "category": "Финансы",
            "use_cases": ["финансы", "ликвидность", "платёжеспособность"],
            "metrics": ["FCF", "OCF", "DCF"],
            "keywords": ["денежный поток", "cash flow", "fcf", "ocf", "ликвидность"],
            "template": TEMPLATES.get("UNIT_ECONOMICS", "")
        },
        "PRICING_ELASTICITY": {
            "name": "Ценовая эластичность",
            "description": "Анализ чувствительности спроса к цене. Оптимальная цена, ценовые сегменты",
            "category": "Финансы",
            "use_cases": ["ценообразование", "реклама", "скидки"],
            "metrics": ["эластичность", "оптимальная цена"],
            "keywords": ["эластичность", "цена", "спрос", "pricing", "скидка", "оптимальная"],
            "template": TEMPLATES.get("4P", "")
        },
        "REVENUE_MODEL": {
            "name": "Revenue Model (Модель дохода)",
            "description": "Анализ модели монетизации: подписка, транзакции, freemium, реклама, лицензии",
            "category": "Финансы",
            "use_cases": ["стартап", "монетизация", "бизнес-модель"],
            "metrics": ["ARR", "MRR", "ARPU"],
            "keywords": ["доход", "монетизация", "подписка", "freemium", "транзакция", "реклама"],
            "template": TEMPLATES.get("BUSINESS_MODEL_CANVAS", "")
        },
        "SENSITIVITY": {
            "name": "Анализ чувствительности",
            "description": "Оценка влияния ключевых факторов (цена, объём, затраты) на финансовый результат",
            "category": "Финансы",
            "use_cases": ["прогноз", "риски", "финансовая модель"],
            "metrics": ["чувствительность", "влияние"],
            "keywords": ["чувствительность", "фактор", "влияние", "риск", "сценарий"],
            "template": TEMPLATES.get("SWOT", "")
        },

        # ========== 8. SAAS-МЕТРИКИ ==========
        "SAAS_METRICS": {
            "name": "SaaS Dashboard (ARR/MRR)",
            "description": "Ключевые метрики SaaS: ARR, MRR, NRR, churn, LTV/CAC, payback period",
            "category": "SaaS-метрики",
            "use_cases": ["SaaS", "подписки", "B2B"],
            "metrics": ["ARR", "MRR", "NRR", "Churn"],
            "keywords": ["saas", "arr", "mrr", "подписка", "метрики", "dashboard"],
            "template": TEMPLATES.get("UNIT_ECONOMICS", "")
        },
        "DAU_MAU": {
            "name": "DAU/MAU Stickiness",
            "description": "Вовлечённость: DAU/MAU ratio, stickiness, daily active users, monthly active users",
            "category": "SaaS-метрики",
            "use_cases": ["продукт", "вовлечённость", "gaming", "соцсети"],
            "metrics": ["DAU", "MAU", "DAU/MAU"],
            "keywords": ["dau", "mau", "активные", "пользователи", "вовлеченность", "липкость"],
            "template": TEMPLATES.get("AARRR", "")
        },
        "NORTH_STAR": {
            "name": "North Star Metric",
            "description": "Главная метрика, отражающая ценность продукта. Определение и каскадирование на команды",
            "category": "SaaS-метрики",
            "use_cases": ["продукт", "рост", "стратегия", "OKR"],
            "metrics": ["NSM", "влияние"],
            "keywords": ["north star", "nsm", "главная метрика", "ценность", "рост"],
            "template": TEMPLATES.get("OKR", "")
        },
        "ACTIVATION_RATE": {
            "name": "Activation Rate",
            "description": "Доля пользователей, достигших ключевого действия 'Aha!' момента в продукте",
            "category": "SaaS-метрики",
            "use_cases": ["онбординг", "продукт", "воронка"],
            "metrics": ["activation rate", "time to activation"],
            "keywords": ["активация", "ahа", "онбординг", "первый опыт", "activation"],
            "template": TEMPLATES.get("AARRR", "")
        },
        "TTV": {
            "name": "Time To Value (TTV)",
            "description": "Время от регистрации до получения первой ценности. Критично для удержания",
            "category": "SaaS-метрики",
            "use_cases": ["онбординг", "продукт", "удержание"],
            "metrics": ["TTV"],
            "keywords": ["ttv", "time to value", "ценность", "онбординг", "скорость"],
            "template": TEMPLATES.get("AARRR", "")
        },
        "NRR": {
            "name": "Net Revenue Retention (NRR)",
            "description": "Удержание дохода с учётом expansion, churn и downgrade. Ключевой SaaS-метрик",
            "category": "SaaS-метрики",
            "use_cases": ["SaaS", "рост", "удержание дохода"],
            "metrics": ["NRR", "GRR"],
            "keywords": ["nrr", "grr", "удержание дохода", "expansion", "saas"],
            "template": TEMPLATES.get("UNIT_ECONOMICS", "")
        },

        # ========== 9. E-COMM / МАРКЕТПЛЕЙСЫ ==========
        "SELLER_ANALYTICS": {
            "name": "Аналитика селлера (WB/Ozon)",
            "description": "Полный анализ продаж на маркетплейсах: выручка, комиссии, логистика, реклама, ассортимент",
            "category": "E-commerce",
            "use_cases": ["Wildberries", "Ozon", "маркетплейс", "селлер"],
            "metrics": ["выручка", "заказы", "AOV", "ACOS", "ROAS"],
            "keywords": ["wildberries", "ozon", "маркетплейс", "селлер", "продажи", "комиссия", "логистика"],
            "template": TEMPLATES.get("SELLER_ANALYTICS", "")
        },
        "KOL_ANALYSIS": {
            "name": "Анализ блогеров / KOL",
            "description": "Оценка эффективности интеграций с блогерами: охват, ER, стоимость, ROI. Поиск оптимальных KOL",
            "category": "E-commerce",
            "use_cases": ["инфлюенсеры", "блогеры", "реклама", "KOL"],
            "metrics": ["ER", "CPM", "ROI", "охват"],
            "keywords": ["блогер", "kol", "инфлюенсер", "интеграция", "реклама", "er", "охват"],
            "template": TEMPLATES.get("KOL_ANALYSIS", "")
        },
        "MARKETPLACE_SEO": {
            "name": "SEO маркетплейсов",
            "description": "Оптимизация карточек товаров: ключевые слова, заголовки, фото, рейтинг. Внутренний поиск WB/Ozon",
            "category": "E-commerce",
            "use_cases": ["Wildberries", "Ozon", "карточка", "трафик"],
            "metrics": ["позиция", "трафик", "конверсия"],
            "keywords": ["seo", "карточка", "поиск", "ранжирование", "keywords", "ozon", "wildberries"],
            "template": TEMPLATES.get("AARRR", "")
        },
        "ASSORTMENT_MATRIX": {
            "name": "Ассортиментная матрица",
            "description": "Оптимизация ассортимента: ширина, глубина, ABC-XYZ анализ, рентабельность категорий",
            "category": "E-commerce",
            "use_cases": ["розница", "e-commerce", "ассортимент"],
            "metrics": ["ABC", "XYZ", "оборачиваемость"],
            "keywords": ["ассортимент", "матрица", "категория", "abc", "xyz", "оборачиваемость"],
            "template": TEMPLATES.get("BCG", "")
        },
        "CATEGORY_MANAGEMENT": {
            "name": "Категорийный менеджмент",
            "description": "Управление категориями: роль категории, целеполагание, стратегия, тактика, планограмма",
            "category": "E-commerce",
            "use_cases": ["розница", "e-commerce", "ассортимент"],
            "metrics": ["продажи", "прибыль на SKU"],
            "keywords": ["категория", "ассортимент", "полка", "планограмма", "роль"],
            "template": TEMPLATES.get("BCG", "")
        },
        "MARKETPLACE_PRICING": {
            "name": "Ценообразование на маркетплейсах",
            "description": "Динамическое ценообразование, мониторинг конкурентов, акции, промокоды. Price wars",
            "category": "E-commerce",
            "use_cases": ["Wildberries", "Ozon", "цены", "конкуренты"],
            "metrics": ["цена", "позиция по цене", "эластичность"],
            "keywords": ["цена", "маркетплейс", "конкуренты", "динамическое", "акция", "скидка"],
            "template": TEMPLATES.get("4P", "")
        },

        # ========== 10. SMM / МЕДИА ==========
        "SMM_ANALYTICS": {
            "name": "SMM-аналитика",
            "description": "Анализ соцсетей: охват, вовлеченность, рост подписчиков, лучшие посты, контент-стратегия",
            "category": "SMM / Медиа",
            "use_cases": ["VK", "Telegram", "Instagram", "SMM-стратегия"],
            "metrics": ["ER", "охват", "CPM", "CPC"],
            "keywords": ["smm", "соцсети", "вовлеченность", "подписчики", "контент", "пост", "er"],
            "template": TEMPLATES.get("AARRR", "")
        },
        "TARGETING_AUDIT": {
            "name": "Аудит таргетинга",
            "description": "Анализ эффективности таргетированной рекламы: аудитории, креативы, CTR, CPA, частота",
            "category": "SMM / Медиа",
            "use_cases": ["таргет", "реклама", "VK", "FB", "myTarget"],
            "metrics": ["CTR", "CPC", "CPA", "CR"],
            "keywords": ["таргет", "реклама", "аудитория", "ctr", "креатив", "сегмент"],
            "template": TEMPLATES.get("MMM", "")
        },
        "VIRAL_COEFFICIENT": {
            "name": "Вирусный коэффициент",
            "description": "K-factor = количество приглашений × конверсия. Анализ виральности и органического роста",
            "category": "SMM / Медиа",
            "use_cases": ["виральность", "шеринг", "рефералы", "рост"],
            "metrics": ["K-factor", "CAC", "виральность"],
            "keywords": ["вирус", "k-factor", "шеринг", "реферал", "приглашение", "виральность"],
            "template": TEMPLATES.get("AARRR", "")
        },
        "CONTENT_EFFICIENCY": {
            "name": "Эффективность контента",
            "description": "Анализ контент-стратегии: форматы, темы, вовлеченность, best practices, контент-план",
            "category": "SMM / Медиа",
            "use_cases": ["контент", "блог", "SMM", "медиа"],
            "metrics": ["вовлеченность", "охват", "шеринг"],
            "keywords": ["контент", "формат", "тема", "эффективность", "best practice", "контент-план"],
            "template": TEMPLATES.get("AARRR", "")
        },
        "COMMUNITY_HEALTH": {
            "name": "Community Health",
            "description": "Здоровье сообщества: активность, тональность, модерация, retention участников",
            "category": "SMM / Медиа",
            "use_cases": ["Telegram", "чат", "сообщество", "генг"],
            "metrics": ["DAU", "MAU", "активность", "тональность"],
            "keywords": ["сообщество", "community", "чат", "модерация", "активность", "тональность"],
            "template": TEMPLATES.get("AARRR", "")
        },
        "SOCIAL_LISTENING": {
            "name": "Social Listening",
            "description": "Мониторинг упоминаний бренда в соцсетях и медиа: тональность, тренды, инсайты",
            "category": "SMM / Медиа",
            "use_cases": ["мониторинг", "репутация", "упоминания", "кризис"],
            "metrics": ["share of voice", "тональность", "охват"],
            "keywords": ["слушание", "мониторинг", "упоминание", "тональность", "репутация"],
            "template": TEMPLATES.get("SWOT", "")
        },
        "TELEGRAM_ADS": {
            "name": "Telegram Ads / Аналитика",
            "description": "Анализ рекламы в Telegram: каналы, посевы, CPM, ER, конверсия в подписку",
            "category": "SMM / Медиа",
            "use_cases": ["Telegram", "посевы", "реклама", "каналы"],
            "metrics": ["CPM", "ER", "CPC", "конверсия"],
            "keywords": ["telegram", "канал", "посев", "реклама", "cpm", "er"],
            "template": TEMPLATES.get("KOL_ANALYSIS", "")
        },

        # ========== 11. ПОВЕДЕНЧЕСКИЕ ==========
        "HOOK_MODEL": {
            "name": "Hook Model (Nir Eyal)",
            "description": "Формирование привычки: Trigger → Action → Variable Reward → Investment. Цикл зависимости",
            "category": "Поведенческие",
            "use_cases": ["продукт", "геймификация", "вовлеченность", "привычка"],
            "metrics": ["DAU/MAU", "retention"],
            "keywords": ["крючок", "hook", "привычка", "триггер", "награда", "инвестиция"],
            "template": TEMPLATES.get("HOOK_MODEL", "")
        },
        "FOGG": {
            "name": "Fogg Behavior Model",
            "description": "B=MAP: Поведение = Мотивация × Способность × Триггер. Анализ почему пользователи делают/не делают",
            "category": "Поведенческие",
            "use_cases": ["продукт", "UX", "изменение поведения", "конверсия"],
            "metrics": ["конверсия"],
            "keywords": ["fogg", "поведение", "мотивация", "способность", "триггер", "b=map"],
            "template": TEMPLATES.get("FOGG", "")
        },
        "COGNITIVE_BIASES": {
            "name": "Когнитивные искажения",
            "description": "Анализ применения когнитивных искажений: якорение, дефицит, социальное доказательство, эффект владения",
            "category": "Поведенческие",
            "use_cases": ["маркетинг", "копирайтинг", "реклама", "переговоры"],
            "metrics": ["конверсия"],
            "keywords": ["когнитивный", "искажение", "bias", "якорение", "дефицит", "соцдоказательство"],
            "template": TEMPLATES.get("SWOT", "")
        },
        "PROSPECT_THEORY": {
            "name": "Теория перспектив (Kahneman)",
            "description": "Принятие решений в условиях риска: loss aversion, framing effect, endowment effect",
            "category": "Поведенческие",
            "use_cases": ["ценообразование", "маркетинг", "продукт"],
            "metrics": ["качественная оценка"],
            "keywords": ["перспектива", "канеман", "потеря", "избегание", "фрейминг", "риск"],
            "template": TEMPLATES.get("SWOT", "")
        },
        "SCARCITY_URGENCY": {
            "name": "Дефицит и срочность",
            "description": "Принципы: ограниченное количество, время, эксклюзивность. Анализ применения в маркетинге",
            "category": "Поведенческие",
            "use_cases": ["e-commerce", "реклама", "email", "лендинг"],
            "metrics": ["конверсия", "скорость"],
            "keywords": ["дефицит", "срочность", "ограничение", "эксклюзив", "таймер", "редкость"],
            "template": TEMPLATES.get("SWOT", "")
        },
        "NEURO": {
            "name": "Нейромаркетинг",
            "description": "Анализ нейромаркетинговых принципов: цвета, шрифты, расположение, триггеры, сенсорный маркетинг",
            "category": "Поведенческие",
            "use_cases": ["дизайн", "упаковка", "реклама", "POS"],
            "metrics": ["внимание", "запоминание"],
            "keywords": ["нейро", "маркетинг", "мозг", "цвет", "шрифт", "сенсорный", "триггер"],
            "template": TEMPLATES.get("SWOT", "")
        },
        "CHOICE_ARCHITECTURE": {
            "name": "Архитектура выбора (Thaler)",
            "description": "Дизайн среды принятия решений: default option, decoy, anchoring, framing, nudge",
            "category": "Поведенческие",
            "use_cases": ["продукт", "ценообразование", "UX", "подписка"],
            "metrics": ["конверсия"],
            "keywords": ["выбор", "архитектура", "nudge", "дефолт", "decoy", "якорь", "thalеr"],
            "template": TEMPLATES.get("SWOT", "")
        },
        "ANCHORING": {
            "name": "Эффект якоря (Anchoring)",
            "description": "Влияние первой цены/информации на последующие решения. Применение в ценообразовании",
            "category": "Поведенческие",
            "use_cases": ["ценообразование", "переговоры", "скидки"],
            "metrics": ["восприятие цены"],
            "keywords": ["якорь", "anchoring", "цена", "восприятие", "первое впечатление"],
            "template": TEMPLATES.get("SWOT", "")
        },
        "SOCIAL_PROOF": {
            "name": "Социальное доказательство",
            "description": "Использование влияния других людей: отзывы, рейтинги, кейсы, количество клиентов, FOMO",
            "category": "Поведенческие",
            "use_cases": ["e-commerce", "лендинг", "реклама"],
            "metrics": ["конверсия"],
            "keywords": ["социальное", "доказательство", "отзыв", "рейтинг", "fomo", "клиент"],
            "template": TEMPLATES.get("SWOT", "")
        },

        # ========== 12. КОНКУРЕНТЫ ==========
        "COMPETITIVE_BENCHMARK": {
            "name": "Конкурентный бенчмаркинг",
            "description": "Сравнение ключевых показателей с конкурентами: цена, качество, ассортимент, сервис, доля рынка",
            "category": "Конкуренты",
            "use_cases": ["анализ рынка", "стратегия", "позиционирование"],
            "metrics": ["benchmark score"],
            "keywords": ["бенчмарк", "конкурент", "сравнение", "показатель", "рейтинг"],
            "template": TEMPLATES.get("SWOT", "")
        },
        "PERCEPTUAL_MAP": {
            "name": "Перцепционная карта",
            "description": "Двумерная карта восприятия брендов/продуктов в глазах потребителей. Поиск свободных ниш",
            "category": "Конкуренты",
            "use_cases": ["позиционирование", "бренд", "ниша"],
            "metrics": ["качественная оценка"],
            "keywords": ["карта", "восприятие", "позиционирование", "ниша", "бренд", "конкурент"],
            "template": TEMPLATES.get("STP", "")
        },
        "WAR_ROOM": {
            "name": "War Room (Конкурентная разведка)",
            "description": "Глубокий анализ конкурентов: продукт, цены, маркетинг, команда, финансы, стратегия",
            "category": "Конкуренты",
            "use_cases": ["конкуренция", "стратегия", "M&A"],
            "metrics": ["качественная оценка"],
            "keywords": ["война", "разведка", "конкурент", "стратегия", "дарк стори"],
            "template": TEMPLATES.get("SWOT", "")
        },
        "FEATURE_MATRIX": {
            "name": "Feature Comparison Matrix",
            "description": "Матрица сравнения функций/характеристик с конкурентами. Выявление пробелов и преимуществ",
            "category": "Конкуренты",
            "use_cases": ["продукт", "конкуренты", "позиционирование"],
            "metrics": ["feature coverage"],
            "keywords": ["фича", "сравнение", "матрица", "конкурент", "функция", "характеристика"],
            "template": TEMPLATES.get("SWOT", "")
        },
        "STRATEGIC_GROUP": {
            "name": "Стратегические группы",
            "description": "Карта стратегических групп: группировка конкурентов по стратегиям. Барьеры мобильности",
            "category": "Конкуренты",
            "use_cases": ["анализ отрасли", "конкурентная стратегия"],
            "metrics": ["качественная оценка"],
            "keywords": ["группа", "стратегическая", "карта", "барьер", "конкурент"],
            "template": TEMPLATES.get("PORTER_5", "")
        },
        "SHADOWING": {
            "name": "Shadowing (Теневое наблюдение)",
            "description": "Наблюдение за действиями клиента в реальной среде. Понимание невысказанных потребностей",
            "category": "Конкуренты",
            "use_cases": ["исследование", "UX", "продукт"],
            "metrics": ["качественная оценка"],
            "keywords": ["наблюдение", "тень", "исследование", "поведение", "контекст"],
            "template": TEMPLATES.get("CJM", "")
        },

        # ========== 13. GROWTH HACKING ==========
        "GROWTH_LOOPS": {
            "name": "Growth Loops (Петли роста)",
            "description": "Замкнутые циклы роста: входное действие → output → усилитель → повторение. Вместо воронок",
            "category": "Growth Hacking",
            "use_cases": ["рост", "продукт", "маркетинг", "виральность"],
            "metrics": ["LTV/CAC", "K-factor", "loop speed"],
            "keywords": ["петля", "growth loop", "рост", "цикл", "виральность", "усилитель"],
            "template": TEMPLATES.get("GROWTH_LOOPS", "")
        },
        "VIRAL_CYCLE": {
            "name": "Вирусный цикл",
            "description": "Длительность вирусного цикла: от получения приглашения до отправки нового. Оптимизация скорости",
            "category": "Growth Hacking",
            "use_cases": ["виральность", "рост", "рефералы"],
            "metrics": ["K-factor", "cycle time"],
            "keywords": ["вирус", "цикл", "скорость", "приглашение", "k-factor"],
            "template": TEMPLATES.get("GROWTH_LOOPS", "")
        },
        "REFERRAL_PROGRAM": {
            "name": "Реферальная программа",
            "description": "Дизайн реферальной программы: стимулы, механика, двустороннее вознаграждение, виральность",
            "category": "Growth Hacking",
            "use_cases": ["рост", "CAC", "лояльность"],
            "metrics": ["K-factor", "CAC", "referral rate"],
            "keywords": ["реферал", "программа", "приглашение", "вознаграждение", "виральность"],
            "template": TEMPLATES.get("GROWTH_LOOPS", "")
        },
        "PLG": {
            "name": "Product-led Growth (PLG)",
            "description": "Рост через продукт: freemium, free trial, self-serve, virality внутри продукта",
            "category": "Growth Hacking",
            "use_cases": ["SaaS", "продукт", "рост", "воронка"],
            "metrics": ["activation", "LTV", "CAC"],
            "keywords": ["plg", "product-led", "freemium", "trial", "самообслуживание"],
            "template": TEMPLATES.get("AARRR", "")
        },
        "FREEMIUM": {
            "name": "Freemium Analysis",
            "description": "Анализ freemium-модели: конверсия в платных, издержки бесплатных пользователей, upsell",
            "category": "Growth Hacking",
            "use_cases": ["SaaS", "монетизация", "рост"],
            "metrics": ["conversion to paid", "freemium cost"],
            "keywords": ["freemium", "бесплатно", "платно", "конверсия", "upsell"],
            "template": TEMPLATES.get("UNIT_ECONOMICS", "")
        },
        "NETWORK_EFFECTS": {
            "name": "Сетевые эффекты",
            "description": "Анализ сетевых эффектов: direct, indirect, two-sided, local. Стратегия усиления Network Effects",
            "category": "Growth Hacking",
            "use_cases": ["платформа", "маркетплейс", "соцсеть", "рост"],
            "metrics": ["density", "liquidity"],
            "keywords": ["сетевой", "эффект", "network", "платформа", "маркетплейс", "плотность"],
            "template": TEMPLATES.get("GROWTH_LOOPS", "")
        },
        "GROWTH_EXPERIMENTS": {
            "name": "Growth Experiments",
            "description": "Система growth-экспериментов: идея → гипотеза → приоритет → тест → анализ → масштаб",
            "category": "Growth Hacking",
            "use_cases": ["рост", "продукт", "маркетинг", "CRO"],
            "metrics": ["ICE score", "PIE score"],
            "keywords": ["эксперимент", "рост", "гипотеза", "тест", "ice", "приоритет"],
            "template": TEMPLATES.get("AARRR", "")
        },

        # ========== 14. РОССИЙСКАЯ СПЕЦИФИКА ==========
        "YANDEX_METRICA": {
            "name": "Аналитика Яндекс Метрики",
            "description": "Веб-аналитика: источники, поведение, конверсии, цели, воронки, когорты. Аудит настроек",
            "category": "Российская специфика",
            "use_cases": ["сайт", "аналитика", "SEO", "контекст"],
            "metrics": ["визиты", "отказы", "глубина", "конверсия"],
            "keywords": ["яндекс", "метрика", "веб", "аналитика", "визит", "цель", "воронка"],
            "template": TEMPLATES.get("AARRR", "")
        },
        "YANDEX_DIRECT": {
            "name": "Анализ Яндекс Директ",
            "description": "Эффективность контекстной рекламы: кампании, ключевые слова, ставки, минус-слова, CPA, CTR",
            "category": "Российская специфика",
            "use_cases": ["контекст", "PPC", "реклама", "Яндекс"],
            "metrics": ["CTR", "CPC", "CPA", "CR"],
            "keywords": ["директ", "яндекс", "контекст", "реклама", "ключевые слова", "ppc"],
            "template": TEMPLATES.get("MMM", "")
        },
        "VK_ADS": {
            "name": "Анализ VK Реклама",
            "description": "Анализ таргетированной рекламы VK: аудитории, креативы, бюджет, CTR, CPA, ретаргетинг",
            "category": "Российская специфика",
            "use_cases": ["VK", "таргет", "реклама", "SMM"],
            "metrics": ["CTR", "CPC", "CPA", "CR"],
            "keywords": ["vk", "вк", "реклама", "таргет", "аудитория", "креатив"],
            "template": TEMPLATES.get("TARGETING_AUDIT", "")
        },
        "WB_SELLER": {
            "name": "Wildberries Seller Analytics",
            "description": "Полный анализ продаж на Wildberries: рейтинг, отзывы, позиции, реклама, акции, выкупы",
            "category": "Российская специфика",
            "use_cases": ["Wildberries", "селлер", "e-commerce", "маркетплейс"],
            "metrics": ["выручка", "заказы", "% выкупа", "рейтинг"],
            "keywords": ["wildberries", "wb", "селлер", "продажи", "выкуп", "рейтинг"],
            "template": TEMPLATES.get("SELLER_ANALYTICS", "")
        },
        "OZON_SELLER": {
            "name": "Ozon Seller Analytics",
            "description": "Анализ продаж на Ozon: трафик, конверсия, реклама, рейтинг, отзывы, цены, акции",
            "category": "Российская специфика",
            "use_cases": ["Ozon", "селлер", "e-commerce", "маркетплейс"],
            "metrics": ["выручка", "заказы", "CR", "рейтинг"],
            "keywords": ["ozon", "селлер", "продажи", "трафик", "конверсия"],
            "template": TEMPLATES.get("SELLER_ANALYTICS", "")
        },
        "DZEN": {
            "name": "Яндекс Дзен аналитика",
            "description": "Анализ канала в Дзен: дочитывания, время, подписки, доход, лучшие публикации, темы",
            "category": "Российская специфика",
            "use_cases": ["Дзен", "контент", "монетизация", "медиа"],
            "metrics": ["дочитывания", "время", "CPM", "подписчики"],
            "keywords": ["дзен", "яндекс", "контент", "дочитывания", "канал", "монетизация"],
            "template": TEMPLATES.get("CONTENT_EFFICIENCY", "")
        },
        "AVITO": {
            "name": "Avito аналитика",
            "description": "Анализ продаж на Avito: объявления, просмотры, отклики, продвижение, тарифы, категории",
            "category": "Российская специфика",
            "use_cases": ["Avito", "C2C", "e-commerce", "объявления"],
            "metrics": ["просмотры", "отклики", "конверсия"],
            "keywords": ["avito", "авито", "объявление", "просмотр", "продажа"],
            "template": TEMPLATES.get("SELLER_ANALYTICS", "")
        },
        "MARKETPLACE_STRATEGY": {
            "name": "Стратегия продаж на маркетплейсах",
            "description": "Комплексная стратегия: выбор площадок, ассортимент, цены, реклама, логистика, юнит-экономика",
            "category": "Российская специфика",
            "use_cases": ["старт на WB/Ozon", "масштабирование", "стратегия"],
            "metrics": ["выручка", "прибыль", "ROAS"],
            "keywords": ["маркетплейс", "стратегия", "wb", "ozon", "выход", "масштабирование"],
            "template": TEMPLATES.get("SELLER_ANALYTICS", "")
        },
    }

    @classmethod
    def get_all_models(cls) -> List[Dict[str, Any]]:
        """Get all available marketing models"""
        return [
            {"key": key, **model}
            for key, model in cls.MODELS.items()
        ]

    @classmethod
    def get_model_by_key(cls, key: str) -> Dict[str, Any]:
        """Get a specific model by key"""
        return cls.MODELS.get(key, {})

    @classmethod
    def find_relevant_models(cls, context: str) -> List[Dict[str, Any]]:
        """Find relevant models based on context keywords"""
        context_lower = context.lower()
        relevant_models = []

        for key, model in cls.MODELS.items():
            score = 0
            keywords = model.get("keywords", [])
            if not keywords:
                continue
            for keyword in keywords:
                if keyword.lower() in context_lower:
                    score += 1
            if score > 0:
                relevant_models.append({
                    "key": key,
                    "model": model,
                    "relevance_score": score / len(keywords)
                })

        relevant_models.sort(key=lambda x: x["relevance_score"], reverse=True)
        return relevant_models

    @classmethod
    def get_models_for_llm_prompt(cls, models: List[Dict]) -> str:
        """Форматирует список моделей для промпта LLM с указанием ключа"""
        lines = []
        for m in models:
            model = m["model"]
            score = m.get("relevance_score", 0)
            lines.append(f"- [{m['key']}] {model['name']} ({score:.0%}): {model['description'][:200]}")
        return "\n".join(lines)

    @classmethod
    def get_model_templates(cls, keys: List[str]) -> Dict[str, str]:
        """Возвращает шаблоны вывода для указанных моделей"""
        return {k: cls.MODELS.get(k, {}).get("template", "{}") for k in keys}
