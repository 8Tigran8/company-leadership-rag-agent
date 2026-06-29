from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from contextlib import suppress
from pathlib import Path
from typing import Any

from company_rag.config import Settings
from company_rag.models import LLMExtractedPerson


class LLMUnavailableError(RuntimeError):
    pass


def _client(settings: Settings):
    api_key = settings.openai_api_key
    if settings.llm_provider == "ollama" and not api_key:
        api_key = "ollama"
    if not api_key:
        raise LLMUnavailableError("OPENAI_API_KEY is required for real LLM calls.")
    try:
        from openai import OpenAI
    except ImportError as exc:  # pragma: no cover - dependency guard
        raise LLMUnavailableError("The openai package is not installed.") from exc
    return OpenAI(
        api_key=api_key,
        base_url=settings.openai_base_url,
        timeout=settings.openai_timeout_seconds,
        max_retries=settings.openai_max_retries,
    )


def compose_answer(
    settings: Settings,
    *,
    question: str,
    grounded_answer: str,
    citations: list[dict[str, Any]],
) -> str:
    citation_text = "\n".join(
        f"[{item['index']}] {item['title']} - {item['url']}\nEvidence: {item['evidence']}"
        for item in citations
    )
    if settings.llm_provider == "codex":
        prompt = (
            "You answer questions over a collected company leadership dataset.\n"
            "Use only the provided grounded answer and citations. Do not inspect files, "
            "run commands, or add outside facts. Preserve uncertainty. Cite sources as "
            "[1], [2].\n\n"
            f"Question: {question}\n\n"
            f"Grounded answer: {grounded_answer}\n\n"
            f"Citations:\n{citation_text}\n\n"
            "Write a concise final answer. Return only the final answer text."
        )
        return _complete_with_codex(settings, prompt)

    client = _client(settings)
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
    if settings.llm_provider == "codex":
        prompt = (
            "Extract current company leadership people from public source text. "
            "Include C-level executives, VPs/SVPs/EVPs, and Heads of departments. "
            "Exclude board-only members, advisors, investors, former employees, "
            "and article authors "
            "unless they also have a current operating leadership role at the target company. "
            "Return strict JSON only with no markdown fences or commentary.\n\n"
            f"Company: {company_name}\n"
            f"Source title: {source_title}\n"
            f"Expected JSON shape: {json.dumps(schema)}\n\n"
            f"Source text:\n{source_text[:20000]}"
        )
        content = _complete_with_codex(settings, prompt)
        payload = _loads_json_object(content)
        people = payload.get("people", [])
        return _validated_extracted_people(people)

    client = _client(settings)
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
    return _validated_extracted_people(people)


def _complete_with_codex(settings: Settings, prompt: str) -> str:
    command = _resolve_codex_command(settings.codex_command)
    if command is None:
        raise LLMUnavailableError(
            f"Codex command '{settings.codex_command}' was not found. "
            "Install/login to Codex CLI or use OPENAI_API_KEY/Ollama."
        )

    fd, output_path = tempfile.mkstemp(prefix="company-rag-codex-", suffix=".txt")
    os.close(fd)
    args = [
        command,
        "exec",
        "--ephemeral",
        "--skip-git-repo-check",
        "--sandbox",
        "read-only",
        "--output-last-message",
        output_path,
    ]
    if settings.codex_model:
        args.extend(["--model", settings.codex_model])
    args.append("-")

    try:
        result = subprocess.run(
            args,
            input=prompt,
            text=True,
            capture_output=True,
            timeout=settings.codex_timeout_seconds,
            check=False,
        )
        output = ""
        try:
            with open(output_path) as file:
                output = file.read().strip()
        except OSError:
            output = ""
        if result.returncode != 0:
            details = (result.stderr or result.stdout).strip()
            raise RuntimeError(
                f"codex exec failed with code {result.returncode}: {details[-1000:]}"
            )
        return output or result.stdout.strip()
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(
            f"codex exec timed out after {settings.codex_timeout_seconds} seconds"
        ) from exc
    finally:
        with suppress(OSError):
            os.remove(output_path)


def _resolve_codex_command(command: str) -> str | None:
    resolved = shutil.which(command)
    if resolved is not None:
        return resolved

    candidate = Path(command)
    if candidate.is_file():
        return str(candidate)

    if command == "codex":
        bundled_codex = Path("/Applications/Codex.app/Contents/Resources/codex")
        if bundled_codex.is_file():
            return str(bundled_codex)
    return None


def _loads_json_object(content: str) -> dict[str, Any]:
    text = content.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return json.loads(text or "{}")


def _validated_extracted_people(items: Any) -> list[LLMExtractedPerson]:
    if not isinstance(items, list):
        return []

    people: list[LLMExtractedPerson] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        cleaned = dict(item)
        for key in ("department", "location", "profile_url"):
            if _is_empty_optional_value(cleaned.get(key)):
                cleaned[key] = None
        if _is_empty_optional_value(cleaned.get("confidence")):
            cleaned["confidence"] = 0.0
        try:
            people.append(LLMExtractedPerson.model_validate(cleaned))
        except ValueError:
            continue
    return people


def _is_empty_optional_value(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"", "none", "null", "n/a"}
    return False
