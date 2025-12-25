def _create_env_template(self):
    """
    Gera o arquivo .env com os novos provedores detectados na tree
    (NewsAPI, Currents) e chaves de segurança obrigatórias.
    """
    secret = self.generate_secret_key()

    content = f"""
# =======================================================
# CONTENT ROBOT v7.0 - CONFIGURAÇÃO DE AMBIENTE
# =======================================================
# IMPORTANTE: Renomeie este arquivo para .env e preencha os valores.
# NUNCA commite o arquivo .env real.

# --- SEGURANÇA DO SISTEMA (OBRIGATÓRIO) ---
# Chave usada para assinar cookies de sessão do Dashboard Flask
FLASK_SECRET_KEY={secret}
# Nível de Log: INFO, DEBUG, ERROR
LOG_LEVEL=INFO

# --- GOOGLE CLOUD (VERTEX AI / YOUTUBE) ---
GOOGLE_API_KEY=
GOOGLE_PROJECT_ID=
GOOGLE_LOCATION=us-central1
YOUTUBE_API_KEY=

# --- PROVEDORES DE NOTÍCIAS (DETECTADOS) ---
# Necessários para: src/providers/newsapi_provider.py
NEWSAPI_KEY=
# Necessários para: src/providers/currents_provider.py
CURRENTS_API_KEY=
# Necessários para: src/providers/gnews_provider.py
GNEWS_API_KEY=

# --- WORDPRESS (PUBLICAÇÃO) ---
WORDPRESS_URL=
WORDPRESS_USERNAME=
WORDPRESS_PASSWORD=

# --- BANCO DE DADOS ---
# Caminho absoluto ou relativo para o SQLite
DATABASE_URI=sqlite:///content_robot.db
"""

    # Escreve como .env se não existir, senão cria .env.example
    if not (self.base_path / '.env').exists():
        self.write_file('.env', content)
        print("⚠️  [NOTICE] Arquivo '.env' criado com SECRET seguro.")
    else:
        self.write_file('.env.example', content)
        print("ℹ️  [INFO] '.env' já existe. Template salvo como '.env.example'.")
