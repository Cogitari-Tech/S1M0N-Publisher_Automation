import os
import logging
from dotenv import load_dotenv
from src.config.database import get_db
from src.models.schema import SystemSettings

load_dotenv()
logger = logging.getLogger(__name__)

class Settings:
    @staticmethod
    def get(key: str, default: str = None) -> str:
        db = get_db()
        try:
            setting = db.query(SystemSettings).filter(SystemSettings.key == key).first()
            if setting and setting.value:
                return setting.value
        except Exception:
            pass
        finally:
            db.close()
        return os.getenv(key) or os.getenv(key.upper()) or default

    @staticmethod
    def get_bool(key: str, default: bool = False) -> bool:
        val = Settings.get(key, str(default))
        if val is None: return default
        return val.lower() in ('true', '1', 'yes', 'on', 'enabled')

    @staticmethod
    def get_int(key: str, default: int = 0) -> int:
        try:
            return int(Settings.get(key, str(default)))
        except (ValueError, TypeError):
            return default

    @property
    def WORDPRESS_URL(self) -> str: return self.get('wordpress_url')
    @property
    def WORDPRESS_USERNAME(self) -> str: return self.get('wordpress_username')
    @property
    def WORDPRESS_PASSWORD(self) -> str: return self.get('wordpress_password')
    @property
    def GOOGLE_API_KEY(self) -> str: return self.get('google_api_key')
    @property
    def GOOGLE_PROJECT_ID(self) -> str: return self.get('google_project_id')
    @property
    def GOOGLE_LOCATION(self) -> str: return self.get('google_location', 'us-central1')
    @property
    def YOUTUBE_API_KEY(self) -> str: return self.get('youtube_api_key')
    @property
    def ENABLE_GLOBAL_IMAGES(self) -> bool: return self.get_bool('enable_global_images', True)
    @property
    def ENABLE_YOUTUBE_EMBED(self) -> bool: return self.get_bool('enable_youtube_embed', True)
    @property
    def REQUIRE_MANUAL_APPROVAL(self) -> bool: return self.get_bool('require_manual_approval', True)
    @property
    def MAX_ARTICLES_PER_CYCLE(self) -> int: return self.get_int('max_articles_cycle', 5)
    @property
    def IMAGE_PROMPT_STYLE(self) -> str: return self.get('image_prompt_style', 'Editorial illustration, photorealistic, 4k')

settings = Settings()