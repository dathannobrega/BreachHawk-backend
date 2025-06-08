FROM python:3.11-slim

# ───── dependências de sistema (Playwright + Chromium) ─────
RUN apt-get update && apt-get install -y \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdbus-1-3 \
    libdrm2 libxkbcommon0 libxcomposite1 libxrandr2 libxdamage1 \
    libxfixes3 libxcb1 libx11-6 libx11-xcb1 libpangocairo-1.0-0 \
    libgtk-3-0 libasound2 xvfb wget curl && \
    rm -rf /var/lib/apt/lists/*

# Diretório de trabalho
WORKDIR /app

# Copia requirements e instala dependências Python
COPY ./backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Instala o navegador Chromium com dependências
RUN PLAYWRIGHT_BROWSERS_PATH=/ms-playwright \
    playwright install --with-deps chromium

# Copia o código-fonte
COPY ./backend/django_project /app/

# Define PYTHONPATH
ENV PYTHONPATH=/app:/app/
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# Comando padrão
ENV DJANGO_SETTINGS_MODULE=breachhawk.settings
CMD ["celery", "-A", "breachhawk.celery", "worker", "-l", "info", "-Ofair"]
