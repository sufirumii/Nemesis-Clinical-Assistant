# Nemesis Clinical Assistant

A clinical decision support system powered by a fine-tuned Meta Llama 3.2 1B Instruct for symptom analysis, differential diagnosis, and treatment planning.

## Demo
<img width="1920" height="1128" alt="1" src="https://github.com/user-attachments/assets/de7eeb1e-c29a-4083-823d-cebd1b9c87a0" />

<img width="1757" height="1008" alt="2" src="https://github.com/user-attachments/assets/fdf22c28-af67-4967-a35c-72d2b92b0637" />

<img width="1730" height="854" alt="3" src="https://github.com/user-attachments/assets/c7b7c582-e445-4e30-bcdd-9e3d84f25134" />

---

## Overview

I fine-tuned Meta Llama 3.2 1B Instruct on 204,773 clinical reasoning conversations and named it LlamaTron RS1 Nemesis. Instead of leaving it as a research experiment, I built it into a proper deployable system with a FastAPI backend, Gradio UI, session memory, PDF report export, and a pytest suite wired to GitHub Actions CI.

The model loads once into memory and serves all requests through a proper API layer. Sessions persist across turns so the model maintains context. PDF exports are generated programmatically with ReportLab. The frontend talks to the backend over HTTP, meaning either can be swapped or scaled independently.

---

## Built With

- **Base Model** — Meta Llama 3.2 1B Instruct
- **Fine-tuned Model** — LlamaTron RS1 Nemesis ([Rumiii/LlamaTron_RS1_Nemesis_1B](https://huggingface.co/Rumiii/LlamaTron_RS1_Nemesis_1B))
- **Training Dataset** — [OpenMed/Medical-Reasoning-SFT-MiniMax-M2.1](https://huggingface.co/datasets/OpenMed/Medical-Reasoning-SFT-MiniMax-M2.1) (204,773 clinical conversations)
- **Backend** — FastAPI + Uvicorn
- **Frontend** — Gradio
- **PDF Export** — ReportLab
- **CI** — GitHub Actions

---

## Key Files

| File | Purpose |
|------|---------|
| `backend/main.py` | FastAPI entry point — registers all routers and warms the model on startup |
| `backend/services/inference.py` | Singleton model loader — loads LlamaTron RS1 Nemesis once and keeps it in memory |
| `backend/services/session.py` | Conversation memory — persists multi-turn context per session |
| `backend/services/pdf_export.py` | PDF generation — builds branded clinical reports using ReportLab |
| `backend/routers/analysis.py` | POST `/analyze` — runs clinical reasoning on symptoms |
| `backend/routers/session.py` | GET/DELETE `/history/{session_id}` — retrieve or clear session |
| `backend/routers/export.py` | POST `/export-pdf` — exports session as downloadable PDF |
| `frontend/app.py` | Gradio UI — fully decoupled from backend, communicates over HTTP |
| `tests/test_api.py` | pytest suite with mocked inference for CI |
| `.github/workflows/ci.yml` | GitHub Actions — runs tests and linting on every push |

---

## Architecture

```
Gradio Frontend  (port 7860)
       │
       │  HTTP
       ▼
FastAPI Backend  (port 8000)
       │
       ├── POST /analyze      →  InferenceService  (LlamaTron RS1 Nemesis)
       ├── GET  /history      →  SessionService
       ├── POST /export-pdf   →  PDFService
       └── GET  /health
```

---

## Getting Started

### 1. Clone and install

```bash
git clone https://github.com/sufirumii/Nemesis-Clinical-Assistant
cd Nemesis-Clinical-Assistant
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env — set DEVICE=cuda if you have a GPU
```

### 3. Start the backend

```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Start the UI (new terminal)

```bash
python frontend/app.py
```

Open `http://localhost:7860` for the UI and `http://localhost:8000/docs` for the API.

---

## Running on Kaggle (Recommended — Free GPU)

Run each cell in order in a Kaggle notebook.

**Cell 1 — Clone and install**
```python
%cd /kaggle/working
!git clone https://github.com/sufirumii/Nemesis-Clinical-Assistant
%cd Nemesis-Clinical-Assistant
!pip install -r requirements.txt -q
```

**Cell 2 — Start the FastAPI backend**
```python
import subprocess, time, threading

def run_backend():
    subprocess.run(["python", "-m", "uvicorn", "backend.main:app",
                    "--host", "0.0.0.0", "--port", "8000"])

threading.Thread(target=run_backend, daemon=True).start()
time.sleep(15)  # model is ~2.5GB — give it time to load
print("Backend should be up!")
```

**Cell 3 — Health check**
```python
import httpx
r = httpx.get("http://localhost:8000/health")
print(r.json())  # should show {"status": "ok", "model_loaded": true}
```

**Cell 4 — Launch Gradio UI with public link**
```python
import os, sys
os.environ["GRADIO_SHARE"] = "true"
sys.path.insert(0, "/kaggle/working/Nemesis-Clinical-Assistant")
exec(open("frontend/app.py").read())
```

Kaggle will print a public `gradio.live` link — open it in any browser.

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/analyze` | Run clinical reasoning on symptoms |
| GET | `/history/{session_id}` | Retrieve session conversation |
| DELETE | `/history/{session_id}` | Clear session |
| POST | `/export-pdf` | Export session as PDF report |
| GET | `/health` | Health check |

**Example request**

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "abc123",
    "symptoms": "45-year-old male, fever 39.8C for 4 days, productive cough, right-sided chest pain on breathing",
    "patient_age": 45,
    "patient_sex": "male"
  }'
```

---

## Disclaimer

This system is intended for **research and educational purposes only**. It is not a substitute for professional medical advice, diagnosis, or treatment. Always consult a qualified healthcare provider for clinical decisions.

---

## License

Apache 2.0 — see [LICENSE](LICENSE) for details.
