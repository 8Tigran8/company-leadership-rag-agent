from company_rag.llm import _validated_extracted_people


def test_validated_extracted_people_coerces_empty_optional_fields() -> None:
    people = _validated_extracted_people(
        [
            {
                "name": "Paul Nichols",
                "title": "CTO",
                "department": "",
                "location": "null",
                "profile_url": "",
                "evidence": "The engineering team at Campfire is led by CTO Paul Nichols.",
                "confidence": 0.9,
                "current": True,
            }
        ]
    )

    assert len(people) == 1
    assert people[0].name == "Paul Nichols"
    assert people[0].profile_url is None
    assert people[0].department is None
    assert people[0].location is None


def test_validated_extracted_people_skips_invalid_payload_items() -> None:
    people = _validated_extracted_people(
        [
            {"name": "Missing title"},
            {
                "name": "Valid Leader",
                "title": "Chief Executive Officer",
                "evidence": "Valid Leader is Chief Executive Officer.",
                "confidence": 0.8,
            },
        ]
    )

    assert [person.name for person in people] == ["Valid Leader"]
