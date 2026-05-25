import httpx
import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any

from .smi_sources import get_top_smi_sources

logger = logging.getLogger(__name__)


class AsyncRSSParser:
    def __init__(self, timeout: int = 10, max_concurrent: int = 15):
        self.timeout = timeout
        self.max_concurrent = max_concurrent
        self.session = None
    
    async def _get_session(self) -> httpx.AsyncClient:
        if self.session is None:
            self.session = httpx.AsyncClient(timeout=self.timeout, follow_redirects=True)
        return self.session
    
    async def close(self):
        if self.session:
            await self.session.aclose()
            self.session = None
    
    async def fetch_source(self, source: Dict[str, str]) -> List[Dict[str, Any]]:
        articles = []
        url = source.get("url", "")
        
        try:
            client = await self._get_session()
            response = await client.get(url)
            response.raise_for_status()
            
            content = response.text
            items = self._parse_rss(content)
            
            for item in items[:10]:
                title = item.get('title', '').strip()
                link = item.get('link', '').strip()
                
                if not title or not link:
                    continue
                
                articles.append({
                    "title": title,
                    "link": link,
                    "description": item.get('description', '')[:500],
                    "full_text": item.get('description', '')[:2000],
                    "published_at": item.get('pubDate'),
                    "source_name": source.get("name", ""),
                    "category": source.get("category", ""),
                })
        
        except Exception as e:
            logger.warning(f"{source.get('name')}: {e}")
        
        return articles
    
    def _parse_rss(self, content: str) -> List[Dict]:
        import re
        items = []
        
        item_pattern = re.compile(r'<item>(.*?)</item>', re.DOTALL)
        title_pattern = re.compile(r'<title><!\[CDATA\[(.*?)\]\]></title>|<title>(.*?)</title>', re.DOTALL)
        link_pattern = re.compile(r'<link>(.*?)</link>', re.DOTALL)
        desc_pattern = re.compile(r'<description><!\[CDATA\[(.*?)\]\]></description>|<description>(.*?)</description>', re.DOTALL)
        date_pattern = re.compile(r'<pubDate>(.*?)</pubDate>', re.DOTALL)
        
        for match in item_pattern.finditer(content):
            item_xml = match.group(1)
            
            title_match = title_pattern.search(item_xml)
            title = title_match.group(1) or title_match.group(2) if title_match else ''
            
            link_match = link_pattern.search(item_xml)
            link = link_match.group(1) if link_match else ''
            
            desc_match = desc_pattern.search(item_xml)
            desc = desc_match.group(1) or desc_match.group(2) if desc_match else ''
            
            date_match = date_pattern.search(item_xml)
            date = date_match.group(1) if date_match else None
            
            if title:
                items.append({
                    'title': title.strip(),
                    'link': link.strip(),
                    'description': desc.strip() if desc else '',
                    'pubDate': date
                })
        
        return items
    
    async def fetch_all(self) -> List[Dict[str, Any]]:
        sources = get_top_smi_sources()
        all_articles = []
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def fetch(src):
            async with semaphore:
                return await self.fetch_source(src)
        
        tasks = [fetch(s) for s in sources]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(results):
            if isinstance(result, list):
                all_articles.extend(result)
                logger.info(f"[{i+1}/{len(sources)}] {sources[i]['name']}: {len(result)}")
        
        return all_articles
    
    async def search(self, query: str, max_results: int = 30) -> List[Dict[str, Any]]:
        articles = await self.fetch_all()
        
        if not query.strip():
            return articles[:max_results]
        
        query_words = [w.strip().lower() for w in query.split() if len(w.strip()) > 1]
        
        if not query_words:
            return articles[:max_results]
        
        scored = []
        for a in articles:
            title = a.get("title", "").lower()
            desc = a.get("description", "").lower()
            full_text = a.get("full_text", "").lower()
            
            score = 0
            
            for word in query_words:
                if len(word) < 2:
                    continue
                score += title.count(word) * 10
                score += desc[:300].count(word) * 3
                score += full_text[:1000].count(word) * 1
            
            if score > 0:
                scored.append((score, a))
        
        scored.sort(reverse=True, key=lambda x: x[0])
        results = [a for _, a in scored[:max_results]]
        
        if len(results) < 3 and len(articles) > max_results:
            results = articles[:max_results]
        
        return results


async def fetch_smi_articles(topic: str = None, max_results: int = 30) -> Dict[str, Any]:
    parser = AsyncRSSParser(timeout=10, max_concurrent=15)
    
    try:
        articles = await parser.search(topic or "", max_results)
        
        sources_count = {}
        for a in articles:
            name = a.get("source_name", "Unknown")
            sources_count[name] = sources_count.get(name, 0) + 1
        
        return {
            "articles": articles,
            "total_found": len(articles),
            "sources": sources_count,
            "topic": topic
        }
    finally:
        await parser.close()