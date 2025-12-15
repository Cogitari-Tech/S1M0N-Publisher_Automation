import os
import secrets
from pathlib import Path

# ==============================================================================
# CONFIGURAÇÃO DE AMBIENTE - CONTENT ROBOT v7.0
# ==============================================================================
# Este script gera os arquivos de configuração seguindo as práticas de
# Clean Code e Segurança (OWASP).
#
# EXECUÇÃO: python setup_environment.py
# ==============================================================================

class ConfigurationManager:
    def __init__(self, base_path: Path):
        self.base_path = base_path
    
    def write_file(self, filename: str, content: str) -> None:
        """Escreve o conteúdo no arquivo especificado com codificação UTF-8."""
        file_path = self.base_path / filename
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content.strip())
            print(f"✅ [SUCCESS] {filename} atualizado com sucesso.")
        except IOError as e:
            print(f"❌ [ERROR] Falha ao escrever {filename}: {e}")

    def generate_secret_key(self) -> str:
        """Gera uma chave criptográfica forte para sessões Flask."""
        return secrets.token_hex(32)

    def setup(self):
        print("Iniciando configuração segura do ambiente...")
        self._create_gitignore()
        self._create_env_template()
        print("Configuração concluída.")

    def _create_gitignore(self):
        """
        Gera um .gitignore robusto baseado na estrutura do projeto e 
        nos requisitos de segurança[cite: 14, 15].
        """
        content = """
# =======================================================
# .gitignore - Content Robot v7.0 (SECURITY ENFORCED)
# =======================================================

# 1. SEGREDOS E AMBIENTE (CRÍTICO)
# Bloqueia qualquer arquivo que possa conter credenciais [cite: 2, 6]
.env
.env.*
!.env.example
secrets/
tokens/

# 2. BANCO DE DADOS
# Nunca commitar bancos SQLite de produção 
*.db
*.sqlite
*.sqlite3
instance/
data/

# 3. DEPENDÊNCIAS PYTHON
__pycache__/
*.py[cod]
*$py.class
venv/
env/
.venv/
.pytest_cache/
.coverage
htmlcov/

# 4. LOGS E ARTEFATOS DE EXECUÇÃO
# Evita vazamento de stack traces em logs commitados [cite: 3, 4]
*.log
logs/
debug_*.txt

# 5. CONTEÚDO GERADO (RUNTIME)
images/
backups/
exports/
temp/

# 6. IDE / SISTEMA
.vscode/
.idea/
.DS_Store
"""
        self.write_file('.gitignore', content)

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
        # Escreve como .env se não existir, senão atualiza .env.example para não sobrescrever segredos
        if not (self.base_path / '.env').exists():
            self.write_file('.env', content)
            print("⚠️  [NOTICE] Arquivo '.env' criado. PREENCHA AS CHAVES IMEDIATAMENTE.")
        else:
            self.write_file('.env.example', content)
            print("ℹ️  [INFO] '.env' já existe. Novo template salvo como '.env.example'.")

if __name__ == "__main__":
    # Executa a configuração no diretório atual
    manager = ConfigurationManager(Path.cwd())
    manager.setup()