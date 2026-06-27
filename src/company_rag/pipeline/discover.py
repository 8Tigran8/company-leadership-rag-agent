from __future__ import annotations

import xml.etree.ElementTree as ET
from urllib.parse import urljoin

import httpx

from company_rag.normalize import canonical_url, normalize_domain

KNOWN_PATHS = [
    "/about",
    "/about-us",
    "/team",
    "/leadership",
    "/management",
    "/company",
    "/people",
    "/investor-relations",
    "/governance",
    "/governance/leadership",
    "/newsroom",
    "/blog",
]


DOMAIN_SEEDS = {
    "robinhood.com": [
        "https://investors.robinhood.com/governance/leadership/",
        "https://investors.robinhood.com/management/vlad-tenev",
        "https://www.sec.gov/Archives/edgar/data/1783879/000178387926000065/hood-20260507.htm",
    ],
    "meetcampfire.com": [
        "https://campfire.ai/blog/campfire-65-million-series-b-co-led-by-accel-and-ribbit",
        "https://campfire.ai/blog/campfire-accelerates-accounting-with-claude",
        "https://campfire.ai/blog/introducing-askember-in-slack",
    ],
    "campfire.ai": [
        "https://campfire.ai/blog/campfire-65-million-series-b-co-led-by-accel-and-ribbit",
        "https://campfire.ai/blog/campfire-accelerates-accounting-with-claude",
        "https://campfire.ai/blog/introducing-askember-in-slack",
    ],
}


def discover_sources(input_url: str, limit: int = 30) -> list[str]:
    domain = normalize_domain(input_url)
    urls: list[str] = []
    seen: set[str] = set()

    def add(url: str) -> None:
        if url not in seen and len(urls) < limit:
            seen.add(url)
            urls.append(url)

    for url in DOMAIN_SEEDS.get(domain, []):
        add(url)

    base = canonical_url(input_url)
    add(base)
    for path in KNOWN_PATHS:
        add(urljoin(base, path.lstrip("/")))

    for url in _sitemap_urls(base):
        add(url)

    return urls


def _sitemap_urls(base_url: str) -> list[str]:
    try:
        response = httpx.get(urljoin(base_url, "/sitemap.xml"), timeout=8, follow_redirects=True)
    except httpx.HTTPError:
        return []
    if response.status_code >= 400:
        return []
    try:
        root = ET.fromstring(response.text)
    except ET.ParseError:
        return []
    urls = [
        element.text.strip()
        for element in root.iter()
        if element.tag.endswith("loc") and element.text and element.text.strip()
    ]
    leadership_terms = (
        "about",
        "team",
        "leadership",
        "management",
        "governance",
        "investor",
        "company",
        "people",
        "blog",
    )
    return [url for url in urls if any(term in url.lower() for term in leadership_terms)][:20]
