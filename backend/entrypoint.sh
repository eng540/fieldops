#!/bin/bash
# إيقاف التشغيل فوراً إذا فشل أي أمر
set -e

echo "🚀 Starting Database Migrations..."
# تشغيل كل ملفات الهجرة لبناء الجداول
alembic upgrade heads

echo "✅ Migrations Complete. Starting Server..."
# تشغيل خادم FastAPI
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}