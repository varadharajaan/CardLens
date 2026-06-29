"""PDF password-candidate generation and Document Intelligence adapter tests."""

from __future__ import annotations

from app.config import settings
from app.parsers.docintel import DocumentIntelligence
from app.parsers.pdf import CardholderHints, password_candidates


def test_password_candidates_from_rules() -> None:
    cands = password_candidates("ICICI", CardholderHints(name="Varad", dob_ddmm="0906"))
    assert "vara0906" in cands


def test_password_candidates_unknown_bank_is_empty() -> None:
    assert password_candidates("NOPE", CardholderHints(name="Varad")) == []


def test_docintel_disabled_without_endpoint() -> None:
    client = DocumentIntelligence()
    assert client.enabled is bool(settings.azure_docintel_endpoint and settings.azure_docintel_key)
    if not client.enabled:
        assert client.analyze_text(b"%PDF-1.4 dummy") == ""
