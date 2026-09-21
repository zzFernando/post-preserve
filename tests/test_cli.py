from postpreserve.cli import main


def test_archive_command_returns_nonzero_when_capture_fails(monkeypatch):
    monkeypatch.setattr(
        "postpreserve.cli.archive",
        lambda *args, **kwargs: {"final_status": "failed", "errors": ["capture failed"]},
    )

    assert main(["archive", "https://www.instagram.com/p/EXAMPLE/"]) == 1


def test_archive_command_returns_distinct_code_for_partial_capture(monkeypatch):
    monkeypatch.setattr(
        "postpreserve.cli.archive",
        lambda *args, **kwargs: {"final_status": "partial"},
    )

    assert main(["archive", "https://www.instagram.com/p/EXAMPLE/"]) == 2
