from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    db_path: Path
    cache_dir: Path
    llm_provider: str
    openai_api_key: str | None
    openai_model: str


def get_settings() -> Settings:
    load_dotenv()

    return Settings(
        db_path=Path(os.getenv("COMPANY_RAG_DB_PATH", "data/company_rag.sqlite")),
        cache_dir=Path(os.getenv("COMPANY_RAG_CACHE_DIR", "data/cache")),
        llm_provider=os.getenv("LLM_PROVIDER", "openai"),
        openai_api_key=os.getenv("OPENAI_API_KEY") or None,
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
    )

