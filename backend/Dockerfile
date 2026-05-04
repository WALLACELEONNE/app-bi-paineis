FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN echo '#!/bin/sh' > /entrypoint.sh && \
    echo 'cd /app && alembic upgrade head' >> /entrypoint.sh && \
    echo 'exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --log-level debug' >> /entrypoint.sh && \
    chmod +x /entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
