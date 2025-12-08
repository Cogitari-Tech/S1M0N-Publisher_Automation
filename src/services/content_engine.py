import time
import logging
import requests
import json
import os
import hashlib
from datetime import datetime
from src.config.settings import settings
from src.config.database import get_db
from src.models.schema import PublishedArticle, PendingArticle
from src.services.news_service import NewsService
from src.services.ai_service import AIService
from src.services.video_service import VideoService
from src.providers.base_provider import NewsItem

logger = logging.getLogger(__name__)

class ContentEngine:
    def __init__(self):
        self.news_service = NewsService()
        self.ai_service = AIService()
        self.video_service = VideoService()

    def run_cycle(self):
        logger.info("🚀 Iniciando ciclo...")
        articles = self.news_service.fetch_all(3)
        processed = 0
        for item in articles:
            if processed >= settings.MAX_ARTICLES_PER_CYCLE: break
            if self._is_duplicate(item.get_hash()): continue
            
            if self._process_article(item, False):
                processed += 1
                time.sleep(5)

    def run_evergreen(self, topic: str):
        mock = NewsItem(url="gen", title=topic, source_name="Evergreen", published_date=datetime.now())
        self._process_article(mock, True)

    def _process_article(self, item, is_evergreen):
        ai_content = self.ai_service.generate_article(item, is_evergreen)
        if not ai_content: return False
        
        img_path = self.ai_service.generate_image(ai_content['titulo'])
        vid_url = self.video_service.find_video(ai_content['titulo'], ai_content.get('palavras_chave'))
        
        ai_content['conteudo_completo'] = self._enrich(ai_content['conteudo_completo'], vid_url)
        
        if settings.REQUIRE_MANUAL_APPROVAL:
            return self._save_pending(ai_content, item, img_path, vid_url)
        else:
            return self._publish_wp(ai_content, item, img_path, vid_url)

    def _enrich(self, html, vid_url):
        if vid_url:
            vid_id = vid_url.split('v=')[-1]
            html += f'<div class="video"><iframe src="https://www.youtube.com/embed/{vid_id}"></iframe></div>'
        return html

    def _save_pending(self, content, item, img, vid):
        db = get_db()
        try:
            # FIX: Tabela PendingArticle agora existe no schema.py
            pend = PendingArticle(
                title=content['titulo'],
                original_url=item.url,
                source_name=item.source_name,
                content_json=json.dumps(content),
                image_path=img,
                video_url=vid,
                status='PENDING'
            )
            db.add(pend)
            db.commit()
            logger.info("📋 Artigo enviado para aprovação.")
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar pendente: {e}")
            return False
        finally:
            db.close()

    def _publish_wp(self, content, item, img, vid):
        # Lógica simplificada de publicação WP
        # Na versão real, usa requests.post para /posts
        db = get_db()
        try:
            pub = PublishedArticle(
                hash=item.get_hash(),
                title=content['titulo'],
                full_content=content['conteudo_completo'],
                source=item.source_name,
                published_date=datetime.now()
            )
            db.add(pub)
            db.commit()
            logger.info(f"✅ Publicado: {content['titulo']}")
            return True
        except Exception as e:
            logger.error(f"Erro WP: {e}")
            return False
        finally:
            db.close()

    def _is_duplicate(self, h):
        db = get_db()
        exists = db.query(PublishedArticle).filter(PublishedArticle.hash == h).first()
        db.close()
        return exists is not None