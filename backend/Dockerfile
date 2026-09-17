FROM python:3.12-slim

WORKDIR /app

# Dependencias de sistema para psycopg2 y bcrypt
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Aplica migraciones y arranca la API. En produccion se ejecuta con
# varios workers detras de un proxy (nginx/traefik/ALB, etc.).
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
