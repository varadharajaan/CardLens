"""Typed loader for externalized YAML config data (banks, password rules, reward values).

This module is the only place that reads the data files under ``config/data``. It validates their
shape with Pydantic models and caches the parsed result. Adding a bank or rule is a data-file edit;
no code here changes. Bank detection is keyword-based against the externalized keyword lists.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field

from app.config import settings
from app.shared.logging.context import get_logger

_logger = get_logger("cardlens.config")

_BANKS_FILE = "banks.yaml"
_PASSWORD_RULES_FILE = "pdf_password_rules.yaml"  # noqa: S105 - filename, not a secret
_REWARD_VALUE_FILE = "reward_value_map.yaml"
_REWARD_MILESTONES_FILE = "reward_milestones.yaml"
_ANOMALY_RULES_FILE = "anomaly_rules.yaml"


class BankConfig(BaseModel):
    """A supported bank identity sourced from ``banks.yaml``."""

    code: str
    display_name: str
    aliases: list[str] = Field(default_factory=list)
    detection_keywords: list[str] = Field(default_factory=list)
    sender_domains: list[str] = Field(default_factory=list)


class PasswordRule(BaseModel):
    """A single PDF password candidate rule sourced from ``pdf_password_rules.yaml``."""

    id: str
    description: str = ""
    template: str
    example: str = ""


class MilestoneRule(BaseModel):
    """A reward milestone threshold sourced from ``reward_milestones.yaml``."""

    key: str
    label: str
    threshold: float


class AnomalyRules(BaseModel):
    """Tunable thresholds for dashboard anomaly detection from ``anomaly_rules.yaml``."""

    due_soon_days: int = 5
    high_utilization_pct: float = 80.0
    reward_drop_points: int = 1000
    large_due_amount: float = 100000.0


class DataLoader:
    """Loads, validates, and caches externalized config data with typed accessors."""

    def __init__(self, config_dir: Path) -> None:
        self._dir = config_dir
        self._banks: list[BankConfig] | None = None
        self._password_rules: dict[str, list[PasswordRule]] | None = None
        self._reward_values: dict[str, Any] | None = None
        self._reward_milestones: dict[str, list[MilestoneRule]] | None = None
        self._anomaly_rules: AnomalyRules | None = None

    def _read_yaml(self, filename: str) -> dict[str, Any]:
        path = self._dir / filename
        if not path.exists():
            raise FileNotFoundError(f"Required config data file is missing: {path}")
        with path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
        if not isinstance(data, dict):
            raise ValueError(f"Config data file is not a mapping: {path}")
        return data

    def banks(self) -> list[BankConfig]:
        """Return all supported banks."""
        if self._banks is None:
            raw = self._read_yaml(_BANKS_FILE)
            self._banks = [BankConfig(**entry) for entry in raw.get("banks", [])]
        return self._banks

    def bank(self, code: str) -> BankConfig | None:
        """Return the bank with the given code (case-insensitive), or None."""
        target = code.strip().upper()
        return next((bank for bank in self.banks() if bank.code.upper() == target), None)

    def detect_bank(self, text: str) -> str | None:
        """Return the bank code whose detection keywords best match the text, or None.

        Matching is case-insensitive and ranked by the number of distinct keyword hits so that a
        statement mentioning several brand terms resolves to the most specific bank.
        """
        if not text:
            return None
        haystack = text.lower()
        best_code: str | None = None
        best_score = 0
        for bank in self.banks():
            score = sum(1 for keyword in bank.detection_keywords if keyword.lower() in haystack)
            if score > best_score:
                best_score = score
                best_code = bank.code
        return best_code

    def password_rules(self, bank_code: str) -> list[PasswordRule]:
        """Return the ordered PDF password rules for a bank code (empty list if none configured)."""
        if self._password_rules is None:
            raw = self._read_yaml(_PASSWORD_RULES_FILE)
            self._password_rules = {
                code: [PasswordRule(**rule) for rule in rules] for code, rules in raw.get("rules", {}).items()
            }
        return self._password_rules.get(bank_code.strip().upper(), [])

    def _reward_value_data(self) -> dict[str, Any]:
        if self._reward_values is None:
            self._reward_values = self._read_yaml(_REWARD_VALUE_FILE)
        return self._reward_values

    def reward_value_per_point(self, program: str | None = None, reward_type: str | None = None) -> float:
        """Return the estimated INR value of one reward point.

        Resolution order: exact program match, then reward-type match, then the configured default.
        """
        data = self._reward_value_data()
        programs: dict[str, float] = data.get("programs", {})
        reward_types: dict[str, float] = data.get("reward_types", {})
        default = float(data.get("default_value_per_point", 0.25))
        if program and program in programs:
            return float(programs[program])
        if reward_type and reward_type in reward_types:
            return float(reward_types[reward_type])
        return default

    def reward_milestones(self) -> dict[str, list[MilestoneRule]]:
        """Return reward milestone thresholds grouped by reward format (ascending per format)."""
        if self._reward_milestones is None:
            raw = self._read_yaml(_REWARD_MILESTONES_FILE)
            self._reward_milestones = {
                fmt: [MilestoneRule(**item) for item in items] for fmt, items in raw.get("milestones", {}).items()
            }
        return self._reward_milestones

    def anomaly_rules(self) -> AnomalyRules:
        """Return the externalized anomaly-detection thresholds."""
        if self._anomaly_rules is None:
            raw = self._read_yaml(_ANOMALY_RULES_FILE)
            self._anomaly_rules = AnomalyRules(**raw.get("rules", {}))
        return self._anomaly_rules

    def validate_all(self) -> None:
        """Eagerly load and validate every data file so misconfiguration fails fast at startup."""
        bank_count = len(self.banks())
        rules = self._password_rules if self._password_rules is not None else None
        if rules is None:
            # Force load of password rules for validation.
            for bank in self.banks():
                self.password_rules(bank.code)
        self._reward_value_data()
        self.reward_milestones()
        self.anomaly_rules()
        _logger.info("config_data.loaded", banks=bank_count, config_dir=str(self._dir))


@lru_cache(maxsize=1)
def get_data_loader() -> DataLoader:
    """Return the process-wide data loader singleton."""
    return DataLoader(settings.config_dir)
