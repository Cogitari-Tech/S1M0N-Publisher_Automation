from src.config.settings import settings
from .clients import GeminiProClient, GeminiFlashClient
from .interfaces import ModelClient

class ModelFactory:
    @staticmethod
    def create_client() -> ModelClient:
        key = settings.GOOGLE_API_KEY
        
        # 1. Try DB setting (Dynamic)
        from src.config.database import get_db
        from src.models.schema import SystemSettings
        
        mode = settings.AI_MODEL_TYPE # Default env
        db = get_db()
        try:
            s = db.query(SystemSettings).filter_by(key='ai_model_mode').first()
            if s and s.value:
                mode = s.value
        except Exception:
            pass
        finally:
            db.close()
        
        if mode == 'flash':
            return GeminiFlashClient(key)
        
        # Default to Pro
        return GeminiProClient(key)
