import secrets
from pathlib import Path

# ==============================================================================
# SCRIPT DE CORREÇÃO DE CHAVES (.env)
# ==============================================================================

def fix_env_file():
    env_path = Path('.env')
    
    # 1. Gera uma chave criptográfica forte
    new_secret = secrets.token_hex(32)
    
    # 2. Define o conteúdo padrão
    env_content = f"""# --- SEGURANÇA (GERADO AUTOMATICAMENTE) ---
FLASK_SECRET_KEY={new_secret}
LOG_LEVEL=INFO

# --- GOOGLE CLOUD (Obrigatório para o Robô) ---
# Cole sua chave aqui: https://console.cloud.google.com/apis/credentials
GOOGLE_API_KEY=
GOOGLE_PROJECT_ID=
GOOGLE_LOCATION=us-central1
YOUTUBE_API_KEY=

# --- WORDPRESS ---
WORDPRESS_URL=
WORDPRESS_USERNAME=
WORDPRESS_PASSWORD=

# --- PROVEDORES ---
NEWSAPI_KEY=
CURRENTS_API_KEY=
GNEWS_API_KEY=

# --- BANCO DE DADOS ---
DATABASE_URI=sqlite:///content_robot.db
"""

    # 3. Escreve o arquivo
    try:
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print(f"✅ [SUCESSO] Arquivo .env regenerado com nova chave de segurança.")
        print(f"🔑 Chave Flask Gerada: {new_secret[:8]}...")
        print("\n👇 AÇÃO NECESSÁRIA:")
        print("Abra o arquivo '.env' e cole sua GOOGLE_API_KEY na linha 6.")
        
    except Exception as e:
        print(f"❌ Erro ao escrever .env: {e}")

if __name__ == "__main__":
    fix_env_file()