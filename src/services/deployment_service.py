import logging
import os
from src.config.settings import settings

logger = logging.getLogger(__name__)

class DeploymentService:
    @staticmethod
    def prepare_build(env: str = 'DEV') -> bool:
        """
        Valida integridade do ambiente antes de processos críticos.
        
        Args:
            env (str): 'DEV' ou 'PROD'.
        
        Returns:
            bool: True se válido, False se inválido (em DEV).
        
        Raises:
            EnvironmentError: Se inválido em PROD.
        """
        logger.info(f"🔐 Validating secure build for ENV: {env}")
        
        # Check critical keys (never log values!)
        critical_vars = {
            'GOOGLE_API_KEY': settings.GOOGLE_API_KEY,
            'FLASK_SECRET_KEY': settings.FLASK_SECRET_KEY,
        }
        
        missing = [k for k, v in critical_vars.items() if not v]
        
        # Production strict checks
        if env == 'PROD':
            if not settings.WORDPRESS_URL:
                missing.append('WORDPRESS_URL')
        
        if missing:
            error_msg = f"⛔ Build Blocked. Missing keys: {', '.join(missing)}"
            if env == 'PROD':
                raise EnvironmentError(error_msg)
            else:
                logger.warning(f"{error_msg} (Allowed in DEV)")
                return False
                
        logger.info("✅ Environment validated. Build prepared.")
        return True
