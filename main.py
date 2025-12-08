import time
import logging
import schedule
import sys
import os

# Garante que o diretório raiz esteja no path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.config.database import init_db
from src.services.content_engine import ContentEngine

# Configuração de Logs Robusta
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.FileHandler("robot.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def safe_run_cycle(engine):
    """Executa o ciclo protegendo o processo principal de falhas."""
    try:
        engine.run_cycle()
    except Exception as e:
        logger.error(f"❌ CRITICAL ERROR no Ciclo: {e}", exc_info=True)
        # Não mata o processo, apenas registra e aguarda o próximo agendamento

def main():
    print("🤖 CONTENT ROBOT v7.1 (Robust) STARTING...")
    
    try:
        init_db()
    except Exception as e:
        logger.critical(f"Falha fatal no Banco de Dados: {e}")
        return

    try:
        engine = ContentEngine()
        
        # Ciclo de Boot (Executa imediatamente)
        safe_run_cycle(engine)
        
        # Agendamento
        schedule.every(2).hours.do(safe_run_cycle, engine)
        
        logger.info("✅ Motor iniciado. Aguardando agendamento...")
        
        while True:
            try:
                schedule.run_pending()
                time.sleep(1)
            except KeyboardInterrupt:
                logger.info("🛑 Parada manual solicitada.")
                break
            except Exception as e:
                logger.error(f"❌ Erro no Loop Principal: {e}")
                time.sleep(5) # Espera segura antes de tentar novamente
                
    except Exception as e:
        logger.critical(f"🔥 O Motor caiu: {e}", exc_info=True)

if __name__ == "__main__":
    main()