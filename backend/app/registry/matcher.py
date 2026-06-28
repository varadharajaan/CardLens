"""Pure card-to-registry matching logic.

Operates on any objects exposing ``bank`` and ``card_name`` attributes, so it is trivially unit
testable without a database. Scoring: an exact bank-code match contributes half the score, and the
fraction of query card-name tokens found in the candidate contributes the other half.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from typing import Protocol


class _MatchCandidate(Protocol):
    bank: str
    card_name: str


def _tokens(text: str | None) -> set[str]:
    return set(re.sub(r"[^a-z0-9]+", " ", (text or "").lower()).split())


def best_match(
    bank: str | None, card_name: str | None, entries: Sequence[_MatchCandidate]
) -> tuple[_MatchCandidate | None, float]:
    """Return the best-matching candidate and its score in the range 0.0 to 1.0."""
    normalized_bank = (bank or "").strip().upper()
    query_tokens = _tokens(card_name)
    best: _MatchCandidate | None = None
    best_score = 0.0
    for entry in entries:
        score = 0.0
        if normalized_bank and entry.bank.upper() == normalized_bank:
            score += 0.5
        entry_tokens = _tokens(entry.card_name)
        if query_tokens and entry_tokens:
            score += 0.5 * (len(query_tokens & entry_tokens) / len(query_tokens))
        if score > best_score:
            best_score = score
            best = entry
    return best, round(best_score, 3)
