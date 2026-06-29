"""PDF handling: config-driven password unlock and text extraction. No passwords hardcoded.

Password candidates are generated from the bank's rules in ``pdf_password_rules.yaml`` combined with
user/card attributes. Each candidate is tried until the PDF opens; the rules are data, not code.
"""

from __future__ import annotations

import io
from dataclasses import dataclass

import pdfplumber
from pypdf import PdfReader
from pypdf.errors import PdfReadError

from app.shared.config.data_loader import get_data_loader


@dataclass
class CardholderHints:
    """Attributes used to materialize password candidates from templated rules."""

    name: str | None = None
    dob_ddmm: str | None = None
    dob_ddmmyy: str | None = None
    card_last4: str | None = None
    card_last6: str | None = None
    crn: str | None = None


def _tokens(h: CardholderHints) -> dict[str, str]:
    name = (h.name or "").strip()
    initials = "".join(part[0] for part in name.split() if part).lower()
    return {
        "name4_lower": name[:4].lower(),
        "name4_upper": name[:4].upper(),
        "name_initials": initials,
        "dob_ddmm": h.dob_ddmm or "",
        "dob_ddmmyy": h.dob_ddmmyy or "",
        "card_last4": h.card_last4 or "",
        "card_last6": h.card_last6 or "",
        "crn": h.crn or "",
    }


def password_candidates(bank: str, hints: CardholderHints) -> list[str]:
    """Return ordered password candidates for a bank from the externalized rule templates."""
    tokens = _tokens(hints)
    candidates: list[str] = []
    for rule in get_data_loader().password_rules(bank):
        try:
            value = rule.template.format(**tokens)
        except KeyError:
            continue
        if value and value not in candidates:
            candidates.append(value)
    return candidates


def unlock(content: bytes, candidates: list[str]) -> bytes | None:
    """Return decrypted PDF bytes if any candidate opens it, else the bytes if not encrypted, else None."""
    reader = PdfReader(io.BytesIO(content))
    if not reader.is_encrypted:
        return content
    for candidate in candidates:
        try:
            if PdfReader(io.BytesIO(content)).decrypt(candidate):
                return content
        except (PdfReadError, NotImplementedError):
            continue
    return None


def extract_text(content: bytes, password: str | None = None) -> str:
    """Extract concatenated text from every page using pdfplumber."""
    with pdfplumber.open(io.BytesIO(content), password=password) as pdf:
        return "\n".join(page.extract_text() or "" for page in pdf.pages)
