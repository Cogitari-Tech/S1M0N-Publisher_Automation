"""
Sistema de Otimização e Limpeza - Content Robot v4.0
Mantém o sistema rápido e eficiente
"""
import os
import shutil
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any
from sqlalchemy import create_engine, func, text
from sqlalchemy.orm import sessionmaker
from database_models import PublishedArticle, APIUsageLog, RateLimitLog, Base
import psutil

logger = logging.getLogger(__name__)

class SystemOptimizer:
    """Otimizador do sistema"""
    
    def __init__(self):
        engine = create_engine('sqlite:///content_robot.db', echo=False)
        Session = sessionmaker(bind=engine)
        self.session = Session()
        
        logger.info("✅ System Optimizer inicializado")
    
    # ==========================================
    # LIMPEZA DE BANCO DE DADOS
    # ==========================================
    def clean_old_articles(self, days: int = 90) -> int:
        """Remove artigos muito antigos do banco"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            old_articles = self.session.query(PublishedArticle).filter(
                PublishedArticle.published_date < cutoff_date
            ).all()
            
            count = len(old_articles)
            
            for article in old_articles:
                self.session.delete(article)
            
            self.session.commit()
            
            logger.info(f"🗑️ {count} artigos antigos removidos (>{days} dias)")
            return count
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"❌ Erro ao limpar artigos: {e}")
            return 0
    
    def clean_old_logs(self, days: int = 30) -> int:
        """Remove logs antigos de API"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            old_logs = self.session.query(APIUsageLog).filter(
                APIUsageLog.date < cutoff_date
            ).all()
            
            count = len(old_logs)
            
            for log in old_logs:
                self.session.delete(log)
            
            self.session.commit()
            
            logger.info(f"🗑️ {count} logs de API removidos (>{days} dias)")
            return count
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"❌ Erro ao limpar logs: {e}")
            return 0
    
    def vacuum_database(self) -> bool:
        """Compacta o banco SQLite"""
        try:
            self.session.execute(text('VACUUM'))
            self.session.commit()
            
            logger.info("🗜️ Banco de dados compactado")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao compactar banco: {e}")
            return False
    
    # ==========================================
    # LIMPEZA DE ARQUIVOS
    # ==========================================
    def clean_old_images(self, days: int = 30) -> Dict[str, Any]:
        """Remove imagens antigas não utilizadas"""
        try:
            result = {'deleted': 0, 'freed_mb': 0}
            images_dir = Path('images')
            
            if not images_dir.exists():
                return result
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
            for image_file in images_dir.glob('*.png'):
                file_time = datetime.fromtimestamp(image_file.stat().st_mtime)
                
                if file_time < cutoff_date:
                    file_size = image_file.stat().st_size
                    image_file.unlink()
                    
                    result['deleted'] += 1
                    result['freed_mb'] += file_size / 1024 / 1024
            
            result['freed_mb'] = round(result['freed_mb'], 2)
            
            logger.info(f"🗑️ {result['deleted']} imagens removidas ({result['freed_mb']} MB)")
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro ao limpar imagens: {e}")
            return {'deleted': 0, 'freed_mb': 0}
    
    def clean_old_logs_files(self, days: int = 30) -> Dict[str, Any]:
        """Remove arquivos de log antigos"""
        try:
            result = {'deleted': 0, 'freed_mb': 0}
            
            # robot.log.1, robot.log.2, etc.
            for i in range(1, 10):
                log_file = Path(f'robot.log.{i}')
                
                if log_file.exists():
                    file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                    cutoff_date = datetime.now() - timedelta(days=days)
                    
                    if file_time < cutoff_date:
                        file_size = log_file.stat().st_size
                        log_file.unlink()
                        
                        result['deleted'] += 1
                        result['freed_mb'] += file_size / 1024 / 1024
            
            result['freed_mb'] = round(result['freed_mb'], 2)
            
            if result['deleted'] > 0:
                logger.info(f"🗑️ {result['deleted']} arquivos de log removidos ({result['freed_mb']} MB)")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro ao limpar logs: {e}")
            return {'deleted': 0, 'freed_mb': 0}
    
    def clean_debug_files(self) -> int:
        """Remove arquivos debug_gemini_*.txt"""
        try:
            count = 0
            
            for debug_file in Path('.').glob('debug_gemini_*.txt'):
                debug_file.unlink()
                count += 1
            
            if count > 0:
                logger.info(f"🗑️ {count} arquivos de debug removidos")
            
            return count
            
        except Exception as e:
            logger.error(f"❌ Erro ao limpar debug: {e}")
            return 0
    
    # ==========================================
    # OTIMIZAÇÃO DE ÍNDICES
    # ==========================================
    def optimize_database_indexes(self) -> bool:
        """Otimiza índices do banco"""
        try:
            # Reindexar
            self.session.execute(text('REINDEX'))
            
            # Analisar tabelas
            self.session.execute(text('ANALYZE'))
            
            self.session.commit()
            
            logger.info("📊 Índices otimizados")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao otimizar índices: {e}")
            return False
    
    # ==========================================
    # ESTATÍSTICAS DO SISTEMA
    # ==========================================
    def get_system_health(self) -> Dict[str, Any]:
        """Retorna saúde do sistema"""
        try:
            db_size = os.path.getsize('content_robot.db') / 1024 / 1024
            
            images_dir = Path('images')
            images_size = 0
            images_count = 0
            
            if images_dir.exists():
                for img in images_dir.glob('*.png'):
                    images_size += img.stat().st_size
                    images_count += 1
            
            images_size_mb = images_size / 1024 / 1024
            
            # Log file size
            log_size = 0
            if os.path.exists('robot.log'):
                log_size = os.path.getsize('robot.log') / 1024 / 1024
            
            # Total articles
            total_articles = self.session.query(PublishedArticle).count()
            
            # System resources
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('.')
            
            return {
                'database_size_mb': round(db_size, 2),
                'images_count': images_count,
                'images_size_mb': round(images_size_mb, 2),
                'log_size_mb': round(log_size, 2),
                'total_articles': total_articles,
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'disk_percent': disk.percent,
                'disk_free_gb': round(disk.free / 1024 / 1024 / 1024, 2)
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter saúde: {e}")
            return {}
    
    def get_optimization_recommendations(self) -> list:
        """Retorna recomendações de otimização"""
        recommendations = []
        
        try:
            health = self.get_system_health()
            
            # Banco muito grande
            if health.get('database_size_mb', 0) > 500:
                recommendations.append({
                    'severity': 'warning',
                    'message': 'Banco de dados > 500MB. Execute limpeza de artigos antigos.',
                    'action': 'clean_old_articles'
                })
            
            # Muitas imagens
            if health.get('images_count', 0) > 1000:
                recommendations.append({
                    'severity': 'warning',
                    'message': f"{health['images_count']} imagens armazenadas. Considere limpeza.",
                    'action': 'clean_old_images'
                })
            
            # Log muito grande
            if health.get('log_size_mb', 0) > 100:
                recommendations.append({
                    'severity': 'info',
                    'message': 'Arquivo de log > 100MB. Execute limpeza.',
                    'action': 'clean_old_logs_files'
                })
            
            # CPU alta
            if health.get('cpu_percent', 0) > 80:
                recommendations.append({
                    'severity': 'critical',
                    'message': 'CPU acima de 80%. Verifique processos em execução.',
                    'action': 'check_processes'
                })
            
            # Memória alta
            if health.get('memory_percent', 0) > 85:
                recommendations.append({
                    'severity': 'critical',
                    'message': 'Memória acima de 85%. Reinicie o sistema.',
                    'action': 'restart_system'
                })
            
            # Disco cheio
            if health.get('disk_percent', 0) > 90:
                recommendations.append({
                    'severity': 'critical',
                    'message': 'Disco acima de 90%. Libere espaço urgentemente!',
                    'action': 'free_disk_space'
                })
            
            if not recommendations:
                recommendations.append({
                    'severity': 'success',
                    'message': '✅ Sistema operando normalmente',
                    'action': None
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar recomendações: {e}")
            return []
    
    # ==========================================
    # OPERAÇÃO COMPLETA DE LIMPEZA
    # ==========================================
    def full_cleanup(self, aggressive: bool = False) -> Dict[str, Any]:
        """
        Executa limpeza completa do sistema
        
        Args:
            aggressive: Se True, remove mais dados (cuidado!)
        """
        result = {
            'articles_deleted': 0,
            'logs_deleted': 0,
            'images_deleted': 0,
            'debug_files_deleted': 0,
            'freed_mb': 0,
            'vacuum_success': False,
            'optimize_success': False
        }
        
        try:
            logger.info("🧹 Iniciando limpeza completa do sistema...")
            
            # 1. Limpar artigos antigos
            days_articles = 30 if aggressive else 90
            result['articles_deleted'] = self.clean_old_articles(days_articles)
            
            # 2. Limpar logs de API
            days_logs = 7 if aggressive else 30
            result['logs_deleted'] = self.clean_old_logs(days_logs)
            
            # 3. Limpar imagens
            days_images = 15 if aggressive else 30
            img_result = self.clean_old_images(days_images)
            result['images_deleted'] = img_result['deleted']
            result['freed_mb'] += img_result['freed_mb']
            
            # 4. Limpar arquivos de log
            log_result = self.clean_old_logs_files(days_logs)
            result['freed_mb'] += log_result['freed_mb']
            
            # 5. Limpar debug files
            result['debug_files_deleted'] = self.clean_debug_files()
            
            # 6. Compactar banco
            result['vacuum_success'] = self.vacuum_database()
            
            # 7. Otimizar índices
            result['optimize_success'] = self.optimize_database_indexes()
            
            logger.info(f"✅ Limpeza concluída! {result['freed_mb']:.2f} MB liberados")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro na limpeza completa: {e}")
            return result


# ==========================================
# TESTES E CLI
# ==========================================
if __name__ == '__main__':
    import sys
    
    optimizer = SystemOptimizer()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'health':
            print("\n🏥 SAÚDE DO SISTEMA\n")
            health = optimizer.get_system_health()
            for key, value in health.items():
                print(f"   {key}: {value}")
        
        elif command == 'recommendations':
            print("\n💡 RECOMENDAÇÕES DE OTIMIZAÇÃO\n")
            recs = optimizer.get_optimization_recommendations()
            for rec in recs:
                icon = {'critical': '🔴', 'warning': '⚠️', 'info': 'ℹ️', 'success': '✅'}
                print(f"   {icon.get(rec['severity'], '•')} {rec['message']}")
        
        elif command == 'cleanup':
            aggressive = '--aggressive' in sys.argv
            print(f"\n🧹 LIMPEZA {'AGRESSIVA' if aggressive else 'NORMAL'}\n")
            result = optimizer.full_cleanup(aggressive)
            
            print(f"   Artigos removidos: {result['articles_deleted']}")
            print(f"   Logs removidos: {result['logs_deleted']}")
            print(f"   Imagens removidas: {result['images_deleted']}")
            print(f"   Debug files: {result['debug_files_deleted']}")
            print(f"   Espaço liberado: {result['freed_mb']:.2f} MB")
            print(f"   Vacuum: {'✅' if result['vacuum_success'] else '❌'}")
            print(f"   Otimização: {'✅' if result['optimize_success'] else '❌'}")
        
        else:
            print(f"❌ Comando desconhecido: {command}")
    
    else:
        print("""
        🛠️  SYSTEM OPTIMIZER v4.0
        
        Uso: python system_optimizer.py [comando]
        
        Comandos:
          health           - Mostra saúde do sistema
          recommendations  - Mostra recomendações
          cleanup          - Executa limpeza normal
          cleanup --aggressive - Limpeza agressiva (cuidado!)
        """)