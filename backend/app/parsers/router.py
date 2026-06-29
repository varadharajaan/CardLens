"""Parser HTTP endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.parsers.pdf import CardholderHints
from app.parsers.schemas import ParsedStatement, ParsePreviewRequest
from app.parsers.service import ParserService
from app.shared.constants.api_paths import ApiPaths
from app.shared.security.deps import get_current_user_id

router = APIRouter(tags=["parsers"])


def get_parser_service() -> ParserService:
    """Provide a :class:`ParserService` (stateless; profiles and config are cached singletons)."""
    return ParserService()


@router.post(
    ApiPaths.PARSERS_PREVIEW,
    response_model=ParsedStatement,
    summary="Preview a parsed statement from raw text",
)
def preview_statement(
    body: ParsePreviewRequest,
    user_id: UUID = Depends(get_current_user_id),
    service: ParserService = Depends(get_parser_service),
) -> ParsedStatement:
    """Parse raw statement text with a versioned profile and return the structured fields.

    Nothing is persisted; this previews what the ingestion pipeline would extract, including the
    mandatory reward-parse status. An unrecognized layout returns 422.
    """
    return service.parse_text(body.bank, body.text)


@router.post(
    ApiPaths.PARSERS_PREVIEW_PDF,
    response_model=ParsedStatement,
    summary="Preview a parsed statement from an uploaded PDF",
)
async def preview_statement_pdf(
    file: UploadFile = File(...),
    bank: str | None = Form(default=None),
    name: str | None = Form(default=None),
    dob_ddmm: str | None = Form(default=None),
    card_last4: str | None = Form(default=None),
    user_id: UUID = Depends(get_current_user_id),
    service: ParserService = Depends(get_parser_service),
) -> ParsedStatement:
    """Unlock and parse an uploaded PDF statement; returns 422 if it cannot be read or matched."""
    content = await file.read()
    hints = CardholderHints(name=name, dob_ddmm=dob_ddmm, card_last4=card_last4)
    return service.parse_pdf(content, bank, hints)
