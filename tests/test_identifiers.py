from postpreserve.identifiers import validate_identifier


def test_identifier_format():
    assert validate_identifier("PP-IG-2026-000001")
    assert not validate_identifier("bad")

