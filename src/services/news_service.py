import logging
from typing import List
from src.providers.rss_provider import RSSProvider
from src.providers.gnews_provider import GNewsProvider
from src.providers.currents_provider import CurrentsProvider
from src.providers.newsapi_provider import NewsAPIProvider

logger = logging.getLogger(__name__)

class NewsService:
    def __init__(self):
        self.providers = [RSSProvider(), GNewsProvider(), CurrentsProvider(), NewsAPIProvider()]

    def fetch_all(self, items_per_source=3) -> List:
        all_news = []
        hashes = set()
        for p in self.providers:
            try:
                items = p.fetch(limit=items_per_source)
                for item in items:
                    h = item.get_hash()
                    if h not in hashes:
                        hashes.add(h)
                        all_news.append(item)
            except Exception as e:
                logger.error(f"Erro em {p.provider_name}: {e}")
        return all_news