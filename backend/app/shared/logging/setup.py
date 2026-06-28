"""structlog + stdlib logging configuration.

A single :func:`configure_logging` call wires structlog through the standard library so that both
application loggers and third-party (uvicorn, sqlalchemy) loggers share one JSON format, one masking
pass, and one set of rotating file handlers. Per-category loggers (ingestion, parser, scheduler) write
to their own files while still propagating to the central ``app.log``.
"""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler

import structlog

from app.config import Settings
from app.shared.logging.masking import masking_processor

_CATEGORY_FILES = {
    "cardlens.ingestion": "ingestion.log",
    "cardlens.parser": "parser.log",
    "cardlens.scheduler": "scheduler.log",
}

_configured = False


def _shared_processors() -> list:
    """Processors applied to every record, whether it originates from structlog or stdlib logging."""
    return [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        masking_processor,
    ]


def _build_formatter(as_json: bool) -> structlog.stdlib.ProcessorFormatter:
    renderer = structlog.processors.JSONRenderer() if as_json else structlog.dev.ConsoleRenderer(colors=True)
    return structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=_shared_processors(),
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )


def _rotating_handler(path: str, settings: Settings, formatter: logging.Formatter, level: int) -> RotatingFileHandler:
    handler = RotatingFileHandler(
        path,
        maxBytes=settings.log_max_bytes,
        backupCount=settings.log_backup_count,
        encoding="utf-8",
    )
    handler.setFormatter(formatter)
    handler.setLevel(level)
    return handler


def configure_logging(settings: Settings) -> None:
    """Configure structlog and the stdlib root logger. Idempotent across repeated calls."""
    global _configured
    if _configured:
        return

    settings.log_dir.mkdir(parents=True, exist_ok=True)
    level = logging.getLevelName(settings.log_level.upper())
    if not isinstance(level, int):
        level = logging.INFO

    structlog.configure(
        processors=[
            *_shared_processors(),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = _build_formatter(settings.log_json)

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    console.setLevel(level)

    app_file = _rotating_handler(str(settings.log_dir / "app.log"), settings, formatter, level)
    error_file = _rotating_handler(str(settings.log_dir / "errors.log"), settings, formatter, logging.ERROR)

    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(level)
    root.addHandler(console)
    root.addHandler(app_file)
    root.addHandler(error_file)

    for logger_name, filename in _CATEGORY_FILES.items():
        category_handler = _rotating_handler(str(settings.log_dir / filename), settings, formatter, level)
        category_logger = logging.getLogger(logger_name)
        category_logger.addHandler(category_handler)
        category_logger.setLevel(level)
        category_logger.propagate = True

    # Route uvicorn through the same handlers; silence the noisy access logger duplication.
    for noisy in ("uvicorn", "uvicorn.error"):
        logging.getLogger(noisy).handlers.clear()
        logging.getLogger(noisy).propagate = True
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    _configured = True
