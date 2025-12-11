# Contexto do Projeto: S1M0N - Publisher Automation

## O que é este projeto?
O **S1M0N** (Content Robot v7.0) é uma plataforma de automação editorial projetada para criar, enriquecer e publicar conteúdo em sites WordPress de forma totalmente autônoma. Ele utiliza uma arquitetura moderna baseada em microsserviços e APIs do Google Cloud.

## Tecnologias Chave
- **Linguagem Principal**: Python 3.10+
- **Framework Web**: Flask (para o Dashboard)
- **IA Generativa**: Google Gemini 2.0 Flash (Texto), Vertex AI Imagen 3.0 (Imagens)
- **Dados Externos**: YouTube Data API v3, NewsAPI, GNews, Currents API, Feeds RSS
- **Persistência**: SQLite (via SQLAlchemy)

## Arquitetura e Fluxo de Dados
O sistema opera em "ciclos" (definidos no Dashboard):
1.  **Monitoramento**: Verifica feeds RSS e APIs de notícias por novidades.
2.  **Filtragem**: Seleciona apenas notícias relevantes e "safe for work".
3.  **Síntese (Brain)**: O `ContentEngine` usa o Gemini para reescrever a notícia, gerando um artigo original e otimizado para SEO.
4.  **Enriquecimento Multimídia**:
    - Gera imagens de destaque via Vertex AI.
    - Busca vídeos relacionados no YouTube para embedar.
5.  **Publicação**: Envia o artigo para o WordPress (como Rascunho ou Publicado, dependendo da config).

## Diretrizes para Desenvolvimento (Agentes)
- **Segurança**: Nunca exponha chaves de API nos logs. O Dashboard possui mecanismos de mascaramento.
- **Clean Architecture**: Mantenha a separação entre `providers` (acesso a dados) e `services` (lógica de negócio).
- **Estabilidade**: O sistema deve ser resiliente a falhas de API (rate limits, timeouts). Sempre use tratativa de erros e logs.
