# 📖 Manual do Usuário: Content Robot v7.0

## Visão Geral do Dashboard

### 1. Monitoramento (Home)
A tela inicial mostra a saúde do sistema.
* **Cache IA:** Quantas vezes o robô economizou dinheiro reutilizando um texto/imagem já gerado.
* **Logs:** Mostra o que o robô está fazendo agora (em tempo real).

### 2. Gerenciando Fontes (RSS)
O robô precisa de fontes para trabalhar no "Modo Notícias".
1. Vá na aba **Fontes RSS**.
2. Clique em **+ Adicionar Feed**.
3. Insira o Nome (ex: `G1 Tecnologia`) e a URL do RSS (ex: `https://g1.globo.com/rss/g1/tecnologia/`).
4. Use o botão **Toggle** (interruptor) na lista para pausar um feed sem deletá-lo.

### 3. Modo Evergreen (Gerador de Guias)
Use esta função para criar conteúdo atemporal que ranqueia bem no Google a longo prazo.
1. Vá na aba **Evergreen**.
2. Digite um tema amplo. Exemplo: *"Benefícios da Yoga para Iniciantes"*.
3. Clique em **Gerar Agora**.
4. **O que acontece:** O robô vai ignorar as notícias do dia e criar um "Guia Definitivo" sobre o tema, com imagens ilustrativas e vídeos educativos do YouTube.

### 4. Toggles Globais (Economia)
Na aba **Configurações**, você tem controles mestres:
* **Gerar Imagens (Vertex AI):** Desative se quiser economizar créditos do Google Cloud. O post sairá sem imagem destacada (ou usará placeholder).
* **Buscar Vídeos:** Desative se preferir posts apenas com texto e imagem.
* **Aprovação Manual:**
    * **Ativado:** O robô cria o post como "Rascunho" ou salva numa fila interna (veja em http://localhost:5001).
    * **Desativado:** O robô publica diretamente no seu site (Cuidado!).

### 5. Manutenção e Performance ("Botão Mágico")
Se o dashboard ficar lento após muitas gerações:
1.  Vá em **Configurações > Painel de Controle**.
2.  Clique em **Otimizar Sistema**.
3.  O robô fará uma faxina na memória RAM e compactará o arquivo de banco de dados (`.db`) para recuperar performance.


## Dicas de Segurança
* **Hard Limit:** Mantenha o "Limite de Artigos/Ciclo" em 5 ou menos para evitar que seu site pareça um spammer.
* **Logs:** Se algo der errado, verifique a caixa preta de logs na Home. "FAIL" ou "ERROR" indicarão o problema.