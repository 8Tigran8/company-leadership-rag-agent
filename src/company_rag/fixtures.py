from __future__ import annotations

import json
from pathlib import Path

from company_rag.models import Fixture


def read_fixture(path: Path) -> Fixture:
    return Fixture.model_validate_json(path.read_text())


def write_fixture(path: Path, fixture: Fixture) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = fixture.model_dump(mode="json", exclude_none=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")

