# 📘 Guia de Configuração: Ecossistema Google

Para que o Content Robot v7.0 funcione com capacidade máxima, você precisa configurar um projeto no Google Cloud. Siga este passo a passo.

## 1. Criar Projeto no Google Cloud
1. Acesse o [Google Cloud Console](https://console.cloud.google.com/).
2. Clique no seletor de projetos (topo esquerdo) e depois em **"Novo Projeto"**.
3. Dê um nome (ex: `Content-Robot-V7`) e crie.
4. **Copie o "ID do projeto"** (ex: `content-robot-v7-48291`). Você usará isso no Dashboard.

## 2. Ativar APIs Necessárias
No menu lateral, vá em **APIs e Serviços > Biblioteca** e ative as seguintes APIs:

1.  **Vertex AI API** (Para geração de imagens).
2.  **YouTube Data API v3** (Para busca de vídeos).
3.  **Generative Language API** (Para o Gemini/Texto).

## 3. Criar Chaves de Acesso (API Keys)

### Para YouTube e Gemini:
1. Vá em **APIs e Serviços > Credenciais**.
2. Clique em **+ Criar Credenciais > Chave de API**.
3. Copie a chave gerada. Essa será sua `YouTube API Key` e `Gemini API Key` no Dashboard.

### Para Vertex AI (Autenticação Avançada):
*Se você estiver rodando localmente (sua máquina):*
1. Instale o [Google Cloud CLI](https://cloud.google.com/sdk/docs/install).
2. Abra o terminal e rode:
   ```bash
   gcloud auth application-default login
   ```
3. Faça login com sua conta Google. Isso cria as credenciais locais que o robô usará automaticamente.

## 4. Configurando no Dashboard
1. Abra o robô (`start_all.bat`) e acesse **http://localhost:5000**.
2. Vá na aba **Configurações**.
3. Preencha:
   * **Google Project ID:** O ID que você copiou no passo 1.
   * **Location:** Deixe como `us-central1` (recomendado).
   * **API Keys:** Cole as chaves geradas no passo 3.
4. Salve.

## 5. Configurando WordPress
1. No seu site WordPress, vá em **Usuários > Perfil**.
2. Role até **Application Passwords**.
3. Crie uma nova senha chamada "Robot".
4. Copie a senha gerada e cole no Dashboard do robô.