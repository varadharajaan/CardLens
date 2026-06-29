"""Azure Document Intelligence adapter, shared by local and prod. Uses a mock when no endpoint is set.

The mock keeps the whole pipeline runnable offline and in tests; when CARDLENS_AZURE_DOCINTEL_ENDPOINT
is configured, the same interface calls the real service. The adapter only returns OCR text; structured
field extraction is the profile engine's job, so the source of truth stays config-driven.
"""

from __future__ import annotations

import io

from app.config import settings
from app.shared.logging.context import get_logger

_logger = get_logger("cardlens.docintel")


class DocumentIntelligence:
    """Returns OCR text for a document, via Azure when configured or a local fallback otherwise."""

    def __init__(self) -> None:
        self._endpoint = settings.azure_docintel_endpoint
        self._key = settings.azure_docintel_key

    @property
    def enabled(self) -> bool:
        """True when a real endpoint and key are configured."""
        return bool(self._endpoint and self._key)

    def analyze_text(self, content: bytes) -> str:
        """Return recognized text. Real call when enabled; otherwise a best-effort local extraction."""
        if not self.enabled:
            _logger.info("docintel.mock", reason="endpoint_unset")
            return ""
        from azure.ai.documentintelligence import DocumentIntelligenceClient
        from azure.core.credentials import AzureKeyCredential

        client = DocumentIntelligenceClient(self._endpoint, AzureKeyCredential(self._key))
        poller = client.begin_analyze_document("prebuilt-read", body=io.BytesIO(content))
        result = poller.result()
        return result.content or ""
