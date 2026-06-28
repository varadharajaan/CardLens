"""Parser orchestration: select a profile for the statement text and extract a ParsedStatement."""

from __future__ import annotations

from app.parsers.engine import extract
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
