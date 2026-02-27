"""
Centralised configuration — reads from .env / environment variables.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Model
    model_id: str = "Rumiii/LlamaTron_RS1_Nemesis_1B"
    device: str = "auto"
    torch_dtype: str = "bfloat16"
    max_new_tokens: int = 600
    temperature: float = 0.7
    top_p: float = 0.9

    # Server
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    gradio_port: int = 7860
    gradio_share: bool = False

    # PDF
    pdf_font: str = "Helvetica"
    logo_path: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
