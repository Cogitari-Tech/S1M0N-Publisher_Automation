import os
import sys
import logging
from pathlib import Path
from typing import Optional, Final
from dotenv import load_dotenv

# ==============================================================================
# SETTINGS & CONFIGURATION - CONTENT ROBOT v7.0
# ==============================================================================
# Responsável por carregar, validar e centralizar todas as configurações.
# Garante que segredos não fiquem espalhados pelo código (Hardcoded Secrets).
# ==============================================================================

# 1. SETUP DE CAMINHOS
# ------------------------------------------------------------------------------
# Resolve o caminho raiz do projeto (assumindo que este arquivo está em src/config/)
BASE_DIR: Final[Path] = Path(__file__).resolve().parent.parent.parent
ENV_PATH: Final[Path] = BASE_DIR / '.env'

# Carrega o arquivo .env se existir
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH, override=True)
else:
    # Loga um aviso mas não falha, pois as variáveis podem vir do ambiente (Docker/Cloud)
    logging.warning(f"⚠️  Arquivo .env não encontrado em: {ENV_PATH}")


class Settings:
    """
    Classe estática para acesso global às configurações.
    Implementa validação básica para garantir integridade.
    """

    # --- SISTEMA & FLASK ---
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()
    FLASK_SECRET_KEY: str = os.getenv("FLASK_SECRET_KEY", "")
    DATABASE_URI: str = os.getenv("DATABASE_URI", "sqlite:///content_robot.db")
    
    # --- AUTOMATION CONTROLS ---
    MAX_ARTICLES_PER_CYCLE: int = int(os.getenv("MAX_ARTICLES_PER_CYCLE", 5))
    REQUIRE_MANUAL_APPROVAL: bool = os.getenv("REQUIRE_MANUAL_APPROVAL", "True").lower() == "true"

    # --- GOOGLE CLOUD (VERTEX AI) ---
    GOOGLE_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY")
    GOOGLE_PROJECT_ID: Optional[str] = os.getenv("GOOGLE_PROJECT_ID")
    GOOGLE_LOCATION: str = os.getenv("GOOGLE_LOCATION", "us-central1")
    AI_MODEL_TYPE: str = os.getenv("AI_MODEL_TYPE", "pro").lower() # pro, flash

    # --- YOUTUBE ---
    YOUTUBE_API_KEY: Optional[str] = os.getenv("YOUTUBE_API_KEY")

    # --- NEWS PROVIDERS (AGREGADORES) ---
    NEWSAPI_KEY: Optional[str] = os.getenv("NEWSAPI_KEY")
    CURRENTS_API_KEY: Optional[str] = os.getenv("CURRENTS_API_KEY")
    GNEWS_API_KEY: Optional[str] = os.getenv("GNEWS_API_KEY")

    # --- WORDPRESS (CMS) ---
    WORDPRESS_URL: Optional[str] = os.getenv("WORDPRESS_URL")
    WORDPRESS_USERNAME: Optional[str] = os.getenv("WORDPRESS_USERNAME")
    WORDPRESS_PASSWORD: Optional[str] = os.getenv("WORDPRESS_PASSWORD")

    @classmethod
    def validate(cls) -> None:
        """
        Verifica se as configurações críticas estão presentes.
        Levanta exceção se algo essencial estiver faltando.
        """
        errors = []

        # 0. Verificação de Gitignore (Segurança de Código)
        gitignore_path = BASE_DIR / '.gitignore'
        if gitignore_path.exists():
            try:
                with open(gitignore_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if '.env' not in content:
                         errors.append("❌ GRAVE: O arquivo '.env' NÃO está listado no .gitignore. Risco de vazamento de credenciais.")
            except Exception as e:
                logging.warning(f"⚠️ Não foi possível ler .gitignore: {e}")
        
        # 1. Segurança Web
        if not cls.FLASK_SECRET_KEY:
            errors.append("❌ FLASK_SECRET_KEY não está definida. O Dashboard está vulnerável.")

        # 2. Motor de IA (Essencial para o Robô)
        if not cls.GOOGLE_API_KEY:
            errors.append("❌ GOOGLE_API_KEY ausente. O Content Engine não funcionará.")
            
        # 3. Publicação (Aviso apenas, não bloqueante se for modo dev)
        if not cls.WORDPRESS_URL:
            logging.warning("⚠️  WORDPRESS_URL não configurada. A publicação falhará.")

        if errors:
            error_msg = "\n".join(errors)
            logging.critical(f"\nERRO DE CONFIGURAÇÃO:\n{error_msg}")
            # FALHA SEGURA: Impede a inicialização se houver riscos graves
            # Exceto em ambiente de testes (CI/pytest)
            if not (os.getenv('CI') or os.getenv('PYTEST_CURRENT_TEST')):
                sys.exit(1) 

    @staticmethod
    def get(key: str, default: any = None) -> any:
        """Obtém configuração do env."""
        return os.getenv(key, default)

    @staticmethod
    def get_bool(key: str, default: bool = False) -> bool:
        """Helper seguro para booleanos."""
        val = str(os.getenv(key, str(default))).lower()
        return val in ("true", "1", "yes", "on")

    @classmethod
    def as_dict(cls) -> dict:
        """Retorna configurações não-sensíveis para debug."""
        return {
            "BASE_DIR": str(BASE_DIR),
            "LOG_LEVEL": cls.LOG_LEVEL,
            "GOOGLE_PROJECT": cls.GOOGLE_PROJECT_ID,
            "WP_URL": cls.WORDPRESS_URL,
            "PROVIDERS": {
                "NewsAPI": bool(cls.NEWSAPI_KEY),
                "Currents": bool(cls.CURRENTS_API_KEY),
                "GNews": bool(cls.GNEWS_API_KEY)
            }
        }

# ==============================================================================
# EXECUÇÃO DE VERIFICAÇÃO (Ao importar)
# ==============================================================================
# Configuração básica de log para garantir que erros sejam vistos
logging.basicConfig(
    level=getattr(logging, Settings.LOG_LEVEL, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Valida ao carregar o módulo
Settings.validate()

# Exporta como objeto instanciado (ou alias de classe) para compatibilidade
settings = Settings