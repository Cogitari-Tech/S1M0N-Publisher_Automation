# 🤖 Content Robot v5.0 - Mini-SaaS Edition

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Gemini](https://img.shields.io/badge/AI-Gemini%202.0-orange)](https://ai.google.dev/)
[![WordPress](https://img.shields.io/badge/CMS-WordPress-21759B)](https://wordpress.org/)
[![Version](https://img.shields.io/badge/Version-5.0-purple)]()

**O Content Robot v5.0** é uma plataforma completa de automação de conteúdo "Set-and-Forget". Evoluindo de um script simples, ele opera agora como um **Mini-SaaS**, permitindo a gestão de credenciais, limites de segurança e prompts diretamente via Dashboard Web, eliminando a necessidade de editar código ou arquivos de configuração manual.

---

## 🔥 Novidades da Versão 5.0

### ⚙️ Painel de Controle Dinâmico
- **Banco de Configurações:** As credenciais (WP, Gemini, YouTube) agora residem no banco de dados SQLite criptografado, não mais em arquivos `.env` estáticos.
- **Gestão em Tempo Real:** Altere prompts de imagem, senhas e chaves de API instantaneamente via interface web.

### 🛡️ Segurança & Anti-Ban
- **Hard Limit (Trava de Segurança):** Define um limite máximo de artigos por ciclo (ex: 5 posts) para evitar detecção de spam ou bloqueios de API.
- **Rate Limiting Inteligente:** Delays aleatórios entre requisições para simular comportamento humano.

### 🎯 SEO Deep-Level (WordPress)
- **RankMath & Yoast Nativo:** O robô injeta metadados diretamente nos campos ocultos dos plugins (`_yoast_wpseo_metadesc`, `rank_math_focus_keyword`), garantindo pontuação máxima de SEO.

### ⚡ Cache Híbrido
- **Economia de Recursos:** Cache inteligente para conteúdo gerado, buscas do YouTube e imagens, reduzindo custos de API e tempo de processamento.

---

## 🚀 Instalação e Upgrade

### 1. Pré-requisitos
- Python 3.10 ou superior
- Git

### 2. Instalação Limpa
```bash
git clone [https://github.com/seu-usuario/content-robot.git](https://github.com/seu-usuario/content-robot.git)
cd content-robot
pip install -r requirements.txt

# Executa a migração para criar o banco e tabelas de configuração
python migration_v5.py
```

### 3. Upgrade da v4.0
Se você já possui o banco de dados da versão anterior:
```bash
# O script detectará o banco existente e criará a tabela SystemSettings
# Importará automaticamente suas variáveis do antigo .env se disponível
python migration_v5.py
```

---

## 🕹️ Como Usar

### 1. Iniciar o Sistema
Utilize o script orquestrador para iniciar todos os serviços (Engine, Dashboard e Aprovação) simultaneamente:

```bash
start_all.bat
```

Isso abrirá três janelas de terminal e disponibilizará:
* **Dashboard de Gestão:** http://localhost:5000
* **Sistema de Aprovação:** http://localhost:5001
* **Engine (Background):** Monitora feeds e processa conteúdo.

### 2. Configuração (Fluxo Novo)
**Não edite arquivos `.py` ou `.env` para ajustes operacionais.**

1.  Acesse o **Dashboard** (Porta 5000).
2.  Vá para a aba **⚙️ Configurações**.
3.  Preencha/Atualize:
    * **WordPress:** URL, Usuário e Application Password.
    * **APIs:** Insira as chaves do Gemini, YouTube e Stability AI.
    * **Operacional:** Defina o "Limite de Artigos por Ciclo" (Recomendado: 5).
4.  Clique em **Salvar**. O robô aplicará as mudanças no próximo ciclo agendado.

### 3. Workflows de Conteúdo

#### 📰 Fluxo de Notícias (Automático)
O robô monitora os Feeds RSS configurados.
1.  **Monitoramento:** A cada ciclo (ex: 120 min), busca novidades.
2.  **Filtragem:** Verifica duplicatas no banco de dados.
3.  **Processamento:**
    * Reescreve o texto com IA (Gemini).
    * Gera imagem editorial (Stability AI).
    * Busca vídeo relacionado (YouTube).
4.  **Publicação:** Envia para o WordPress (Direto ou via Aprovação).

#### 🌲 Fluxo Evergreen (Configurável)
Para gerar conteúdo atemporal:
1.  Acesse **Configurações** no Dashboard.
2.  Altere o **Prompt de Estilo** para focar em artigos educativos ou listas (ex: "Crie um guia completo sobre...").
3.  O sistema aplicará este novo estilo aos tópicos capturados, transformando notícias passageiras em guias evergreen.

---

## 🧩 Estrutura do Projeto

```
content-robot/
├── content_robot.py      # Engine Principal (Lógica de Segurança e SEO v5.0)
├── dashboard.py          # Dashboard Web & API de Settings
├── approval_system.py    # Interface de Revisão Humana
├── database_models.py    # Schema do Banco (inclui tabela SystemSettings)
├── migration_v5.py       # Script de Migração de Banco e Seed
├── cache_manager.py      # Gestão de Cache (YouTube/Conteúdo/Imagens)
├── system_optimizer.py   # Rotinas de Limpeza e Manutenção
├── start_all.bat         # Launcher Windows
├── requirements.txt      # Dependências Python
└── content_robot.db      # Banco de Dados SQLite (NÃO COMMITAR)
```

---

## ⚠️ Segurança e Dados

* **Credenciais no Banco:** O arquivo `content_robot.db` agora contém suas chaves de API e senhas. Certifique-se de que ele esteja listado no `.gitignore`.
* **Logs:** O arquivo `robot.log` é gerado localmente para auditoria de erros e performance.

---

## 📜 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.