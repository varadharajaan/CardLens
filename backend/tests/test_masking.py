"""Tests for sensitive-data masking helpers."""

from __future__ import annotations

from app.shared.logging.masking import mask_card_number, mask_email, mask_mapping


def test_mask_card_number_keeps_last_four() -> None:
    masked = mask_card_number("4111 1111 1111 1234")

    assert masked.endswith("1234")
    assert "4111" not in masked


def test_mask_email_partial() -> None:
    masked = mask_email("varadharajaan@outlook.com")

    assert masked.endswith("@outlook.com")
    assert masked.startswith("v")
    assert "varadharajaan" not in masked


def test_mask_mapping_redacts_sensitive_keys() -> None:
    masked = mask_mapping({"password": "hunter2", "refresh_token": "abc.def", "note": "ok"})

    assert masked["password"] == "***REDACTED***"
    assert masked["refresh_token"] == "***REDACTED***"
    assert masked["note"] == "ok"


def test_mask_mapping_masks_embedded_card_number() -> None:
    masked = mask_mapping({"evidence": "charged on card 4111111111111234 today"})

    assert "4111111111111234" not in masked["evidence"]
    assert "1234" in masked["evidence"]
