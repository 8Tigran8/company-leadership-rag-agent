from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import urlparse


def normalize_domain(value: str) -> str:
    candidate = value.strip()
    if not candidate:
        raise ValueError("Domain or URL is required.")
    if "://" not in candidate:
        candidate = f"https://{candidate}"

    parsed = urlparse(candidate)
    host = parsed.netloc.lower()
    if "@" in host:
        host = host.rsplit("@", 1)[-1]
    if ":" in host:
        host = host.split(":", 1)[0]
    if host.startswith("www."):
        host = host[4:]
    if not host or "." not in host:
        raise ValueError(f"Invalid company domain or URL: {value}")
    return host.rstrip(".")


def canonical_url(value: str) -> str:
    domain = normalize_domain(value)
    return f"https://{domain}/"


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "item"


@dataclass(frozen=True)
class NormalizedTitle:
    normalized_role: str | None
    seniority: str | None
    department: str | None


def normalize_title(title: str) -> NormalizedTitle:
    text = title.lower()
    role: str | None = None
    seniority: str | None = None

    if "chief executive officer" in text or re.search(r"\bceo\b", text):
        role, seniority = "CEO", "c_level"
    elif "chief technology officer" in text or re.search(r"\bcto\b", text):
        role, seniority = "CTO", "c_level"
    elif "chief financial officer" in text or re.search(r"\bcfo\b", text):
        role, seniority = "CFO", "c_level"
    elif "chief marketing officer" in text or re.search(r"\bcmo\b", text):
        role, seniority = "CMO", "c_level"
    elif "chief operating officer" in text or re.search(r"\bcoo\b", text):
        role, seniority = "COO", "c_level"
    elif "chief information security officer" in text or re.search(r"\bciso\b", text):
        role, seniority = "CISO", "c_level"
    elif "chief investment officer" in text or re.search(r"\bcio\b", text):
        role, seniority = "CIO", "c_level"
    elif "chief legal" in text or "general counsel" in text:
        role, seniority = "CLO", "c_level"
    elif "chief people officer" in text:
        role, seniority = "CPO", "c_level"
    elif "senior vice president" in text or re.search(r"\bsvp\b", text):
        role, seniority = "SVP", "vice_president"
    elif "executive vice president" in text or re.search(r"\bevp\b", text):
        role, seniority = "EVP", "vice_president"
    elif "vice president" in text or re.search(r"\bvp\b", text):
        role, seniority = "VP", "vice_president"
    elif (
        "head of " in text
        or "chief of staff" in text
        or "president" in text
        or "general manager" in text
    ):
        role, seniority = "HEAD", "head"
    elif "senior director" in text or "director" in text:
        role, seniority = "DIRECTOR", "head"

    department = normalize_department(title)
    return NormalizedTitle(normalized_role=role, seniority=seniority, department=department)


def normalize_department(title: str) -> str | None:
    text = title.lower()
    mappings = [
        ("Marketing", ["marketing", "brand", "communications", "growth"]),
        ("Finance", ["finance", "financial", "treasury", "accounting", "investor relations"]),
        ("Engineering", ["engineering", "technology", "technical", "cto"]),
        ("Product", ["product"]),
        ("Legal", ["legal", "compliance", "general counsel", "corporate affairs"]),
        ("People", ["people", "human resources", "rewards", "talent"]),
        ("Risk", ["risk", "audit"]),
        ("Operations", ["operations", "chief of staff", "operating"]),
        ("Security", ["security", "ciso"]),
        ("Brokerage", ["brokerage", "securities"]),
        ("Crypto", ["crypto", "bitstamp"]),
        ("Go-to-market", ["go-to-market", "sales", "partnerships", "business development"]),
        ("Executive", ["ceo", "chief executive", "founder"]),
    ]
    for department, keywords in mappings:
        if any(keyword in text for keyword in keywords):
            return department
    return None


def is_excluded_title(title: str) -> bool:
    text = title.lower()
    excluded = ["board", "advisor", "former", "investor", "angel", "partner at"]
    return any(word in text for word in excluded)
