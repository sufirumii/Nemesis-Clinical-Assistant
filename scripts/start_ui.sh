#!/bin/bash
set -e
echo "🌐 Starting LlamaTron CDS Agent UI..."
source .env 2>/dev/null || true
python frontend/app.py
