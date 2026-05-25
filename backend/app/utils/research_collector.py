import httpx
import asyncio
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import re
from urllib.parse import quote
from app.config import settings


class ResearchDataCollector:
    """Сервис для сбора данных из бесплатных источников для маркетинговых исследований"""

    def __init__(self):
        self.session = None
        self.proxy = settings.GIGACHAT_PROXY

    async def _get_session(self):
        if self.session is None:
            kwargs = {
                "headers": {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Accept": "application/json, text/plain, */*",
                },
                "timeout": 30.0,
                "follow_redirects": True,
            }
            self.session = httpx.AsyncClient(**kwargs)
        return self.session

    # ─── World Bank ────────────────────────────────────────────────
    async def fetch_world_bank_data(self, indicator: str, country: str = "world", date: str = "2019:2024") -> List[Dict[str, Any]]:
        try:
            session = await self._get_session()
            url = f"http://api.worldbank.org/v2/country/{country}/indicator/{indicator}?date={date}&format=json&per_page=100"
            response = await session.get(url)
            if response.status_code == 200:
                data = response.json()
                if len(data) > 1 and data[1]:
                    return [{
                        "indicator": indicator, "country": item.get("country", {}).get("value"),
                        "country_code": item.get("country", {}).get("id"), "date": item.get("date"),
                        "value": item.get("value"), "source": "World Bank",
                    } for item in data[1] if item.get("value") is not None]
            return []
        except Exception as e:
            print(f"World Bank error: {e}"); return []

    # ─── Google Trends ─────────────────────────────────────────────
    async def fetch_google_trends(self, keyword: str, geo: str = "RU") -> List[Dict[str, Any]]:
        try:
            from .trends_service import trends_service
            trends = await trends_service.get_trending_searches()
            return [{
                "keyword": keyword, "geo": geo,
                "trends": [t.get("title", "") for t in trends[:10]],
                "descriptions": [t.get("description", "") for t in trends[:5]],
                "source": "Google Trends RSS", "timestamp": datetime.now().isoformat(),
            }]
        except Exception as e:
            print(f"Google Trends error: {e}"); return []

    # ─── arXiv ─────────────────────────────────────────────────────
    async def fetch_arxiv_papers(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        try:
            session = await self._get_session()
            url = f"http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results={max_results}"
            response = await session.get(url)
            if response.status_code == 200:
                import xml.etree.ElementTree as ET
                root = ET.fromstring(response.text)
                ns = {'atom': 'http://www.w3.org/2005/Atom'}
                papers = []
                for entry in root.findall('atom:entry', ns):
                    title_elem = entry.find('atom:title', ns)
                    summary_elem = entry.find('atom:summary', ns)
                    published_elem = entry.find('atom:published', ns)
                    id_elem = entry.find('atom:id', ns)
                    authors = [a.text or "" for a in entry.findall('atom:author/atom:name', ns)]
                    papers.append({
                        "title": title_elem.text.strip() if title_elem.text else "",
                        "summary": summary_elem.text.strip()[:500] if summary_elem.text else "",
                        "published": published_elem.text if published_elem.text else "",
                        "id": id_elem.text if id_elem.text else "",
                        "authors": authors, "source": "arXiv.org",
                    })
                return papers
            return []
        except Exception as e:
            print(f"arXiv error: {e}"); return []

    # ─── Reddit ─────────────────────────────────────────────────────
    async def fetch_reddit_posts(self, subreddit: str, query: str = "", limit: int = 10) -> List[Dict[str, Any]]:
        for attempt in range(2):
            try:
                session = self.session if attempt == 0 else httpx.AsyncClient(
                    headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"},
                    timeout=15.0, follow_redirects=True,
                )
                url = f"https://www.reddit.com/r/{subreddit}/search.json?q={query}&limit={limit}" if query else f"https://www.reddit.com/r/{subreddit}/hot.json?limit={limit}"
                response = await session.get(url)
                if response.status_code == 200:
                    posts = response.json().get("data", {}).get("children", [])
                    return [{
                        "title": p.get("data", {}).get("title", ""),
                        "selftext": p.get("data", {}).get("selftext", "")[:300],
                        "score": p.get("data", {}).get("score", 0),
                        "num_comments": p.get("data", {}).get("num_comments", 0),
                        "subreddit": p.get("data", {}).get("subreddit", ""),
                        "source": f"Reddit r/{subreddit}",
                    } for p in posts]
                return []
            except:
                if attempt == 0: continue
                return []
        return []

    # ─── Wikipedia API ─────────────────────────────────────────────
    async def fetch_wikipedia_summary(self, query: str) -> List[Dict[str, Any]]:
        """Обзор индустрии, ключевые термины, история рынка"""
        try:
            session = await self._get_session()
            url = f"https://ru.wikipedia.org/api/rest_v1/page/summary/{quote(query.replace(' ', '_'))}"
            response = await session.get(url, follow_redirects=True)
            if response.status_code == 200:
                data = response.json()
                return [{
                    "title": data.get("title", query),
                    "extract": data.get("extract", ""),
                    "url": f"https://ru.wikipedia.org/wiki/{data.get('title', query).replace(' ', '_')}",
                    "source": "Wikipedia",
                }]
            # попробуем поиск
            search_url = f"https://ru.wikipedia.org/w/api.php?action=query&list=search&srsearch={query}&format=json&srlimit=3"
            sr = await session.get(search_url)
            if sr.status_code == 200:
                results = sr.json().get("query", {}).get("search", [])
                return [{"title": r.get("title", ""), "extract": r.get("snippet", "").replace("<span class=\"searchmatch\">", "").replace("</span>", ""), "source": "Wikipedia (search)"} for r in results[:3]]
            return []
        except Exception as e:
            print(f"Wikipedia error: {e}"); return []

    # ─── News API ──────────────────────────────────────────────────
    async def fetch_news(self, query: str) -> List[Dict[str, Any]]:
        """Свежие новости по теме (NewsAPI.org)"""
        api_key = settings.NEWSAPI_KEY or ""
        if not api_key:
            return []
        try:
            session = await self._get_session()
            url = f"https://newsapi.org/v2/everything?q={query}&pageSize=5&language=ru&sortBy=relevancy&apiKey={api_key}"
            response = await session.get(url)
            if response.status_code == 200:
                articles = response.json().get("articles", [])
                return [{
                    "title": a.get("title", ""), "description": a.get("description", ""),
                    "url": a.get("url", ""), "source_name": a.get("source", {}).get("name", ""),
                    "published": a.get("publishedAt", "")[:10], "source": "NewsAPI",
                } for a in articles[:5]]
            return []
        except Exception as e:
            print(f"NewsAPI error: {e}"); return []

    # ─── GitHub API ────────────────────────────────────────────────
    async def fetch_github_projects(self, query: str) -> List[Dict[str, Any]]:
        """Open-source проекты, инструменты в нише"""
        try:
            session = await self._get_session()
            url = f"https://api.github.com/search/repositories?q={query}+in:name,description&sort=stars&per_page=5"
            token = getattr(settings, "GITHUB_TOKEN", "")
            headers = {"Authorization": f"Bearer {token}"} if token else {}
            response = await session.get(url, headers=headers)
            if response.status_code == 200:
                items = response.json().get("items", [])
                return [{
                    "name": r.get("full_name", ""), "description": r.get("description", "") or "",
                    "stars": r.get("stargazers_count", 0), "language": r.get("language", ""),
                    "url": r.get("html_url", ""), "source": "GitHub",
                } for r in items[:5]]
            return []
        except Exception as e:
            print(f"GitHub error: {e}"); return []

    # ─── Google Books API ──────────────────────────────────────────
    async def fetch_google_books(self, query: str) -> List[Dict[str, Any]]:
        """Книги и публикации по теме"""
        try:
            session = await self._get_session()
            url = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults=5&langRestrict=ru"
            response = await session.get(url)
            if response.status_code == 200:
                items = response.json().get("items", [])
                return [{
                    "title": v.get("volumeInfo", {}).get("title", ""),
                    "authors": v.get("volumeInfo", {}).get("authors", []),
                    "description": (v.get("volumeInfo", {}).get("description", "") or "")[:300],
                    "published": v.get("volumeInfo", {}).get("publishedDate", ""),
                    "link": v.get("volumeInfo", {}).get("infoLink", ""),
                    "source": "Google Books",
                } for v in items[:5]]
            return []
        except Exception as e:
            print(f"Google Books error: {e}"); return []

    # ─── Wikipedia Pageviews ───────────────────────────────────────
    async def fetch_wikipedia_pageviews(self, query: str, days: int = 30) -> List[Dict[str, Any]]:
        """Популярность темы во времени"""
        try:
            session = await self._get_session()
            from datetime import timedelta
            end = datetime.now()
            start = end - timedelta(days=days)
            date_fmt = "%Y%m%d"
            title = query.replace(" ", "_")
            url = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/ru.wikipedia/all-access/all-agents/{title}/daily/{start.strftime(date_fmt)}/{end.strftime(date_fmt)}"
            response = await session.get(url)
            if response.status_code == 200:
                items = response.json().get("items", [])
                total = sum(i.get("views", 0) for i in items)
                avg = total / len(items) if items else 0
                return [{
                    "title": query, "total_views_30d": total, "avg_daily": round(avg, 0),
                    "source": "Wikipedia Pageviews",
                }]
            return []
        except Exception as e:
            print(f"Wikipedia pageviews error: {e}"); return []

    # ─── Open Library API ──────────────────────────────────────────
    async def fetch_open_library(self, query: str) -> List[Dict[str, Any]]:
        """Книги, авторы, исследования"""
        try:
            session = await self._get_session()
            url = f"https://openlibrary.org/search.json?q={query}&limit=5"
            response = await session.get(url)
            if response.status_code == 200:
                docs = response.json().get("docs", [])
                return [{
                    "title": d.get("title", ""),
                    "authors": d.get("author_name", []),
                    "published": d.get("first_publish_year", ""),
                    "subject": (d.get("subject", []) or [])[:3],
                    "link": f"https://openlibrary.org{d.get('key', '')}" if d.get("key") else "",
                    "source": "Open Library",
                } for d in docs[:5]]
            return []
        except Exception as e:
            print(f"Open Library error: {e}"); return []

    # ─── Reddit (упрощённый) ───────────────────────────────────────
    # (уже есть выше как fetch_reddit_posts)

    # ─── Сбор всех данных ──────────────────────────────────────────
    async def collect_comprehensive_research_data(self, topic: str, industry: Optional[str] = None) -> Dict[str, Any]:
        """Собрать данные из ВСЕХ доступных источников параллельно"""
        keywords = [topic]
        if industry:
            keywords.append(f"{topic} {industry}")

        tasks = {}
        for kw in keywords[:2]:
            tasks[f"world_bank_gdp_{kw}"] = self.fetch_world_bank_data("NY.GDP.MKTP.CD", "RU", "2020:2024")
            tasks[f"world_bank_inflation_{kw}"] = self.fetch_world_bank_data("FP.CPI.TOTL.ZG", "RU", "2020:2024")
            tasks[f"world_bank_unemployment_{kw}"] = self.fetch_world_bank_data("SL.UEM.TOTL.ZS", "RU", "2020:2024")
            tasks[f"google_trends_{kw}"] = self.fetch_google_trends(kw)
            tasks[f"arxiv_{kw}"] = self.fetch_arxiv_papers(kw, 5)
            tasks[f"wikipedia_{kw}"] = self.fetch_wikipedia_summary(kw)
            tasks[f"github_{kw}"] = self.fetch_github_projects(kw)
            tasks[f"google_books_{kw}"] = self.fetch_google_books(kw)
            tasks[f"open_library_{kw}"] = self.fetch_open_library(kw)
            tasks[f"wiki_views_{kw}"] = self.fetch_wikipedia_pageviews(kw)

        tasks["reddit_marketing"] = self.fetch_reddit_posts("marketing", topic)
        tasks["reddit_digital_marketing"] = self.fetch_reddit_posts("digital_marketing", topic)
        tasks["news"] = self.fetch_news(topic)

        results = await asyncio.gather(*tasks.values(), return_exceptions=True)

        collected = {
            "world_bank": [], "google_trends": [], "arxiv": [], "reddit": [],
            "wikipedia": [], "news": [], "github": [], "google_books": [],
            "open_library": [], "wikipedia_pageviews": [],
        }

        keys = list(tasks.keys())
        for i, key in enumerate(keys):
            val = results[i] if i < len(results) else []
            if isinstance(val, Exception):
                continue
            if key.startswith("world_bank"): collected["world_bank"].extend(val if isinstance(val, list) else [])
            elif key.startswith("google_trends"): collected["google_trends"].extend(val if isinstance(val, list) else [])
            elif key.startswith("arxiv"): collected["arxiv"].extend(val if isinstance(val, list) else [])
            elif key.startswith("reddit"): collected["reddit"].extend(val if isinstance(val, list) else [])
            elif key.startswith("wikipedia") and not key.startswith("wiki_views"): collected["wikipedia"].extend(val if isinstance(val, list) else [])
            elif key.startswith("wiki_views"): collected["wikipedia_pageviews"].extend(val if isinstance(val, list) else [])
            elif key.startswith("github"): collected["github"].extend(val if isinstance(val, list) else [])
            elif key.startswith("google_books"): collected["google_books"].extend(val if isinstance(val, list) else [])
            elif key.startswith("open_library"): collected["open_library"].extend(val if isinstance(val, list) else [])
            elif key == "news": collected["news"].extend(val if isinstance(val, list) else [])

        return collected


research_collector = ResearchDataCollector()