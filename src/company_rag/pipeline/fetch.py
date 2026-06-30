from __future__ import annotations

import hashlib
import re
from datetime import UTC, datetime
from pathlib import Path

import httpx
from bs4 import BeautifulSoup

from company_rag.models import SourceDocument
from company_rag.normalize import slugify

FETCH_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36 "
        "company-leadership-rag-agent/0.1"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def fetch_source(url: str, *, company_domain: str, cache_dir: Path) -> SourceDocument | None:
    cache_dir.mkdir(parents=True, exist_ok=True)
    try:
        response = httpx.get(
            url,
            follow_redirects=True,
            timeout=20,
            headers=FETCH_HEADERS,
        )
    except httpx.HTTPError:
        return None
    if response.status_code >= 400 or not response.text.strip():
        return None

    html = response.text
    cache_key = hashlib.sha256(str(response.url).encode()).hexdigest()[:16]
    (cache_dir / f"{cache_key}.html").write_text(html)
    title, text = html_to_text(html)
    if not text:
        return None

    return SourceDocument(
        id=f"src_{slugify(company_domain)}_{cache_key}",
        company_domain=company_domain,
        url=str(response.url),
        title=title or str(response.url),
        source_type="web",
        fetched_at=datetime.now(UTC).isoformat(),
        text=text,
        confidence="Medium",
        metadata={
            "status_code": response.status_code,
            "content_sha256": hashlib.sha256(html.encode()).hexdigest(),
        },
    )


def html_to_text(html: str) -> tuple[str, str]:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "svg"]):
        tag.decompose()
    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    text = soup.get_text("\n", strip=True)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return title, text[:100000]
