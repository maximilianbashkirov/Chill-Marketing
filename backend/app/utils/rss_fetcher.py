import httpx
import asyncio
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import xml.etree.ElementTree as ET
import re
from app.config import settings


class RSSFetcher:
    """Сервис для сбора данных из RSS фидов"""
    
    def __init__(self):
        self.proxy = settings.GIGACHAT_PROXY or os.environ.get('HTTP_PROXY')
    
    RSS_SOURCES = {
        "youtube_trending": {
            "url": "https://www.youtube.com/feeds/videos.xml?channel_id=UC-lHJZR3Gqxm24_Vd_AJ5Yw",
            "name": "YouTube Trending",
            "category": "entertainment"
        },
        "reddit_popular": {
            "url": "https://www.reddit.com/r/popular/hot/.json",
            "name": "Reddit Popular",
            "category": "general",
            "is_json": True
        },
        "reddit_technology": {
            "url": "https://www.reddit.com/r/technology/.json",
            "name": "Reddit Technology",
            "category": "tech"
        },
        "reddit_marketing": {
            "url": "https://www.reddit.com/r/marketing/.json",
            "name": "Reddit Marketing",
            "category": "marketing"
        },
        "hacker_news": {
            "url": "https://news.ycombinator.com/rss",
            "name": "Hacker News",
            "category": "tech"
        },
        "medium_tech": {
            "url": "https://medium.com/feed/topic/technology",
            "name": "Medium Technology",
            "category": "tech"
        },
        "medium_business": {
            "url": "https://medium.com/feed/topic/business",
            "name": "Medium Business",
            "category": "business"
        }
    }
    
    def __init__(self):
        self.session = None
        self._last_update = None
        self._trends_cache = {}
    
    async def _get_session(self):
        if self.session is None:
            kwargs = {
                "headers": {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Accept": "application/rss+xml, application/xml, text/xml, application/json"
                },
                "timeout": 30.0,
                "follow_redirects": True
            }
            if self.proxy:
                kwargs["proxies"] = {"http://": self.proxy, "https://": self.proxy}
                print(f"Using proxy for RSS: {self.proxy}")
            self.session = httpx.AsyncClient(**kwargs)
        return self.session
    
    async def fetch_all_sources(self) -> Dict[str, List[Dict[str, Any]]]:
        """Собрать данные со всех источников"""
        results = {}
        
        for source_id, source_config in self.RSS_SOURCES.items():
            try:
                data = await self._fetch_source(source_id, source_config)
                results[source_id] = data
                print(f"Fetched {len(data)} items from {source_config['name']}")
            except Exception as e:
                print(f"Error fetching {source_id}: {e}")
                results[source_id] = []
        
        self._last_update = datetime.now()
        self._trends_cache = results
        return results
    
    async def _fetch_source(self, source_id: str, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Собрать данные с одного источника"""
        session = await self._get_session()
        
        if config.get("is_json"):
            return await self._fetch_json(source_id, config["url"], config["category"])
        else:
            return await self._fetch_rss(config["url"], config["category"])
    
    async def _fetch_rss(self, url: str, category: str) -> List[Dict[str, Any]]:
        """Парсить RSS фид"""
        try:
            session = await self._get_session()
            response = await session.get(url)
            
            if response.status_code != 200:
                return []
            
            root = ET.fromstring(response.text)
            items = root.findall(".//item") or root.findall(".//entry")
            
            results = []
            for item in items[:15]:
                title = item.find("title")
                link = item.find("link")
                desc = item.find("description") or item.find("summary") or item.find("content")
                
                results.append({
                    "title": title.text if title is not None else "",
                    "url": link.text if link is not None else "",
                    "description": self._clean_html(desc.text if desc is not None else ""),
                    "category": category,
                    "source": "rss",
                    "fetched_at": datetime.now().isoformat()
                })
            
            return results
        except Exception as e:
            print(f"RSS fetch error for {url}: {e}")
            return []
    
    async def _fetch_json(self, url: str, category: str) -> List[Dict[str, Any]]:
        """Парсить JSON API (Reddit)"""
        try:
            session = await self._get_session()
            response = await session.get(url, headers={"Accept": "application/json"})
            
            if response.status_code != 200:
                return []
            
            data = response.json()
            posts = data.get("data", {}).get("children", [])[:15]
            
            results = []
            for post in posts:
                post_data = post.get("data", {})
                results.append({
                    "title": post_data.get("title", ""),
                    "url": f"https://reddit.com{post_data.get('permalink', '')}",
                    "description": post_data.get("selftext", "")[:200],
                    "score": post_data.get("score", 0),
                    "category": category,
                    "source": "reddit",
                    "fetched_at": datetime.now().isoformat()
                })
            
            return results
        except Exception as e:
            print(f"JSON fetch error for {url}: {e}")
            return []
    
    def _clean_html(self, text: str) -> str:
        """Очистить HTML теги"""
        if not text:
            return ""
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()[:200]
    
    def get_trending_keywords(self) -> List[str]:
        """Получить трендовые ключевые слова из собранных данных"""
        keywords = set()
        
        for source_data in self._trends_cache.values():
            for item in source_data:
                title = item.get("title", "")
                words = re.findall(r'\b[А-Яа-яA-Z]{4,}\b', title)
                keywords.update(words[:3])
        
        return sorted(list(keywords))[:50]
    
    def get_trends_by_category(self) -> Dict[str, List[str]]:
        """Сгруппировать тренды по категориям"""
        trends_by_cat = {}
        
        for source_id, source_data in self._trends_cache.items():
            for item in source_data:
                cat = item.get("category", "general")
                title = item.get("title", "")
                
                if cat not in trends_by_cat:
                    trends_by_cat[cat] = []
                if title and len(trends_by_cat[cat]) < 10:
                    trends_by_cat[cat].append(title)
        
        return trends_by_cat
    
    def get_all_trends(self) -> List[Dict[str, Any]]:
        """Получить все тренды"""
        all_trends = []
        
        for source_data in self._trends_cache.values():
            all_trends.extend(source_data)
        
        return all_trends


rss_fetcher = RSSFetcher()