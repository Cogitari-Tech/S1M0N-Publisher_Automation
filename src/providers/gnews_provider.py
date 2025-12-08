import logging
import requests
from datetime import datetime
from typing import List
from src.providers.base_provider import BaseNewsProvider, NewsItem
from src.config.settings import settings

logger = logging.getLogger(__name__)

class GNewsProvider(BaseNewsProvider):
    BASE_URL = "https://gnews.io/api/v4/top-headlines"
    
    @property
    def provider_name(self) -> str: return 'gnews'

    def fetch(self, limit: int = 5) -> List[NewsItem]:
        if not settings.get_bool('enable_gnews', False): return []
        api_key = settings.get('gnews_api_key')
        if not api_key: return []

        try:
            resp = requests.get(self.BASE_URL, params={'token': api_key, 'lang': 'pt', 'country': 'br', 'max': limit}, timeout=10)
            if resp.status_code != 200: return []
            
            items = []
            for art in resp.json().get('articles', []):
                items.append(NewsItem(
                    url=art.get('url'),
                    title=art.get('title'),
                    source_name=f"GNews: {art.get('source', {}).get('name')}",
                    published_date=datetime.now(), 
                    summary=art.get('description', ''),
                    author=None
                ))
            return items
        except Exception as e:
            logger.error(f"Erro GNews: {e}")
            return []