#!/bin/bash
set -e
echo "🏥 LlamaTron CDS Agent — Full Stack Start"
echo "Starting backend in background..."
bash scripts/start_backend.sh &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"
sleep 8
echo "Starting Gradio UI..."
bash scripts/start_ui.sh
