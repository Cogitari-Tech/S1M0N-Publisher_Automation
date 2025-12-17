import logging
import requests
from datetime import datetime
from typing import List
from src.providers.base_provider import BaseNewsProvider, NewsItem
from src.config.settings import settings

class NewsAPIProvider(BaseNewsProvider):
    BASE_URL = "https://newsapi.org/v2/top-headlines"
    
    @property
    def provider_name(self) -> str: return 'newsapi'

    def fetch(self, limit: int = 5) -> List[NewsItem]:
        if not settings.get_bool('enable_newsapi', False): return []
        api_key = settings.get('newsapi_key')
        if not api_key: return []

        try:
            resp = requests.get(self.BASE_URL, params={'apiKey': api_key, 'country': 'br', 'pageSize': limit}, timeout=10)
            if resp.status_code != 200: return []
            
            items = []
            for art in resp.json().get('articles', []):
                if not art.get('url') or not art.get('title'): continue
                items.append(NewsItem(
                    url=art.get('url'),
                    title=art.get('title'),
                    source_name="NewsAPI",
                    published_date=datetime.now(),
                    summary=art.get('description', ''),
                    author=art.get('author')
                ))
            return items
        except Exception:
            return []