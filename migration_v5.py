"""
Migração do Banco de Dados v4.0 -> v5.0
Cria a tabela de configurações dinâmicas e popula com defaults
"""
import sqlite3
import logging
import os
from datetime import datetime
from dotenv import load_dotenv

# Carrega variáveis de ambiente para usar como valores iniciais
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DB_NAME = 'content_robot.db'

def get_env_default(key, default_value):
    """Helper para pegar valor do .env ou usar default"""
    val = os.getenv(key)
    return val if val else default_value

def migrate_database_v5():
    """Executa migração para v5.0 (System Settings)"""
    conn = None
    try:
        if not os.path.exists(DB_NAME):
            logger.error(f"❌ Banco de dados {DB_NAME} não encontrado. Execute o robô pelo menos uma vez antes.")
            return False

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        logger.info("🔄 Iniciando migração v4.0 -> v5.0...")
        
        # ==========================================
        # 1. CRIAR TABELA system_settings
        # ==========================================
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_settings (
                    key VARCHAR(100) PRIMARY KEY,
                    value TEXT,
                    description VARCHAR(255),
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            logger.info("✅ Tabela system_settings verificada/criada")
        except sqlite3.Error as e:
            logger.error(f"❌ Erro ao criar tabela: {e}")
            return False

        # ==========================================
        # 2. DEFINIR CONFIGURAÇÕES PADRÃO (SEED)
        # ==========================================
        # Lista de configurações iniciais (Key, Value, Description)
        default_settings = [
            # Segurança e Fluxo
            ('max_articles_cycle', '5', 'Limite máximo de artigos por ciclo (Hard Limit)'),
            ('check_interval_minutes', '120', 'Intervalo entre ciclos automáticos (minutos)'),
            
            # Credenciais WordPress
            ('wordpress_url', get_env_default('WORDPRESS_URL', ''), 'URL do WordPress'),
            ('wordpress_username', get_env_default('WORDPRESS_USERNAME', ''), 'Usuário do WordPress'),
            ('wordpress_password', get_env_default('WORDPRESS_PASSWORD', ''), 'Application Password do WordPress'),
            
            # Credenciais APIs
            ('youtube_api_key', get_env_default('YOUTUBE_API_KEY', ''), 'Chave da API do YouTube'),
            ('stability_api_key', get_env_default('STABILITY_API_KEY', ''), 'Chave da Stability AI'),
            
            # Configurações de Conteúdo
            ('image_prompt_style', 'Editorial illustration, modern style, minimal, high quality', 'Estilo padrão para geração de imagens'),
            ('min_quality_score', '60', 'Nota mínima de qualidade para publicação'),
            ('generate_images', 'true', 'Gerar imagens com IA (true/false)'),
            ('require_manual_approval', 'true', 'Exigir aprovação manual (true/false)')
        ]

        logger.info("⚙️  Populando configurações iniciais...")
        
        for key, value, description in default_settings:
            # Upsert: Insere se não existe, ignora se já existe (para não sobrescrever edições futuras)
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO system_settings (key, value, description, updated_at)
                    VALUES (?, ?, ?, ?)
                ''', (key, value, description, datetime.now()))
            except sqlite3.Error as e:
                logger.warning(f"⚠️  Erro ao inserir {key}: {e}")

        conn.commit()
        
        # ==========================================
        # 3. VERIFICAÇÃO
        # ==========================================
        cursor.execute("SELECT count(*) FROM system_settings")
        count = cursor.fetchone()[0]
        
        logger.info(f"✅ Migração concluída! {count} configurações ativas.")
        logger.info("="*50)
        logger.info("PRÓXIMOS PASSOS:")
        logger.info("1. O Content Robot passará a ler configurações do Banco de Dados.")
        logger.info("2. Use o Dashboard para alterar chaves e limites em tempo real.")
        logger.info("="*50)
        
        return True

    except Exception as e:
        logger.error(f"❌ Erro fatal na migração: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    import sys
    
    print("""
    ╔══════════════════════════════════════════╗
    ║   🔄 MIGRAÇÃO v5.0 (SETTINGS DB)         ║
    ║                                          ║
    ║   Cria tabela para gestão dinâmica       ║
    ║   de configurações via Dashboard.        ║
    ╚══════════════════════════════════════════╝
    """)
    
    response = input("Deseja executar a migração? (s/n): ")
    if response.lower() == 's':
        migrate_database_v5()
    else:
        print("Cancelado.")