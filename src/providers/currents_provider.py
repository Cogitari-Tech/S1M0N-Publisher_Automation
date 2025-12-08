import logging
import requests
from datetime import datetime
from typing import List
from src.providers.base_provider import BaseNewsProvider, NewsItem
from src.config.settings import settings

logger = logging.getLogger(__name__)

class CurrentsProvider(BaseNewsProvider):
    BASE_URL = "https://api.currentsapi.services/v1/latest-news"

    @property
    def provider_name(self) -> str: return 'currents'

    def fetch(self, limit: int = 5) -> List[NewsItem]:
        if not settings.get_bool('enable_currents', False): return []
        api_key = settings.get('currents_api_key')
        if not api_key: return []

        try:
            resp = requests.get(self.BASE_URL, params={'apiKey': api_key, 'language': 'pt'}, timeout=15)
            if resp.status_code != 200: return []
            
            items = []
            for art in resp.json().get('news', [])[:limit]:
                items.append(NewsItem(
                    url=art.get('url'),
                    title=art.get('title'),
                    source_name=f"Currents: {art.get('author', 'Unknown')}",
                    published_date=datetime.now(),
                    summary=art.get('description', ''),
                    author=art.get('author')
                ))
            return items
        except Exception:
            return []