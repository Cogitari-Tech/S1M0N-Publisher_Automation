# 🚀 Guia Operacional: Content Robot v5.0 (Quick Start)

Este guia cobre a configuração técnica essencial para colocar o sistema em produção.

## 1. Configuração do WordPress (Crucial)

Antes de rodar o código, prepare seu WordPress para aceitar conexões via API REST.

* **Gerar Senha de Aplicativo (Application Password):**
    1.  Acesse o painel administrativo: **Usuários > Seu Perfil** (ou Perfil).
    2.  Role até o final da página na seção **"Application Passwords"**. Digite um nome (ex: `ContentRobot`), clique em **Add New** e **copie a senha gerada** (sem espaços). *Nunca use sua senha de login normal.*

* **Descobrir IDs de Categorias e Tags:**
    1.  Vá em **Posts > Categorias** (ou Tags).
    2.  Passe o mouse sobre o botão **"Editar"** da categoria desejada.
    3.  Olhe para a URL no rodapé do navegador. O número após `tag_ID=` ou `ID=` é o ID numérico (ex: `...&tag_ID=15&...` -> ID **15**).

## 2. Configuração de Ambiente (.env)

Crie um arquivo chamado `.env` na raiz do projeto e preencha as variáveis abaixo.
*Nota: Na v5.0, estes valores serão importados automaticamente para o Banco de Dados na primeira execução.*

```ini
# --- CORE (Obrigatório) ---
# Chave da IA Generativa (Google Gemini)
GOOGLE_API_KEY=sua_chave_aqui

# Credenciais do WordPress
WORDPRESS_URL=[https://seusite.com](https://seusite.com)
WORDPRESS_USERNAME=seu_usuario_admin
WORDPRESS_PASSWORD=xxxx xxxx xxxx xxxx  # Use a Application Password gerada acima

# --- OPCIONAIS (Recomendado) ---
# Para buscar vídeos relacionados e enriquecer o post
YOUTUBE_API_KEY=sua_chave_youtube_data_v3

# Para gerar imagens exclusivas com IA
STABILITY_API_KEY=sua_chave_stability_ai

# Notificações de Status
NOTIFICATION_WEBHOOK_URL=url_do_seu_webhook_discord
```

## 3. Execução e Deploy

Abra o terminal na pasta do projeto e execute os comandos na ordem:

**A. Configurar Ambiente Virtual (Python)**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

**B. Instalar Dependências**
```bash
pip install -r requirements.txt
```

**C. Inicializar Banco de Dados (Migração v5.0)**
*Este passo cria o banco SQLite e importa suas configurações do .env.*
```bash
python migration_v5.py
```

**D. Rodar a Automação**
Para iniciar todos os serviços (Engine + Dashboard + Aprovação):
```bash
# Windows
start_all.bat

# Linux/Mac (ou execução manual em terminais separados)
python content_robot.py
python dashboard.py
python approval_system.py
```

**E. Acesso ao Sistema**
* **Dashboard de Gestão:** http://localhost:5000
* **Interface de Aprovação:** http://localhost:5001