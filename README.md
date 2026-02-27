<div align="center">

# 🧠 LlamaTron RS1 Nemesis — Clinical Decision Support Agent

**A production-ready AI agent for symptom analysis, differential diagnosis, and treatment planning.**  
Built on [LlamaTron-RS1-Nemesis-1B](https://huggingface.co/Rumiii/LlamaTron_RS1_Nemesis_1B) — a Llama-3.2-1B model fine-tuned on 204K clinical reasoning conversations.

[![License](https://img.shields.io/badge/license-Apache_2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green.svg)](https://fastapi.tiangolo.com)
[![Gradio](https://img.shields.io/badge/Gradio-4.36-orange.svg)](https://gradio.app)
[![HuggingFace](https://img.shields.io/badge/Model-HuggingFace-yellow.svg)](https://huggingface.co/Rumiii/LlamaTron_RS1_Nemesis_1B)

</div>

---

## ✨ Features

- **Symptom → Differential Diagnosis → Treatment Plan** pipeline
- **Chain-of-thought reasoning display** — see the model think step by step
- **Export conversation as PDF** — professional clinical report
- **FastAPI backend** with `/analyze`, `/history`, `/export-pdf` endpoints
- **Gradio UI** with large, readable medical interface
- **Fully documented REST API** via Swagger at `/docs`

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│               Gradio Frontend               │
│         frontend/app.py  (port 7860)        │
└──────────────────┬──────────────────────────┘
                   │  HTTP  (httpx)
┌──────────────────▼──────────────────────────┐
│              FastAPI Backend                │
│         backend/main.py  (port 8000)        │
│                                             │
│  /analyze    →  InferenceService            │
│  /history    →  SessionService              │
│  /export-pdf →  PDFService                  │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│     LlamaTron RS1 Nemesis 1B (HF Hub)       │
│   Rumiii/LlamaTron_RS1_Nemesis_1B           │
└─────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### 1. Clone & install

```bash
git clone https://github.com/sufirumii/LlamaTron-CDS-Agent
cd LlamaTron-CDS-Agent
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env — set DEVICE=cuda if you have a GPU
```

### 3. Start the FastAPI backend

```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Start the Gradio UI (new terminal)

```bash
python frontend/app.py
```

Visit **http://localhost:7860** for the UI and **http://localhost:8000/docs** for the API.

---

## 🖥️ Running on Kaggle (GPU)

```python
# In a Kaggle notebook cell:
!git clone https://github.com/sufirumii/LlamaTron-CDS-Agent
%cd LlamaTron-CDS-Agent
!pip install -r requirements.txt -q
!cp .env.example .env

import subprocess, threading

def run_api():
    subprocess.run(["python", "-m", "uvicorn", "backend.main:app",
                    "--host", "0.0.0.0", "--port", "8000"])

threading.Thread(target=run_api, daemon=True).start()

# Then in another cell:
import os; os.environ["GRADIO_SHARE"] = "true"
!python frontend/app.py
```

---

## 📡 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/analyze` | Run clinical analysis on symptoms |
| GET | `/history/{session_id}` | Retrieve session conversation |
| DELETE | `/history/{session_id}` | Clear session |
| POST | `/export-pdf` | Export session as PDF report |
| GET | `/health` | Health check |

### Example request

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "abc123",
    "symptoms": "35-year-old male, fever 39.2C for 3 days, productive cough, right-sided chest pain on breathing",
    "patient_age": 35,
    "patient_sex": "male"
  }'
```

---

## ⚠️ Disclaimer

This tool is intended for **research and educational purposes only**.  
It is **not** a substitute for professional medical advice, diagnosis, or treatment.  
Always consult a qualified healthcare provider for medical decisions.

---

## 📄 License

Apache 2.0 — see [LICENSE](LICENSE) for details.

**Model:** [Rumiii/LlamaTron_RS1_Nemesis_1B](https://huggingface.co/Rumiii/LlamaTron_RS1_Nemesis_1B)  
**Dataset:** [OpenMed/Medical-Reasoning-SFT-MiniMax-M2.1](https://huggingface.co/datasets/OpenMed/Medical-Reasoning-SFT-MiniMax-M2.1)  
**Base Model:** [meta-llama/Llama-3.2-1B-Instruct](https://huggingface.co/meta-llama/Llama-3.2-1B-Instruct)
