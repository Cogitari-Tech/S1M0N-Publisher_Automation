# Guia de Testes e Execução Local com Docker

## Pré-requisitos
- Docker e Docker Compose instalados
- Porta 5000 disponível (Dashboard)

---

## 🚀 Execução Completa (Dashboard + Robot em Background)

### 1. Iniciar a aplicação em background
```bash
docker-compose up -d
```
Isso inicia:
- **Dashboard** na `http://localhost:5000` (web interface)
- **Robot** processando conteúdo em background
- **Rede interna** para comunicação entre serviços

### 2. Verificar status dos serviços
```bash
docker-compose ps
```

### 3. Ver logs em tempo real
```bash
# Logs do dashboard
docker-compose logs -f dashboard

# Logs do robot
docker-compose logs -f robot

# Todos os logs
docker-compose logs -f
```

### 4. Parar a aplicação
```bash
docker-compose down
```

### 5. Limpar tudo (volumes, imagens)
```bash
docker-compose down -v --rmi all
```

### 6. Acessar shell do container em execução
```bash
docker-compose exec dashboard bash
docker-compose exec robot bash
```

---

## 🧪 Testes Unitários e Lint

### 1. Rodar todos os testes
```bash
docker-compose -f docker-compose.test.yml up test
```

### 2. Rodar testes com cobertura
```bash
docker-compose -f docker-compose.test.yml up test-with-coverage
```
O relatório HTML será gerado em `htmlcov/index.html`

### 3. Rodar apenas lint (verificação de código)
```bash
docker-compose -f docker-compose.test.yml up lint
```

### 4. Rodar testes específicos
```bash
docker-compose -f docker-compose.test.yml run --rm test pytest tests/test_smoke.py -v
```

### 5. Modo interativo (shell dentro do container de teste)
```bash
docker-compose -f docker-compose.test.yml run --rm test bash
```

### 6. Limpar containers de teste
```bash
docker-compose -f docker-compose.test.yml down --rmi all
```

---

## 📁 Estrutura de Arquivos

### Para Execução Completa
- `Dockerfile`: Imagem da aplicação (dashboard + robot)
- `docker-compose.yml`: Orquestração de serviços (dashboard, robot, db-helper)
- `.dockerignore`: Otimização de build

### Para Testes
- `Dockerfile.test`: Imagem com pytest, flake8 e dependências
- `docker-compose.test.yml`: Serviços de teste (test, test-with-coverage, lint)

---

## 📋 Fluxo de Desenvolvimento Típico

```bash
# 1. Iniciar ambiente completo em background
docker-compose up -d

# 2. Acessar dashboard
open http://localhost:5000

# 3. Ver logs em tempo real
docker-compose logs -f

# 4. Fazer edições no código (hot reload ativado via volumes)

# 5. Quando pronto, rodar testes
docker-compose -f docker-compose.test.yml up test

# 6. Parar tudo
docker-compose down
```

---

## 🔍 Troubleshooting

### Porta 5000 já em uso
```bash
# Liberar a porta ou usar outra no docker-compose.yml
# Editar: ports: - "5001:5000"
```

### Erro de permissão ao escrever logs/imagens
```bash
docker-compose exec dashboard bash
chmod -R 755 /app/logs /app/images
```

### Reiniciar um serviço específico
```bash
docker-compose restart dashboard
```

### Rebuild completo
```bash
docker-compose build --no-cache
```
