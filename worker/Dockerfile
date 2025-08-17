FROM python:3.11-slim

# ───── dependências de sistema (Chromium do Playwright) ─────
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl wget git xvfb \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdbus-1-3 \
    libdrm2 libxkbcommon0 libxcomposite1 libxrandr2 libxdamage1 \
    libxfixes3 libxcb1 libx11-6 libx11-xcb1 libpangocairo-1.0-0 \
    libgtk-3-0 libasound2 libgbm1 libxshmfence1 libpci3 xdg-utils \
    # fontes (equivalentes no Debian trixie)
    fonts-unifont fonts-ubuntu fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# Diretório de trabalho
WORKDIR /app

# Dependências Python
COPY ./backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Instala **apenas** o navegador (sem tentar deps via apt)
# (o comando 'playwright' vem do pacote Python 'playwright')
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
RUN playwright install chromium

# Código-fonte
COPY ./backend/django_project /app/

# Ambiente
ENV PYTHONPATH=/app:/app/
ENV DJANGO_SETTINGS_MODULE=breachhawk.settings

# Processo
CMD ["celery", "-A", "breachhawk.celery", "worker", "-l", "info", "-Ofair"]
