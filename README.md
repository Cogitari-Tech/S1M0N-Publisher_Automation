# 🤖 Content Robot v7.0 - Google Ecosystem Edition

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Google Cloud](https://img.shields.io/badge/Google-Vertex%20AI-4285F4)](https://cloud.google.com/vertex-ai)
[![Gemini](https://img.shields.io/badge/AI-Gemini%202.0-orange)](https://ai.google.dev/)
[![YouTube](https://img.shields.io/badge/API-YouTube%20Data-FF0000)](https://developers.google.com/youtube/v3)
[![Version](https://img.shields.io/badge/Version-7.0-blue)]()

**O Content Robot v7.0** é uma plataforma "Enterprise-Grade" de automação de conteúdo. Migrada para o ecossistema Google Cloud, ela unifica inteligência textual (Gemini), visual (Vertex AI/Imagen) e multimídia (YouTube) em uma arquitetura limpa e escalável.

---

## ⚡ Diferenciais da Versão 7.0

### ☁️ Google Ecosystem Native
- **Imagens via Vertex AI (Imagen 3.0):** Geração de imagens fotorrealistas de nível comercial, substituindo soluções instáveis.
- **YouTube Data API v3:** Busca nativa de vídeos contextuais para aumentar o tempo de permanência no blog.
- **Gemini 2.0 Flash:** Motor de reescrita ultra-rápido e econômico.

### 🌲 Modo Evergreen (On-Demand)
- **Gerador de Guias:** Digite um tema (ex: *"O Futuro da Energia Solar"*) e o sistema pesquisa, estrutura e escreve um artigo "Cornerstone" completo (>1500 palavras) com imagens e vídeos, sem depender de notícias.

### 🛡️ Segurança & Compliance
- **Clean Architecture:** Código modular (`src/providers`, `src/services`) facilitando manutenção.
- **Trava de Segurança:** Limite rígido de posts por ciclo para evitar detecção de spam.
- **SEO Deep-Level:** Injeção direta de metadados nos campos ocultos do **Yoast** e **RankMath**.

---

## 🚀 Instalação Rápida

### Pré-requisitos
- Python 3.10+
- Conta no Google Cloud Platform (GCP)

### 1. Setup Inicial
```bash
# Clone e entre na pasta
git clone [https://github.com/seu-usuario/content-robot.git](https://github.com/seu-usuario/content-robot.git)
cd content-robot

# Instale dependências
pip install -r requirements.txt

# Inicialize o Banco de Dados
python -c "from src.config.database import init_db; init_db()"
```

### 2. Execução
Utilize o launcher para iniciar Engine, Dashboard e Sistema de Aprovação:

```bash
# Windows
start_all.bat

# Linux/Mac
python main.py & python dashboard_launcher.py & python approval_system.py
```

### 3. Acesso
- **Dashboard de Gestão:** http://localhost:5000
- **Sistema de Aprovação:** http://localhost:5001

---

## ⚙️ Configuração (Sem Código)

Não edite arquivos `.env`. Toda a configuração é feita via Dashboard:
1. Acesse a aba **Configurações**.
2. Insira suas credenciais do Google Cloud e WordPress.
3. Clique em Salvar. O sistema fará o "Hot-Reload" no próximo ciclo.

---

## 🧩 Estrutura de Arquivos (Clean Arch)

```
content-robot/
├── main.py               # Entry Point do Motor
├── dashboard_launcher.py # Entry Point da Interface
├── src/
│   ├── config/           # Settings e Database
│   ├── interface/        # Flask App e UI
│   ├── models/           # Schema SQLAlchemy
│   ├── providers/        # Conectores (RSS, GNews)
│   └── services/         # Lógica de Negócio (AI, Video, Engine)
└── content_robot.db      # Banco de Dados (Ignorado no Git)
```

---

## 📜 Licença
MIT License.