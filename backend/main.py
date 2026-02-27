"""
FastAPI application entry point for LlamaTron CDS Agent.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.core.config import get_settings
from backend.core.logger import logger
from backend.services.inference import inference_service
from backend.routers import analysis, session, export

cfg = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting LlamaTron CDS Agent API...")
    inference_service.load()          # warm up model on startup
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title="LlamaTron RS1 Nemesis — Clinical Decision Support Agent",
    description=(
        "AI-powered clinical reasoning: symptom analysis → "
        "differential diagnosis → treatment planning.\n\n"
        "**Disclaimer:** For research and educational purposes only."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analysis.router)
app.include_router(session.router)
app.include_router(export.router)


@app.get("/health", tags=["Health"])
async def health():
    return {
        "status": "ok",
        "model": cfg.model_id,
        "model_loaded": inference_service._loaded,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=cfg.api_host,
                port=cfg.api_port, reload=True)
