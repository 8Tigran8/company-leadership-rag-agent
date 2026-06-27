from __future__ import annotations

import json
from typing import Any

from company_rag.config import Settings
from company_rag.models import LLMExtractedPerson


class LLMUnavailableError(RuntimeError):
    pass


def _client(settings: Settings):
    if not settings.openai_api_key:
        raise LLMUnavailableError("OPENAI_API_KEY is required for real LLM calls.")
    try:
        from openai import OpenAI
    except ImportError as exc:  # pragma: no cover - dependency guard
        raise LLMUnavailableError("The openai package is not installed.") from exc
    return OpenAI(api_key=settings.openai_api_key)


def compose_answer(
    settings: Settings,
    *,
    question: str,
    grounded_answer: str,
    citations: list[dict[str, Any]],
) -> str:
    client = _client(settings)
    citation_text = "\n".join(
        f"[{item['index']}] {item['title']} - {item['url']}\nEvidence: {item['evidence']}"
        for item in citations
    )
    messages = [
        {
            "role": "system",
            "content": (
                "You answer questions over a collected company leadership dataset. "
                "Use only the provided grounded answer and citations. "
                "Do not add outside facts. Preserve uncertainty. Cite sources as [1], [2]."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Question: {question}\n\n"
                f"Grounded answer: {grounded_answer}\n\n"
                f"Citations:\n{citation_text}\n\n"
                "Write a concise final answer."
            ),
        },
    ]
    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=messages,
        temperature=0,
    )
    content = response.choices[0].message.content
    return content.strip() if content else grounded_answer


def extract_people(settings: Settings, *, company_name: str, source_title: str, source_text: str):
    client = _client(settings)
    schema = {
        "people": [
            {
                "name": "Full name",
                "title": "Current professional title at the target company",
                "department": "Department or function, if explicit or strongly implied",
                "location": "Person-specific location, only if stated",
                "profile_url": "Public profile URL, if present",
                "evidence": "Short source-backed evidence snippet",
                "confidence": 0.0,
                "current": True,
            }
        ]
    }
    messages = [
        {
            "role": "system",
            "content": (
                "Extract current company leadership people from public source text. "
                "Include C-level executives, VPs/SVPs/EVPs, and Heads of departments. "
                "Exclude board-only members, advisors, investors, former employees, "
                "and article authors "
                "unless they also have a current operating leadership role at the target company. "
                "Return strict JSON only."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Company: {company_name}\n"
                f"Source title: {source_title}\n"
                f"Expected JSON shape: {json.dumps(schema)}\n\n"
                f"Source text:\n{source_text[:20000]}"
            ),
        },
    ]
    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=messages,
        temperature=0,
        response_format={"type": "json_object"},
    )
    content = response.choices[0].message.content or "{}"
    payload = json.loads(content)
    people = payload.get("people", [])
    return [LLMExtractedPerson.model_validate(item) for item in people]
