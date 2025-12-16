# Imagem base Python
FROM python:3.10-slim

# Metadados
LABEL maintainer="S1M0N Publisher Automation"
LABEL description="Content Robot - Automated News Publisher"

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Diretório de trabalho
WORKDIR /app

# Instala dependências do sistema necessárias
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Copia arquivos de requisitos primeiro (cache de layer)
COPY requirements.txt .

# Instala dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação
COPY . .

# Cria diretório para dados persistentes
RUN mkdir -p /app/data

# Expõe porta do dashboard (se aplicável)
EXPOSE 5000

# Health check padrão
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Comando padrão (pode ser sobrescrito no docker-compose)
CMD ["python", "main.py"]
