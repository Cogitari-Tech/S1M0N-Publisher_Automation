# 🐳 S1M0N Publisher Automation - Docker

## Guia Rápido de Uso

### 1️⃣ Configuração Inicial

```bash
# Copie o arquivo de exemplo para .env
cp .env.docker .env

# Edite o arquivo .env com suas credenciais
nano .env
```

**Variáveis Obrigatórias:**
- `GOOGLE_API_KEY` - Chave da API do Google Gemini
- `FLASK_SECRET_KEY` - Chave secreta para o dashboard
- Pelo menos uma chave de provedor de notícias (NEWSAPI_KEY, CURRENTS_API_KEY ou GNEWS_API_KEY)

### 2️⃣ Executar o Projeto

```bash
# Iniciar todos os serviços
docker-compose up -d

# Ver logs em tempo real
docker-compose logs -f

# Ver logs de um serviço específico
docker-compose logs -f dashboard
docker-compose logs -f robot
```

### 3️⃣ Acessar o Dashboard

Abra o navegador em: **http://localhost:5000**

### 4️⃣ Comandos Úteis

```bash
# Parar os serviços
docker-compose stop

# Parar e remover containers
docker-compose down

# Parar, remover e limpar volumes (CUIDADO: apaga o banco de dados)
docker-compose down -v

# Reconstruir as imagens
docker-compose build

# Reiniciar um serviço específico
docker-compose restart dashboard

# Ver status dos containers
docker-compose ps

# Executar comandos dentro de um container
docker-compose exec robot python system_health_check.py
docker-compose exec dashboard bash
```

### 5️⃣ Estrutura dos Serviços

#### 🤖 Robot Service
- **Container:** `s1m0n-robot`
- **Função:** Motor principal de automação (busca, processa e agenda publicações)
- **Comando:** `python main.py`
- **Reinicia:** Automaticamente em caso de falha

#### 📊 Dashboard Service
- **Container:** `s1m0n-dashboard`
- **Função:** Interface web de gerenciamento
- **Porta:** 5000 (configurável via `DASHBOARD_PORT`)
- **Comando:** `python dashboard_launcher.py`
- **Acesso:** http://localhost:5000

### 6️⃣ Volumes e Persistência

Os dados são armazenados em volumes Docker:
- `robot-data`: Banco de dados SQLite e arquivos gerados
- Localização: `/app/data/content_robot.db`

### 7️⃣ Troubleshooting

**Problema: Dashboard não abre**
```bash
# Verifique se o container está rodando
docker-compose ps

# Veja os logs
docker-compose logs dashboard
```

**Problema: Erros de configuração**
```bash
# Verifique as variáveis de ambiente
docker-compose exec robot env | grep GOOGLE

# Teste a conexão com o banco
docker-compose exec robot python system_health_check.py
```

**Problema: Permissões de volume**
```bash
# Se tiver problemas de permissão no Linux
sudo chown -R $USER:$USER ./data
```

### 8️⃣ Desenvolvimento Local

Para rodar com código local (hot-reload):

```bash
# Os volumes já estão mapeados, basta editar os arquivos
# e reiniciar o serviço desejado
docker-compose restart robot
docker-compose restart dashboard
```

### 9️⃣ Segurança

⚠️ **IMPORTANTE:**
- Nunca commite o arquivo `.env` com credenciais reais
- Use senhas fortes para `FLASK_SECRET_KEY`
- Em produção, use secrets management (AWS Secrets, Docker Secrets, etc)

### 🔟 Ambiente de Produção

Para produção, considere:

```bash
# Use docker-compose.prod.yml separado
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Configure reverse proxy (Nginx/Traefik)
# Use certificados SSL
# Configure backups automáticos do volume robot-data
```

---

## 📝 Notas

- O banco de dados SQLite é compartilhado entre os serviços via volume
- Os serviços comunicam-se através da rede `s1m0n-network`
- Health checks garantem que os serviços estão saudáveis
- Logs são salvos em `robot.log` dentro do container
