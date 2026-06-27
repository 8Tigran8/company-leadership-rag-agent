from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, HttpUrl

Confidence = Literal["High", "Medium", "Low"]
ClaimType = Literal["role", "department", "location", "profile", "note"]


class Company(BaseModel):
    domain: str
    name: str
    website_url: str | None = None


class SourceDocument(BaseModel):
    id: str
    company_domain: str
    url: str
    title: str
    source_type: str = "web"
    fetched_at: str
    text: str = ""
    confidence: Confidence = "Medium"
    metadata: dict[str, Any] = Field(default_factory=dict)


class Person(BaseModel):
    id: str
    company_domain: str
    name: str
    profile_url: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class Claim(BaseModel):
    id: str
    company_domain: str
    person_id: str
    claim_type: ClaimType
    value: str
    normalized_role: str | None = None
    seniority: str | None = None
    department: str | None = None
    status: str = "current"
    source_id: str
    evidence: str
    confidence: Confidence = "Medium"
    extracted_at: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class Fixture(BaseModel):
    company: Company
    sources: list[SourceDocument]
    people: list[Person]
    claims: list[Claim]
    generated_at: str
    generator_version: str = "0.1.0"
    notes: list[str] = Field(default_factory=list)


class LLMExtractedPerson(BaseModel):
    name: str
    title: str
    department: str | None = None
    location: str | None = None
    profile_url: HttpUrl | None = None
    evidence: str
    confidence: float = Field(ge=0, le=1)
    current: bool = True

