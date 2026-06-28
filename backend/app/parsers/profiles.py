"""Versioned, config-driven parser profiles loaded from ``config/data/parser_profiles/<bank>/vN.yaml``.

A new real-world statement layout is added as a NEW version file (never an edit to an existing one).
The engine selects the highest-version profile whose fingerprint keywords all appear in the text.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml
from pydantic import BaseModel, Field

from app.config import settings


class FieldRule(BaseModel):
    """A single extraction rule: a regex with a named ``value`` group and a coercion type."""

    pattern: str
    type: str = "text"


class Profile(BaseModel):
    """A versioned parser profile for one bank's statement layout."""

    bank: str
    version: int
    reward_type: str | None = None
    fingerprint: list[str] = Field(default_factory=list)
    fields: dict[str, FieldRule] = Field(default_factory=dict)
    reward: dict[str, FieldRule] = Field(default_factory=dict)


class ProfileLoader:
    """Loads and caches every versioned profile and selects one for a given statement."""

    def __init__(self, base_dir: Path) -> None:
        self._dir = base_dir
        self._profiles: list[Profile] | None = None

    def _all(self) -> list[Profile]:
        if self._profiles is None:
            loaded: list[Profile] = []
            if self._dir.exists():
                for path in sorted(self._dir.glob("*/v*.yaml")):
                    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
                    loaded.append(Profile(**raw))
            self._profiles = loaded
        return self._profiles

    def all(self) -> list[Profile]:
        """Return every loaded profile."""
        return list(self._all())

    def for_bank(self, bank: str) -> list[Profile]:
        """Return a bank's profiles, newest version first."""
        target = bank.strip().upper()
        return sorted(
            (p for p in self._all() if p.bank.upper() == target),
            key=lambda p: p.version,
            reverse=True,
        )

    def select(self, bank: str | None, text: str) -> Profile | None:
        """Pick the best profile: prefer a fingerprint match, then the newest version.

        When ``bank`` is given, only that bank's profiles are considered; otherwise every profile is a
        candidate and the fingerprint is what resolves the bank.
        """
        candidates = self.for_bank(bank) if bank else self._all()
        haystack = text.lower()
        matched = [
            p
            for p in candidates
            if p.fingerprint and all(keyword.lower() in haystack for keyword in p.fingerprint)
        ]
        pool = matched or ([] if bank is None else candidates)
        if not pool:
            return None
        return sorted(pool, key=lambda p: p.version, reverse=True)[0]


@lru_cache(maxsize=1)
def get_profile_loader() -> ProfileLoader:
    """Return the process-wide parser profile loader singleton."""
    return ProfileLoader(settings.config_dir / "parser_profiles")
