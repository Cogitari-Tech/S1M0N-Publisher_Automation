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
        from src.config.database import get_db
        from src.models.schema import SystemSettings
        
        all_news = []
        hashes = set()
        
        # Mapa de provedores para chaves de configuração
        provider_map = {
            'GNews': 'enable_gnews',
            'NewsAPI': 'enable_newsapi',
            'Currents': 'enable_currents',
            'RSS': None # RSS sempre ativo ou controlado por outra flag? Assumindo sempre ativo por enquanto ou config própria
        }

        db = get_db()
        settings_cache = {s.key: s.value for s in db.query(SystemSettings).all()}
        db.close()

        for p in self.providers:
            # Verifica se o provedor está habilitado
            config_key = provider_map.get(p.provider_name) # Assumes provider has .provider_name property matching these keys
            
            # Se tiver chave de config, verifica. Se for 'false', pula.
            if config_key:
                is_enabled = settings_cache.get(config_key, 'true').lower() == 'true'
                if not is_enabled:
                    logger.info(f"⏭️ Skipping {p.provider_name} (Disabled via Settings)")
                    continue

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