"""
System Health Check - Content Robot v7.1
Diagnóstico automatizado de infraestrutura, conexões e permissões.
Execute antes do deploy ou quando houver erros.
"""
import os
import sys
import socket
import logging
import sqlite3
import requests
from datetime import datetime

# Configuração de Cores ANSI (Terminal)
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_status(step, message, status):
    symbol = "✅ PASS" if status else "❌ FAIL"
    color = Colors.OKGREEN if status else Colors.FAIL
    print(f"{Colors.BOLD}[{step}]{Colors.ENDC} {message.ljust(50)} {color}{symbol}{Colors.ENDC}")
    return status

def check_python_version():
    v = sys.version_info
    valid = v.major == 3 and v.minor >= 10
    return print_status("CORE", f"Python Version ({v.major}.{v.minor})", valid)

def check_structure():
    required_paths = [
        'src',
        'src/config',
        'src/services',
        'src/interface',
        'src/models',
        'src/providers',
        'requirements.txt',
        '.env'
    ]
    all_exist = True
    for path in required_paths:
        if not os.path.exists(path):
            print(f"   ↳ {Colors.FAIL}Missing: {path}{Colors.ENDC}")
            all_exist = False
    return print_status("FILES", "Integridade da Estrutura de Arquivos", all_exist)

def check_permissions():
    dirs = ['images', 'logs']
    all_ok = True
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        test_file = os.path.join(d, 'test_write.tmp')
        try:
            with open(test_file, 'w') as f:
                f.write('write_test')
            os.remove(test_file)
        except Exception:
            print(f"   ↳ {Colors.FAIL}Sem permissão de escrita em: {d}{Colors.ENDC}")
            all_ok = False
    return print_status("PERM", "Permissões de Escrita (Images/Logs)", all_ok)

def check_database():
    db_path = 'content_robot.db'
    if not os.path.exists(db_path):
        print(f"   ↳ {Colors.WARNING}Banco não encontrado. Será criado na primeira execução.{Colors.ENDC}")
        return print_status("DB", "Conexão SQLite", True) # Não é falha crítica, pois o setup cria
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [r[0] for r in cursor.fetchall()]
        required_tables = ['system_settings', 'rss_feeds', 'published_articles']
        missing = [t for t in required_tables if t not in tables]
        
        conn.close()
        
        if missing:
            print(f"   ↳ {Colors.FAIL}Tabelas faltando: {missing}{Colors.ENDC}")
            return print_status("DB", "Integridade do Schema", False)
            
        return print_status("DB", "Conexão e Schema SQLite", True)
    except Exception as e:
        print(f"   ↳ {e}")
        return print_status("DB", "Conexão SQLite", False)

def check_internet():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return print_status("NET", "Conectividade Externa", True)
    except OSError:
        return print_status("NET", "Conectividade Externa", False)

def check_api_keys():
    # Carrega .env manualmente para não depender do src.config neste teste isolado
    from dotenv import load_dotenv
    load_dotenv()
    
    keys = {
        'GOOGLE_API_KEY': os.getenv('GOOGLE_API_KEY'),
        'GOOGLE_PROJECT_ID': os.getenv('GOOGLE_PROJECT_ID'),
        'YOUTUBE_API_KEY': os.getenv('YOUTUBE_API_KEY'),
        'WORDPRESS_URL': os.getenv('WORDPRESS_URL')
    }
    
    missing = [k for k, v in keys.items() if not v or v == "sua_chave_aqui"]
    
    if missing:
        print(f"   ↳ {Colors.WARNING}Variáveis não configuradas no .env: {missing}{Colors.ENDC}")
        # Retorna Warning, não Fail, pois podem estar no Banco de Dados
        return print_status("ENV", "Variáveis de Ambiente (.env)", True) 
    
    return print_status("ENV", "Variáveis de Ambiente (.env)", True)

def run_diagnostics():
    print(f"\n{Colors.HEADER}🔍 INICIANDO DIAGNÓSTICO DO SISTEMA (v7.1){Colors.ENDC}")
    print("="*65)
    
    checks = [
        check_python_version(),
        check_structure(),
        check_permissions(),
        check_internet(),
        check_api_keys(),
        check_database()
    ]
    
    print("="*65)
    
    if all(checks):
        print(f"{Colors.OKGREEN}{Colors.BOLD}🎉 TUDO PRONTO! O SISTEMA ESTÁ SAUDÁVEL.{Colors.ENDC}")
        print(f"Execute {Colors.OKCYAN}start_all.bat{Colors.ENDC} para iniciar.")
        sys.exit(0)
    else:
        print(f"{Colors.FAIL}{Colors.BOLD}⚠️  FALHAS DETECTADAS.{Colors.ENDC}")
        print("Corrija os itens marcados com FAIL antes de iniciar.")
        sys.exit(1)

if __name__ == "__main__":
    run_diagnostics()