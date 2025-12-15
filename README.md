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
start_all.bat

# Linux/Mac
python main.py & python dashboard_launcher.py
```

### 3. Acesso
- **Dashboard de Gestão:** http://localhost:5000

---

## 📖 Guia de Funcionalidades (v8.3)

### 1. Histórico & Chat
O sistema armazena todas as gerações no banco de dados.
- Na aba **Evergreen**, clique em qualquer linha do histórico para abrir o **Modo Chat**.
- Visualize as mensagens exatas enviadas (User) e recebidas (Assistant).
- Status "COMPLETED" indica que o artigo foi finalizado com sucesso.

### 2. Seletor de Modelo AI
Em **Configurações > Google Ecosystem**, escolha o motor ideal:
- **Gemini Pro (Melhor para Raciocínio Complexo)**: Use para artigos longos, analíticos ou que exigem alta criatividade.
- **Gemini Flash (Alta Velocidade)**: Use para notícias rápidas ou quando a velocidade de resposta for crítica (ex: testes).

### 3. Controle de Performance (NOVO v8.3)
No menu **Configurações > Painel de Controle**:
- **Frequência de Atualização**: Slider preciso para definir o intervalo de gerações (5 min até 4 horas).
- **Otimização de Sistema**: Botão "Otimizar Sistema" que executa limpeza profunda de RAM (`gc.collect`) e compactação de banco de dados (`VACUUM`) para manter o Dashboard leve.

### 4. Indicador de Ambiente
O Dashboard exibe um badge no topo:
- **VERDE (DEV)**: Ambiente de desenvolvimento. Seguro para testar.
- **VERMELHO (PROD)**: Ambiente de produção. Ações de escrita (POST/DELETE) devem ser feitas com cautela.

---

## 🛠️ Deployment e Variáveis de Ambiente

Para deploy em produção (ex: Cloud Run, Heroku, VPS), configure as variáveis de ambiente. O `DeploymentService` validará estas chaves antes do build.

| Variável | Descrição | Obrigatório |
| :--- | :--- | :--- |
| `FLASK_ENV` | Define o ambiente (`DEV` ou `PROD`). | Sim |
| `GOOGLE_API_KEY` | Chave Mestre do Gemini. | Sim |
| `GOOGLE_PROJECT_ID` | Project ID do GCP para Vertex AI. | Sim |
| `YOUTUBE_API_KEY` | Para busca de vídeos relacionados. | Não (Recomendado) |
| `WORDPRESS_URL` | URL do blog de destino. | Sim |
| `WORDPRESS_USERNAME` | Usuário de publicação. | Sim |
| `WORDPRESS_PASSWORD` | Application Password (não a senha de login). | Sim |

> **Nota**: Tokens de API de Notícias (GNews, NewsAPI) são opcionais e podem ser ativados via Dashboard.

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