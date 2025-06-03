FROM python:3.11-slim

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

# libs mínimas para Firefox/Playwright + Tor socks
RUN apt-get update && apt-get install -y \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r /app/requirements.txt \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

ENV PYTHONPATH=/app

COPY ./app/ /app

CMD ["uvicorn", "main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
