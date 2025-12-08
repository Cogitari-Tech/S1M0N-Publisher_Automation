import logging
import feedparser
from datetime import datetime
from time import mktime
from typing import List
from src.providers.base_provider import BaseNewsProvider, NewsItem
from src.config.database import get_db
from src.models.schema import RSSFeed

logger = logging.getLogger(__name__)

class RSSProvider(BaseNewsProvider):
    @property
    def provider_name(self) -> str: return 'rss'

    def fetch(self, limit: int = 3) -> List[NewsItem]:
        news_items = []
        db = get_db()
        try:
            active_feeds = db.query(RSSFeed).filter(RSSFeed.is_active == True).all()
            for feed_record in active_feeds:
                try:
                    feed_data = feedparser.parse(feed_record.url)
                    if feed_data.bozo and not feed_data.entries: continue
                    for entry in feed_data.entries[:limit]:
                        pub_date = datetime.now()
                        if hasattr(entry, 'published_parsed') and entry.published_parsed:
                            pub_date = datetime.fromtimestamp(mktime(entry.published_parsed))
                        
                        news_items.append(NewsItem(
                            url=entry.link,
                            title=entry.title,
                            source_name=f"{feed_record.name} (RSS)",
                            published_date=pub_date,
                            summary=entry.get('summary', '') or entry.get('description', ''),
                            author=entry.get('author', 'Unknown')
                        ))
                except Exception as e:
                    logger.error(f"Erro no feed {feed_record.url}: {e}")
        finally:
            db.close()
        return news_items