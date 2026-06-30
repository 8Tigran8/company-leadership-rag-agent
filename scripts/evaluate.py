from __future__ import annotations

import json
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from company_rag.db import connect, load_fixture
from company_rag.fixtures import read_fixture
from company_rag.rag.retriever import retrieve

FIXTURE_PATHS = [
    Path("data/fixtures/robinhood.com.json"),
    Path("data/fixtures/meetcampfire.com.json"),
]

REQUIRED_FILES = [
    Path("README.md"),
    Path("pyproject.toml"),
    Path("uv.lock"),
    Path(".env.example"),
    Path("session.json"),
    Path("data/fixtures/robinhood.com.json"),
    Path("data/fixtures/meetcampfire.com.json"),
]


@dataclass(frozen=True)
class GoldenQuestion:
    domain: str
    fixture_path: Path
    question: str
    required_substrings: tuple[str, ...]
    forbidden_substrings: tuple[str, ...] = ()
    require_citation: bool = True


GOLDEN_QUESTIONS = [
    GoldenQuestion(
        domain="robinhood.com",
        fixture_path=Path("data/fixtures/robinhood.com.json"),
        question="Who's their CTO?",
        required_substrings=("could not verify a current CTO",),
        forbidden_substrings=("Jeffrey Pinner",),
    ),
    GoldenQuestion(
        domain="robinhood.com",
        fixture_path=Path("data/fixtures/robinhood.com.json"),
        question="How many VPs do they have?",
        required_substrings=("12 current VP/SVP/EVP", "Chris Koegel", "Seok Lee"),
    ),
    GoldenQuestion(
        domain="robinhood.com",
        fixture_path=Path("data/fixtures/robinhood.com.json"),
        question="Who heads marketing?",
        required_substrings=("Deepak Rao",),
    ),
    GoldenQuestion(
        domain="robinhood.com",
        fixture_path=Path("data/fixtures/robinhood.com.json"),
        question="Where is their CEO based?",
        required_substrings=("Bay Area of California",),
    ),
    GoldenQuestion(
        domain="meetcampfire.com",
        fixture_path=Path("data/fixtures/meetcampfire.com.json"),
        question="Who's their CTO?",
        required_substrings=("Paul Nichols",),
    ),
    GoldenQuestion(
        domain="meetcampfire.com",
        fixture_path=Path("data/fixtures/meetcampfire.com.json"),
        question="How many VPs do they have?",
        required_substrings=("1 current VP/SVP/EVP",),
    ),
    GoldenQuestion(
        domain="meetcampfire.com",
        fixture_path=Path("data/fixtures/meetcampfire.com.json"),
        question="Who heads marketing?",
        required_substrings=("Katrina Queirolo",),
    ),
    GoldenQuestion(
        domain="meetcampfire.com",
        fixture_path=Path("data/fixtures/meetcampfire.com.json"),
        question="Where is their CEO based?",
        required_substrings=("San Francisco, California",),
    ),
]


def main() -> int:
    report = evaluate()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["summary"]["overall_status"] == "pass" else 1


def evaluate() -> dict[str, Any]:
    fixture_reports = [_fixture_metrics(path) for path in FIXTURE_PATHS]
    golden_reports = [_run_golden_question(question) for question in GOLDEN_QUESTIONS]
    repository_report = _repository_metrics()

    total_claims = sum(item["claims"] for item in fixture_reports)
    source_covered_claims = sum(
        item["claim_source_url_coverage"]["passed"] for item in fixture_reports
    )
    evidence_covered_claims = sum(
        item["claim_evidence_coverage"]["passed"] for item in fixture_reports
    )
    source_text_supported_claims = sum(
        item["claim_source_text_support"]["passed"] for item in fixture_reports
    )
    normalized_role_claims = sum(
        item["role_normalization_coverage"]["passed"] for item in fixture_reports
    )
    total_role_claims = sum(
        item["role_normalization_coverage"]["total"] for item in fixture_reports
    )
    trusted_sources = sum(item["trusted_source_coverage"]["passed"] for item in fixture_reports)
    total_sources = sum(item["trusted_source_coverage"]["total"] for item in fixture_reports)
    duplicate_name_count = sum(item["duplicate_name_count"] for item in fixture_reports)
    passed_golden = sum(1 for item in golden_reports if item["status"] == "pass")

    thresholds = {
        "required_files_present": repository_report["required_files"]["missing"] == [],
        "fixtures_valid": all(item["status"] == "pass" for item in fixture_reports),
        "claim_source_url_coverage": source_covered_claims == total_claims,
        "claim_evidence_coverage": evidence_covered_claims == total_claims,
        "claim_source_text_support": source_text_supported_claims == total_claims,
        "role_normalization_coverage": normalized_role_claims == total_role_claims,
        "trusted_source_coverage": trusted_sources == total_sources,
        "duplicate_name_count": duplicate_name_count == 0,
        "golden_question_pass_rate": passed_golden == len(golden_reports),
    }

    return {
        "summary": {
            "overall_status": "pass" if all(thresholds.values()) else "fail",
            "fixtures": len(fixture_reports),
            "people": sum(item["people"] for item in fixture_reports),
            "claims": total_claims,
            "sources": total_sources,
            "golden_questions": {
                "passed": passed_golden,
                "total": len(golden_reports),
                "rate": _ratio(passed_golden, len(golden_reports)),
            },
            "thresholds": thresholds,
        },
        "repository": repository_report,
        "fixtures": fixture_reports,
        "golden_questions": golden_reports,
    }


def _repository_metrics() -> dict[str, Any]:
    missing = [str(path) for path in REQUIRED_FILES if not path.exists()]
    return {
        "required_files": {
            "passed": len(REQUIRED_FILES) - len(missing),
            "total": len(REQUIRED_FILES),
            "missing": missing,
        }
    }


def _fixture_metrics(path: Path) -> dict[str, Any]:
    fixture = read_fixture(path)
    sources = {source.id: source for source in fixture.sources}
    people = {person.id: person for person in fixture.people}
    role_claims = [claim for claim in fixture.claims if claim.claim_type == "role"]

    source_url_passed = sum(
        1
        for claim in fixture.claims
        if claim.source_id in sources and bool(sources[claim.source_id].url)
    )
    evidence_passed = sum(1 for claim in fixture.claims if bool(claim.evidence.strip()))
    source_text_support_passed = 0
    unsupported_claims: list[str] = []
    for claim in fixture.claims:
        source = sources.get(claim.source_id)
        person = people.get(claim.person_id)
        if source and person and person.name in source.text and claim.value in source.text:
            source_text_support_passed += 1
        else:
            unsupported_claims.append(claim.id)

    normalized_role_passed = sum(1 for claim in role_claims if bool(claim.normalized_role))
    trusted_source_types = {"official", "sec", "public-profile"}
    trusted_source_passed = sum(
        1 for source in fixture.sources if source.source_type in trusted_source_types
    )
    duplicate_name_count = len(fixture.people) - len(
        {person.name.lower() for person in fixture.people}
    )

    status = "pass"
    if unsupported_claims or duplicate_name_count or normalized_role_passed != len(role_claims):
        status = "fail"

    return {
        "path": str(path),
        "domain": fixture.company.domain,
        "status": status,
        "people": len(fixture.people),
        "claims": len(fixture.claims),
        "sources": len(fixture.sources),
        "current_claims": sum(1 for claim in fixture.claims if claim.status == "current"),
        "former_claims": sum(1 for claim in fixture.claims if claim.status == "former"),
        "claim_source_url_coverage": _coverage(source_url_passed, len(fixture.claims)),
        "claim_evidence_coverage": _coverage(evidence_passed, len(fixture.claims)),
        "claim_source_text_support": _coverage(source_text_support_passed, len(fixture.claims)),
        "role_normalization_coverage": _coverage(normalized_role_passed, len(role_claims)),
        "trusted_source_coverage": _coverage(trusted_source_passed, len(fixture.sources)),
        "duplicate_name_count": duplicate_name_count,
        "unsupported_claim_ids": unsupported_claims,
        "source_types": sorted({source.source_type for source in fixture.sources}),
    }


def _run_golden_question(question: GoldenQuestion) -> dict[str, Any]:
    fixture = read_fixture(question.fixture_path)
    with tempfile.TemporaryDirectory(prefix="company-rag-eval-") as temp_dir:
        db_path = Path(temp_dir) / "eval.sqlite"
        with connect(db_path) as conn:
            load_fixture(conn, fixture)
            result = retrieve(conn, question.domain, question.question)

    missing = [text for text in question.required_substrings if text not in result.answer]
    forbidden = [text for text in question.forbidden_substrings if text in result.answer]
    citation_failed = question.require_citation and not result.citations
    status = "fail" if missing or forbidden or citation_failed else "pass"
    return {
        "domain": question.domain,
        "question": question.question,
        "status": status,
        "intent": result.intent,
        "citation_count": len(result.citations),
        "missing_required_substrings": missing,
        "forbidden_substrings_present": forbidden,
        "answer": result.answer,
    }


def _coverage(passed: int, total: int) -> dict[str, Any]:
    return {"passed": passed, "total": total, "rate": _ratio(passed, total)}


def _ratio(passed: int, total: int) -> float:
    return round(passed / total, 4) if total else 1.0


if __name__ == "__main__":
    sys.exit(main())
