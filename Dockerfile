FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    PATH="/root/.local/bin:$PATH"

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# instale só as deps de produção
COPY requirements.prod.txt .
RUN pip install --no-cache-dir -r requirements.prod.txt

# copie o projeto
# copiar entrypoint e dar permissão
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# iniciar pelo entrypoint
CMD ["/app/entrypoint.sh"]