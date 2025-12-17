import sys
import os
import logging

# Adiciona o diretório atual ao PATH do Python para garantir que 'src' seja encontrado
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.interface.dashboard_app import app
from src.config.database import init_db

# Configura log apenas para erro no dashboard para manter o console limpo
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

if __name__ == "__main__":
    print("🔄 Inicializando Banco de Dados...")
    init_db()
    print("📊 Dashboard v7.1 ONLINE")
    print("👉 Acesso: http://localhost:5000")
    
    # O use_reloader=False evita que o script rode duas vezes ao iniciar
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)