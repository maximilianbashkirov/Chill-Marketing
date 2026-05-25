from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.utils.rss_fetcher import rss_fetcher
from app.utils.content_knowledge import (
    content_knowledge_base,
    get_category_for_keyword,
    get_trending_topics_for_category,
    get_format_suggestions,
    get_best_hashtags,
    get_posting_times,
    get_content_ideas_for_category
)


router = APIRouter(prefix="/trends", tags=["Trends & Knowledge Base"])


class TrendItem(BaseModel):
    title: str
    description: Optional[str] = None
    url: Optional[str] = None
    category: str
    source: str


class CategoryAdd(BaseModel):
    name: str
    high_engagement_topics: List[str]
    best_hashtags: List[str]


class TrendResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


@router.get("/fetch", response_model=TrendResponse)
async def fetch_all_trends():
    """Собрать свежие тренды из всех RSS источников"""
    try:
        results = await rss_fetcher.fetch_all_sources()
        
        trends_by_cat = rss_fetcher.get_trends_by_category()
        keywords = rss_fetcher.get_trending_keywords()
        
        return TrendResponse(
            success=True,
            message=f"Собрано {sum(len(v) for v in results.values())} трендов",
            data={
                "trends_by_category": trends_by_cat,
                "top_keywords": keywords[:30],
                "last_update": datetime.now().isoformat(),
                "sources_count": len(results)
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sources", response_model=TrendResponse)
async def get_sources():
    """Получить список доступных источников"""
    sources = [
        {"id": k, "name": v["name"], "category": v["category"]}
        for k, v in rss_fetcher.RSS_SOURCES.items()
    ]
    
    return TrendResponse(
        success=True,
        message=f"Досточено {len(sources)} источников",
        data={"sources": sources}
    )


@router.get("/keywords", response_model=TrendResponse)
async def get_trending_keywords():
    """Получить трендовые ключевые слова"""
    keywords = rss_fetcher.get_trending_keywords()
    
    return TrendResponse(
        success=True,
        message=f"Найдено {len(keywords)} ключевых слов",
        data={"keywords": keywords}
    )


@router.get("/by-category/{category}", response_model=TrendResponse)
async def get_trends_by_category(category: str):
    """Получить тренды по категории"""
    trends = rss_fetcher.get_trends_by_category().get(category, [])
    
    return TrendResponse(
        success=True,
        message=f"Найдено {len(trends)} трендов",
        data={"trends": trends, "category": category}
    )


@router.get("/knowledge-base", response_model=TrendResponse)
async def get_knowledge_base():
    """Получить текущую базу знаний"""
    return TrendResponse(
        success=True,
        message="База знаний получена",
        data={
            "categories": list(content_knowledge_base.keys()),
            "knowledge_base": content_knowledge_base
        }
    )


@router.post("/knowledge-base/category", response_model=TrendResponse)
async def add_category(category: CategoryAdd):
    """Добавить новую категорию в базу знаний"""
    if category.name in content_knowledge_base:
        raise HTTPException(status_code=400, detail="Категория уже существует")
    
    content_knowledge_base[category.name] = {
        "high_engagement_topics": category.high_engagement_topics,
        "trending_formats": [
            {"name": "Пост", "description": "Текстовый контент", "platforms": ["Instagram", "Telegram"]},
            {"name": "Карусель", "description": "Мультислайд", "platforms": ["Instagram"]}
        ],
        "best_hashtags": category.best_hashtags,
        "posting_times": {
            "weekday": ["12:00-14:00", "18:00-21:00"],
            "weekend": ["10:00-12:00"]
        }
    }
    
    return TrendResponse(
        success=True,
        message=f"Категория '{category.name}' добавлена",
        data={"category": category.name}
    )


@router.get("/insights", response_model=TrendResponse)
async def get_marketing_insights():
    """Получить маркетинговые инсайты на основе трендов"""
    keywords = rss_fetcher.get_trending_keywords()
    trends_by_cat = rss_fetcher.get_trends_by_category()
    
    insights = {
        "trending_topics": [],
        "content_suggestions": [],
        "hashtag_recommendations": []
    }
    
    if "marketing" in trends_by_cat:
        insights["trending_topics"] = trends_by_cat["marketing"][:5]
    
    if "tech" in trends_by_cat:
        insights["content_suggestions"] = [
            f"Свяжите вашу тему с трендом: {trends_by_cat['tech'][0]}",
            f"Создайте гайд по: {trends_by_cat['tech'][1]}"
        ]
    
    keywords_with_marketing = [k for k in keywords if any(
        word in k.lower() for word in ["маркетинг", "бизнес", "продажи", "успех"]
    )]
    insights["hashtag_recommendations"] = keywords_with_marketing[:10]
    
    return TrendResponse(
        success=True,
        message="Инсайты сгенерированы",
        data=insights
    )


@router.post("/refresh", response_model=TrendResponse)
async def refresh_knowledge_base():
    """Обновить базу знаний свежими трендами"""
    await rss_fetcher.fetch_all_sources()
    
    return TrendResponse(
        success=True,
        message="База обновлена",
        data={
            "last_update": datetime.now().isoformat(),
            "cached_trends_count": sum(len(v) for v in rss_fetcher._trends_cache.values())
        }
    )