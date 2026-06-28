"""Generic extraction engine: applies a profile's regex rules to statement text and classifies rewards."""

from __future__ import annotations

import re
from datetime import date, datetime

from app.parsers.profiles import FieldRule, Profile
from app.parsers.schemas import ParsedStatement

_DATE_FORMATS = (
    "%d-%m-%Y",
    "%d/%m/%Y",
    "%d-%m-%y",
    "%d/%m/%y",
    "%d %b %Y",
    "%d-%b-%Y",
    "%d %B %Y",
    "%d-%b-%y",
)


def _coerce(value: str, kind: str) -> object | None:
    text = value.strip()
    if kind == "money":
        try:
            return float(text.replace(",", ""))
        except ValueError:
            return None
    if kind == "int":
        try:
            return int(text.replace(",", ""))
        except ValueError:
            return None
    if kind == "date":
        for fmt in _DATE_FORMATS:
            try:
                return datetime.strptime(text, fmt).date()
            except ValueError:
                continue
        return None
    return text


def _match(rule: FieldRule, text: str) -> tuple[object, str] | None:
    found = re.search(rule.pattern, text, re.IGNORECASE)
    if not found:
        return None
    raw = found.group("value") if "value" in found.groupdict() else found.group(0)
    coerced = _coerce(raw, rule.type)
    if coerced is None:
        return None
    return coerced, found.group(0).strip()


def _as_float(value: object | None) -> float | None:
    return value if isinstance(value, float) else None


def _as_int(value: object | None) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def _as_date(value: object | None) -> date | None:
    return value if isinstance(value, date) else None


def _as_text(value: object | None) -> str | None:
    return value.strip() if isinstance(value, str) else None


def extract(profile: Profile, text: str) -> ParsedStatement:
    """Run every field and reward rule in ``profile`` over ``text`` and build a ParsedStatement."""
    fields: dict[str, object] = {}
    for name, rule in profile.fields.items():
        result = _match(rule, text)
        if result is not None:
            fields[name] = result[0]
    parse_confidence = round(len(fields) / max(len(profile.fields), 1), 2)

    reward: dict[str, object] = {}
    evidence: str | None = None
    for name, rule in profile.reward.items():
        result = _match(rule, text)
        if result is not None:
            reward[name] = result[0]
            if evidence is None:
                evidence = result[1]

    closing = _as_int(reward.get("points_closing"))
    cashback = _as_float(reward.get("cashback"))
    credited = _as_int(reward.get("points_credited"))
    if closing is not None or cashback is not None:
        reward_status, reward_confidence = "FOUND", 0.9
        reason = "Closing reward balance or cashback located in the statement."
    elif credited is not None:
        reward_status, reward_confidence = "PARTIAL", 0.5
        reason = "Only partial reward signals found (earned points); closing balance missing."
    else:
        reward_status, reward_confidence = "NOT_FOUND", 0.0
        reason = "No reward fields matched the statement text."

    return ParsedStatement(
        bank=profile.bank,
        profile_version=profile.version,
        card_name=_as_text(fields.get("card_name")),
        last4=_as_text(fields.get("last4")),
        statement_date=_as_date(fields.get("statement_date")),
        due_date=_as_date(fields.get("due_date")),
        total_due=_as_float(fields.get("total_due")),
        minimum_due=_as_float(fields.get("minimum_due")),
        reward_points_closing=closing,
        reward_points_credited=credited,
        cashback_earned=cashback,
        reward_type=profile.reward_type,
        reward_parse_status=reward_status,
        reward_confidence=reward_confidence,
        reward_parse_reason=reason,
        evidence_snippet=evidence,
        parse_confidence=parse_confidence,
        manual_review_flag=reward_status != "FOUND" or parse_confidence < 0.5,
    )
