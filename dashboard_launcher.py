import sys
import os
import logging


sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.interface.dashboard_app import app
from src.config.database import init_db


werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.setLevel(logging.ERROR)


DEBUG_MODE = os.environ.get("FLASK_DEBUG", "0").strip().lower() in ("1", "true", "yes")

if __name__ == "__main__":
    print("🔄 Inicializando Banco de Dados...")
    init_db()

    print("📊 Dashboard v7.1 ONLINE")
    print("👉 Acesso: http://localhost:5000")


    app.run(
        host="0.0.0.0",
        port=5000,
        debug=DEBUG_MODE,
        use_reloader=False
    )
