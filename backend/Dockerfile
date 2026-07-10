# syntax=docker/dockerfile:1
FROM python:3.12-slim as builder

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry

# Copy dependency files
COPY pyproject.toml poetry.lock* ./

# Install dependencies (no root package yet)
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# ─────────────────────────────────────────
# Production stage
# ─────────────────────────────────────────
FROM python:3.12-slim as production

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini ./
# نسخ سكريبت الإقلاع الجديد
COPY entrypoint.sh ./

# Non-root user for security (مع إعطاء صلاحية التنفيذ للسكريبت)
RUN groupadd -r fieldops && useradd -r -g fieldops fieldops \
    && chown -R fieldops:fieldops /app \
    && chmod +x /app/entrypoint.sh

USER fieldops

EXPOSE 8000

# جعل الحاوية تبدأ من خلال سكريبت الإقلاع الذي يبني قاعدة البيانات أولاً
CMD ["./entrypoint.sh"]