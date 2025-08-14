# Updated Dockerfile with proper permissions
FROM python:3.12-slim as builder

RUN apt-get update && apt-get install -y \
    build-essential gcc g++ libpq-dev libffi-dev \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    libpq5 curl wget gnupg ca-certificates \
    fonts-liberation libappindicator3-1 libasound2 \
    libatk-bridge2.0-0 libatk1.0-0 libcups2 \
    libdbus-1-3 libdrm2 libgtk-3-0 libnspr4 \
    libnss3 libxcomposite1 libxdamage1 libxfixes3 \
    libxrandr2 libxss1 libxtst6 xdg-utils \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create user and directories
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Create directories with proper permissions
RUN mkdir -p /app/cache /app/uploads /app/tmp \
    /home/appuser/.cache/ms-playwright && \
    chown -R appuser:appuser /app /home/appuser

# Set environment variables
ENV TRANSFORMERS_CACHE=/app/cache
ENV HF_HOME=/app/cache
ENV SENTENCE_TRANSFORMERS_HOME=/app/cache
ENV PLAYWRIGHT_BROWSERS_PATH=/home/appuser/.cache/ms-playwright
ENV TMPDIR=/app/tmp

# Install Playwright browsers as root first
RUN python -m playwright install chromium

COPY --chown=appuser:appuser . .

# Fix Playwright permissions for appuser
RUN chown -R appuser:appuser /root/.cache/ms-playwright || true

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]