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
COPY ./django_project/ /app/django_project

# Executa o servidor Django
CMD ["python", "django_project/manage.py", "runserver", "0.0.0.0:8000"]
