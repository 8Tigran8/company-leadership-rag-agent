from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from uuid import uuid4

from company_rag.config import Settings
from company_rag.llm import LLMUnavailableError, compose_answer
from company_rag.rag.retriever import RetrievalResult, retrieve


def answer_question(
    conn: sqlite3.Connection,
    settings: Settings,
    *,
    domain: str,
    question: str,
    use_llm: bool = True,
) -> tuple[str, RetrievalResult]:
    result = retrieve(conn, domain, question)
    citation_dicts = [citation.__dict__ for citation in result.citations]
    answer = result.answer
    if use_llm:
        try:
            answer = compose_answer(
                settings,
                question=question,
                grounded_answer=result.answer,
                citations=citation_dicts,
            )
        except LLMUnavailableError:
            answer = "[local retrieval mode - OPENAI_API_KEY not set]\n" + result.answer
        except Exception as exc:
            answer = f"[local retrieval mode - LLM composition failed: {type(exc).__name__}]\n"
            answer += result.answer
    return answer, result


def create_chat_session(conn: sqlite3.Connection, domain: str) -> str:
    session_id = f"chat_{uuid4().hex[:12]}"
    conn.execute(
        "INSERT INTO chat_sessions(id, company_domain, created_at) VALUES (?, ?, ?)",
        (session_id, domain, _now()),
    )
    conn.commit()
    return session_id


def save_chat_message(
    conn: sqlite3.Connection,
    *,
    session_id: str,
    role: str,
    content: str,
    citations_json: str = "[]",
) -> None:
    conn.execute(
        """
        INSERT INTO chat_messages(id, session_id, role, content, created_at, citations_json)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (f"msg_{uuid4().hex[:12]}", session_id, role, content, _now(), citations_json),
    )
    conn.commit()


def _now() -> str:
    return datetime.now(UTC).isoformat()
