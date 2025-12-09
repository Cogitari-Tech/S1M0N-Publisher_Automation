# Guia de Testes Locais com Docker

## Pré-requisitos
- Docker e Docker Compose instalados

## Comandos Disponíveis

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

### 5. Modo interativo (shell dentro do container)
```bash
docker-compose -f docker-compose.test.yml run --rm test bash
```

### 6. Limpar containers e imagens
```bash
docker-compose -f docker-compose.test.yml down --rmi all
```

## Estrutura
- `Dockerfile.test`: Imagem Python 3.10 com pytest, flake8 e dependências
- `docker-compose.test.yml`: Orquestração de serviços (test, test-with-coverage, lint)
- `.dockerignore`: Exclui arquivos desnecessários do build

## Exemplo de Fluxo de Trabalho
```bash
# 1. Build inicial
docker-compose -f docker-compose.test.yml build

# 2. Rodar lint
docker-compose -f docker-compose.test.yml up lint

# 3. Rodar testes
docker-compose -f docker-compose.test.yml up test

# 4. Gerar relatório de cobertura
docker-compose -f docker-compose.test.yml up test-with-coverage
```
