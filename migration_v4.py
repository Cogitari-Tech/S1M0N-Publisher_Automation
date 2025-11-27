"""
Migração do Banco de Dados v3.x -> v4.0
Adiciona tabelas de cache e novos campos
"""
import sqlite3
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_database():
    """Executa migração completa"""
    try:
        conn = sqlite3.connect('content_robot.db')
        cursor = conn.cursor()
        
        logger.info("🔄 Iniciando migração v3.x -> v4.0...")
        
        # ==========================================
        # 1. ADICIONAR COLUNAS EM pending_articles
        # ==========================================
        try:
            cursor.execute('''
                ALTER TABLE pending_articles 
                ADD COLUMN youtube_url VARCHAR(500)
            ''')
            logger.info("✅ Coluna youtube_url adicionada")
        except sqlite3.OperationalError:
            logger.info("⚠️  Coluna youtube_url já existe")
        
        try:
            cursor.execute('''
                ALTER TABLE pending_articles 
                ADD COLUMN image_path VARCHAR(500)
            ''')
            logger.info("✅ Coluna image_path adicionada")
        except sqlite3.OperationalError:
            logger.info("⚠️  Coluna image_path já existe")
        
        # ==========================================
        # 2. CRIAR TABELAS DE CACHE
        # ==========================================
        
        # Cached Content
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cached_content (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_hash VARCHAR(64) UNIQUE NOT NULL,
                input_title VARCHAR(500),
                input_content_snippet TEXT,
                cached_result TEXT,
                ai_provider VARCHAR(50),
                prompt_id VARCHAR(100),
                hit_count INTEGER DEFAULT 0,
                last_hit TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                is_valid BOOLEAN DEFAULT 1
            )
        ''')
        logger.info("✅ Tabela cached_content criada")
        
        # YouTube Cache
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS youtube_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_hash VARCHAR(64) UNIQUE NOT NULL,
                query_text VARCHAR(500),
                video_url VARCHAR(500),
                video_title VARCHAR(500),
                hit_count INTEGER DEFAULT 0,
                last_hit TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP
            )
        ''')
        logger.info("✅ Tabela youtube_cache criada")
        
        # Image Cache
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS image_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prompt_hash VARCHAR(64) UNIQUE NOT NULL,
                prompt_text VARCHAR(1000),
                image_path VARCHAR(500),
                hit_count INTEGER DEFAULT 0,
                last_hit TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP
            )
        ''')
        logger.info("✅ Tabela image_cache criada")
        
        # ==========================================
        # 3. CRIAR ÍNDICES PARA PERFORMANCE
        # ==========================================
        
        # Índices de cache
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_cached_content_hash 
            ON cached_content(content_hash)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_youtube_query_hash 
            ON youtube_cache(query_hash)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_image_prompt_hash 
            ON image_cache(prompt_hash)
        ''')
        
        # Índices existentes melhorados
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_published_date 
            ON published_articles(published_date)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_pending_status 
            ON pending_articles(status, created_at)
        ''')
        
        logger.info("✅ Índices criados")
        
        # ==========================================
        # 4. OTIMIZAR BANCO
        # ==========================================
        cursor.execute('VACUUM')
        cursor.execute('ANALYZE')
        
        conn.commit()
        conn.close()
        
        logger.info("✅ Migração concluída com sucesso!")
        logger.info("\n" + "="*50)
        logger.info("PRÓXIMOS PASSOS:")
        logger.info("1. Adicione YOUTUBE_API_KEY no .env")
        logger.info("2. Reinicie content_robot.py")
        logger.info("3. Reinicie approval_system.py")
        logger.info("4. Acesse dashboard em http://localhost:5000")
        logger.info("="*50 + "\n")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro na migração: {e}")
        return False

def verify_migration():
    """Verifica se migração foi bem-sucedida"""
    try:
        conn = sqlite3.connect('content_robot.db')
        cursor = conn.cursor()
        
        logger.info("\n🔍 Verificando migração...\n")
        
        # Verifica tabelas
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' 
            ORDER BY name
        """)
        
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = [
            'cached_content',
            'youtube_cache',
            'image_cache',
            'published_articles',
            'pending_articles',
            'api_usage_logs',
            'rate_limit_logs'
        ]
        
        for table in expected_tables:
            if table in tables:
                logger.info(f"✅ Tabela '{table}' OK")
            else:
                logger.error(f"❌ Tabela '{table}' FALTANDO!")
        
        # Verifica colunas de pending_articles
        cursor.execute("PRAGMA table_info(pending_articles)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'youtube_url' in columns:
            logger.info("✅ Coluna 'youtube_url' OK")
        else:
            logger.error("❌ Coluna 'youtube_url' FALTANDO!")
        
        if 'image_path' in columns:
            logger.info("✅ Coluna 'image_path' OK")
        else:
            logger.error("❌ Coluna 'image_path' FALTANDO!")
        
        conn.close()
        
        logger.info("\n✅ Verificação concluída!\n")
        
    except Exception as e:
        logger.error(f"❌ Erro na verificação: {e}")

if __name__ == '__main__':
    import sys
    
    print("""
    ╔══════════════════════════════════════════╗
    ║   🔄 MIGRAÇÃO v3.x → v4.0                ║
    ║                                          ║
    ║   ⚠️  FAÇA BACKUP DO BANCO ANTES!       ║
    ║                                          ║
    ║   Comandos:                              ║
    ║   - migrate  : Executar migração         ║
    ║   - verify   : Verificar migração        ║
    ╚══════════════════════════════════════════╝
    """)
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'migrate':
            # Backup automático
            import shutil
            from datetime import datetime
            
            backup_name = f"content_robot_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            
            try:
                shutil.copy2('content_robot.db', backup_name)
                logger.info(f"💾 Backup criado: {backup_name}")
            except:
                logger.warning("⚠️  Não foi possível criar backup")
            
            # Executar migração
            success = migrate_database()
            
            if success:
                verify_migration()
        
        elif command == 'verify':
            verify_migration()
        
        else:
            print(f"❌ Comando desconhecido: {command}")
            print("   Use: migrate ou verify")
    
    else:
        print("❌ Especifique um comando: migrate ou verify")