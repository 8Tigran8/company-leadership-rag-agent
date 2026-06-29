import pytest

from company_rag.normalize import (
    is_excluded_title,
    normalize_department,
    normalize_domain,
    normalize_title,
)


def test_normalize_domain_accepts_url_and_domain() -> None:
    assert normalize_domain("https://www.robinhood.com/us/en/") == "robinhood.com"
    assert normalize_domain("meetcampfire.com") == "meetcampfire.com"


def test_normalize_domain_rejects_invalid_value() -> None:
    with pytest.raises(ValueError):
        normalize_domain("not-a-domain")


def test_normalize_title_maps_required_roles() -> None:
    assert normalize_title("Chief Technology Officer").normalized_role == "CTO"
    assert normalize_title("SVP and GM, Growth and Marketing").normalized_role == "SVP"
    assert normalize_title("Head of Product").seniority == "head"
    assert normalize_title("VP, Corporate Finance & Investor Relations").normalized_role == "VP"
    assert normalize_title("Chief Brokerage Officer").normalized_role == "CXO"
    assert normalize_department("Managing Director, Robinhood Strategies") is None


def test_excluded_title_keeps_investor_relations_leaders() -> None:
    assert not is_excluded_title("VP, Corporate Finance & Investor Relations")
    assert is_excluded_title("Strategic Advisor")
