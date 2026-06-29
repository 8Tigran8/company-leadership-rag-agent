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
    openai_base_url: str | None = None
    openai_timeout_seconds: float = 60.0
    openai_max_retries: int = 3
    codex_command: str = "codex"
    codex_model: str | None = None
    codex_timeout_seconds: float = 120.0


def get_settings() -> Settings:
    load_dotenv()

    return Settings(
        db_path=Path(os.getenv("COMPANY_RAG_DB_PATH", "data/company_rag.sqlite")),
        cache_dir=Path(os.getenv("COMPANY_RAG_CACHE_DIR", "data/cache")),
        llm_provider=os.getenv("LLM_PROVIDER", "openai"),
        openai_api_key=os.getenv("OPENAI_API_KEY") or None,
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        openai_base_url=os.getenv("OPENAI_BASE_URL") or None,
        openai_timeout_seconds=float(os.getenv("OPENAI_TIMEOUT_SECONDS", "60")),
        openai_max_retries=int(os.getenv("OPENAI_MAX_RETRIES", "3")),
        codex_command=os.getenv("CODEX_COMMAND", "codex"),
        codex_model=os.getenv("CODEX_MODEL") or None,
        codex_timeout_seconds=float(os.getenv("CODEX_TIMEOUT_SECONDS", "120")),
    )
