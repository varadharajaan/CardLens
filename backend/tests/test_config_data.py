"""Tests for externalized config-data loading and bank detection."""

from __future__ import annotations

from app.shared.config.data_loader import get_data_loader


def test_known_banks_are_loaded() -> None:
    loader = get_data_loader()

    assert loader.bank("ICICI") is not None
    assert loader.bank("HDFC") is not None
    assert loader.bank("YES") is not None


def test_detect_bank_from_statement_text() -> None:
    loader = get_data_loader()

    assert loader.detect_bank("Your HDFC Bank credit card statement is ready") == "HDFC"
    assert loader.detect_bank("ICICI Bank Amazon Pay statement") == "ICICI"


def test_password_rules_are_config_driven() -> None:
    loader = get_data_loader()

    axis_rules = loader.password_rules("AXIS")
    assert axis_rules
    assert all(rule.template for rule in axis_rules)


def test_reward_value_resolution_order() -> None:
    loader = get_data_loader()

    assert loader.reward_value_per_point(program="AMEX_MR_POINTS") == 0.45
    assert loader.reward_value_per_point(reward_type="CASHBACK") == 1.0
    assert loader.reward_value_per_point() > 0
