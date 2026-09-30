from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[1]

class Settings(BaseSettings):
    groq_api_key: str = ""
    groq_model: str = "openai/gpt-oss-120b"
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    chroma_path: str = "./data/chroma"
    top_k: int = 5
    temperature: float = 0.1

    model_config = SettingsConfigDict(env_file=ROOT / ".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def chroma_dir(self) -> Path:
        p = Path(self.chroma_path)
        return p if p.is_absolute() else ROOT / p

@lru_cache
def get_settings() -> Settings:
    return Settings()

def project_path(value: str) -> Path:
    p = Path(value)
    return p if p.is_absolute() else ROOT / p
