import logging
from datetime import datetime
from googleapiclient.discovery import build
from src.config.settings import settings
from src.config.database import get_db
from src.models.schema import YouTubeCache

logger = logging.getLogger(__name__)

class VideoService:
    def __init__(self):
        key = settings.YOUTUBE_API_KEY
        self.client = build('youtube', 'v3', developerKey=key) if key else None

    def find_video(self, title: str, keywords: list = None) -> str:
        if not settings.ENABLE_YOUTUBE_EMBED or not self.client: return None
        
        import hashlib
        query = f"{title} {' '.join(keywords[:2] if keywords else [])}"
        qhash = hashlib.md5(query.encode()).hexdigest()
        
        db = get_db()
        cached = db.query(YouTubeCache).filter(YouTubeCache.query_hash == qhash).first()
        if cached:
            db.close()
            return cached.video_url

        try:
            req = self.client.search().list(part="snippet", q=query, type="video", maxResults=1, videoEmbeddable="true")
            res = req.execute()
            if not res['items']: return None
            
            vid_url = f"https://www.youtube.com/watch?v={res['items'][0]['id']['videoId']}"
            db.add(YouTubeCache(query_hash=qhash, video_url=vid_url, created_at=datetime.now()))
            db.commit()
            return vid_url
        except Exception:
            return None
        finally:
            db.close()