"""Parser request/response schemas (DTOs)."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field


class ParsePreviewRequest(BaseModel):
    """Raw statement text to parse, with an optional bank hint."""

    bank: str | None = Field(default=None, max_length=40)
    text: str = Field(min_length=1)


class ParsedStatement(BaseModel):
    """The structured result of parsing statement text with a versioned profile.

    Reward extraction is mandatory: ``reward_parse_status`` is always one of FOUND / PARTIAL /
    NOT_FOUND with a confidence, a human-readable reason, and (when found) an evidence snippet, so a
    reward outcome is never silently dropped. ``manual_review_flag`` is set whenever the parse is not
    fully confident.
    """

    bank: str
    profile_version: int
    card_name: str | None = None
    last4: str | None = None
    statement_date: date | None = None
    due_date: date | None = None
    total_due: float | None = None
    minimum_due: float | None = None
    reward_points_closing: int | None = None
    reward_points_credited: int | None = None
    cashback_earned: float | None = None
    reward_type: str | None = None
    reward_parse_status: str
    reward_confidence: float
    reward_parse_reason: str
    evidence_snippet: str | None = None
    parse_confidence: float
    manual_review_flag: bool
