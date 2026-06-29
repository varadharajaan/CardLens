"""Parser orchestration: select a profile for the statement text and extract a ParsedStatement."""

from __future__ import annotations

from app.parsers.docintel import DocumentIntelligence
from app.parsers.engine import extract
from app.parsers.pdf import CardholderHints, extract_text, password_candidates, unlock
from app.parsers.profiles import get_profile_loader
from app.parsers.schemas import ParsedStatement
from app.shared.config.data_loader import get_data_loader
from app.shared.errors.exceptions import DomainValidationError
from app.shared.logging.context import get_logger

_logger = get_logger("cardlens.parsers")


class ParserService:
    """Resolves a versioned profile for statement text and runs the extraction engine."""

    def __init__(self) -> None:
        self._loader = get_profile_loader()
        self._data = get_data_loader()

    def parse_text(self, bank: str | None, text: str) -> ParsedStatement:
        """Parse raw statement text. Raises :class:`DomainValidationError` when no profile matches.

        The bank is taken from the caller's hint, or detected from the text via the bank keyword
        config. An unmatched layout is surfaced as a 422 (never a silently wrong parse).
        """
        bank_hint = bank or self._data.detect_bank(text)
        profile = self._loader.select(bank_hint, text)
        if profile is None:
            raise DomainValidationError(
                "No parser profile matches this statement; it needs manual review or a new profile."
            )
        parsed = extract(profile, text)
        _logger.info(
            "statement.parsed",
            bank=parsed.bank,
            profile_version=parsed.profile_version,
            reward_parse_status=parsed.reward_parse_status,
            parse_confidence=parsed.parse_confidence,
        )
        return parsed

    def parse_pdf(self, content: bytes, bank: str | None, hints: CardholderHints) -> ParsedStatement:
        """Unlock (config passwords), extract text (pdfplumber, then Document Intelligence), and parse.

        Falls back to the Document Intelligence adapter when local extraction yields nothing; raises
        :class:`DomainValidationError` when the PDF cannot be read or matched to a profile.
        """
        candidates = password_candidates(bank, hints) if bank else []
        if unlock(content, candidates) is None:
            raise DomainValidationError("PDF is encrypted and no configured password unlocked it.")
        text = ""
        for password in [None, *candidates]:
            try:
                text = extract_text(content, password)
            except Exception:  # noqa: BLE001 - try the next candidate / fallback
                text = ""
            if text.strip():
                break
        if not text.strip():
            text = DocumentIntelligence().analyze_text(content)
        if not text.strip():
            raise DomainValidationError("Could not extract any text from the PDF.")
        return self.parse_text(bank, text)
