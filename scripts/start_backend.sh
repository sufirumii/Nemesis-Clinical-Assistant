#!/bin/bash
set -e
echo "🚀 Starting LlamaTron CDS Agent Backend..."
source .env 2>/dev/null || true
python -m uvicorn backend.main:app \
  --host "${API_HOST:-0.0.0.0}" \
  --port "${API_PORT:-8000}" \
  --reload \
  --log-level info
