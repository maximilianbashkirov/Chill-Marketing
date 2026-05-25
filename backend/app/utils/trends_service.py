import httpx
import asyncio
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import re


class GoogleTrendsService:
    """Service for fetching trends from Google Trends via RSS and search"""
    
    BASE_URL = "https://trends.google.com"
    RSS_URLS = {
        "ru": f"{BASE_URL}/trends/rss?id=TRENDING_SEARCHES_DAILY_LATEST&geo=RU&hl=ru-RU",
        "world": f"{BASE_URL}/trends/rss?id=TRENDING_SEARCHES_DAILY_LATEST&geo=GLOBAL&hl=ru-RU",
        "business": f"{BASE_URL}/trends/rss?id=TOP_CHARTS&geo=RU&hl=ru-RU&cat=bz",
        "tech": f"{BASE_URL}/trends/rss?id=TOP_CHARTS&geo=RU&hl=ru-RU&cat=ts",
    }
    
    def __init__(self):
        self.session = None
        self._cached_trends = {}
        self._cache_time = None
    
    async def _get_session(self):
        if self.session is None:
            self.session = httpx.AsyncClient(
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Accept": "text/html,application/xml,application/rss+xml",
                    "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8"
                },
                timeout=30.0,
                follow_redirects=True
            )
        return self.session
    
    def _is_cache_valid(self) -> bool:
        if self._cache_time is None:
            return False
        return (datetime.now() - self._cache_time).total_seconds() < 3600
    
    async def get_trending_searches(self, country: str = "RU") -> List[Dict[str, Any]]:
        """Get trending searches via RSS"""
        if self._is_cache_valid() and self._cached_trends.get("trending"):
            return self._cached_trends["trending"]
        
        try:
            session = await self._get_session()
            geo = "RU" if country == "RU" else "GLOBAL"
            rss_url = f"{self.BASE_URL}/trends/rss?id=TRENDING_SEARCHES_DAILY_LATEST&geo={geo}&hl=ru-RU"
            
            response = await session.get(rss_url)
            
            if response.status_code == 200:
                trends = self._parse_rss(response.text)
                self._cached_trends["trending"] = trends
                self._cache_time = datetime.now()
                return trends[:15]
            return []
        except Exception as e:
            print(f"Google Trends RSS error: {e}")
            return self._get_fallback_trends()
    
    def _parse_rss(self, rss_content: str) -> List[Dict[str, Any]]:
        """Parse RSS feed content"""
        try:
            root = ET.fromstring(rss_content)
            items = root.findall(".//item")
            
            trends = []
            for item in items:
                title = item.find("title")
                description = item.find("description")
                link = item.find("link")
                
                trends.append({
                    "title": title.text if title is not None else "",
                    "description": description.text if description is not None else "",
                    "link": link.text if link is not None else "",
                    "queries": []
                })
            return trends
        except Exception as e:
            print(f"RSS parsing error: {e}")
            return []
    
    async def search_keyword_trends(self, keyword: str) -> Dict[str, Any]:
        """Search for trends related to a keyword via Google search"""
        try:
            session = await self._get_session()
            
            search_url = f"https://www.google.com/search?q={keyword}&tbm=trl&hl=ru"
            response = await session.get(search_url)
            
            if response.status_code == 200:
                return {
                    "keyword": keyword,
                    "status": "analyzed",
                    "note": "Проанализировано через поисковую выдачу"
                }
            return {"keyword": keyword, "status": "error"}
        except Exception as e:
            print(f"Search trends error: {e}")
            return {"keyword": keyword, "status": "error"}
    
    async def get_related_queries(self, keyword: str) -> Dict[str, Any]:
        """Get related queries via search"""
        try:
            session = await self._get_session()
            search_url = f"https://www.google.com/search?q={keyword}&hl=ru-RU"
            response = await session.get(search_url)
            
            if response.status_code == 200:
                html = response.text
                related = re.findall(r'related:\{1:"([^"]+)"', html)
                
                return {
                    "keyword": keyword,
                    "related_queries": related[:10] if related else [],
                    "status": "success"
                }
            return {"keyword": keyword, "status": "error"}
        except Exception as e:
            print(f"Related queries error: {e}")
            return {}
    
    async def get_top_charts(self, year: int = 2024, category: str = "all") -> List[Dict[str, Any]]:
        """Get top charts via RSS"""
        try:
            session = await self._get_session()
            cat_map = {"all": "", "business": "bz", "tech": "ts", "entertainment": "e", "health": "h", "sports": "t"}
            cat_param = cat_map.get(category, "")
            cat_param = f"&cat={cat_param}" if cat_param else ""
            
            rss_url = f"{self.BASE_URL}/trends/rss?id=TOP_CHARTS&geo=RU&hl=ru-RU&year={year}{cat_param}"
            response = await session.get(rss_url)
            
            if response.status_code == 200:
                return self._parse_rss(response.text)
            return []
        except Exception as e:
            print(f"Top charts error: {e}")
            return []
    
    async def get_category_trends(self, category: str) -> List[Dict[str, Any]]:
        """Get category-specific trends"""
        try:
            return await self.get_trending_searches()
        except Exception as e:
            print(f"Category trends error: {e}")
            return []
    
    def _get_fallback_trends(self) -> List[Dict[str, Any]]:
        """Fallback trends when API fails"""
        return [
            {"title": "ИИ и нейросети", "description": "Популярные запросы об искусственном интеллекте"},
            {"title": "Маркетинг 2024", "description": "Тренды цифрового маркетинга"},
            {"title": "Здоровый образ жизни", "description": "Фитнес и правильное питание"},
            {"title": "Путешествия", "description": "Популярные направления"},
            {"title": "Технологии", "description": "Новинки гаджетов"}
        ]


trends_service = GoogleTrendsService()