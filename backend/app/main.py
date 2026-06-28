"""FastAPI application factory and ASGI entry point.

Wires logging, configuration validation, middleware, error handlers, and routers. The module-level
``app`` is what uvicorn imports (``app.main:app``).
"""

from __future__ import annotations

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.auth.router import router as auth_router
from app.bank_accounts.router import debit_cards_router
from app.bank_accounts.router import router as bank_accounts_router
from app.cards.router import accounts_router as card_accounts_router
from app.cards.router import router as cards_router
from app.config import settings
from app.dashboard.router import router as dashboard_router
from app.health.router import router as health_router
from app.parsers.router import router as parsers_router
from app.registry.router import router as registry_router
from app.shared.config.data_loader import get_data_loader
from app.shared.constants.headers import HeaderNames
from app.shared.errors.handlers import register_exception_handlers
from app.shared.logging.context import get_logger
from app.shared.logging.middleware import RequestContextMiddleware
from app.shared.logging.setup import configure_logging
from app.statements.router import router as statements_router
from app.users.router import router as users_router


def create_app() -> FastAPI:
    """Build and return the configured FastAPI application."""
    configure_logging(settings)
    logger = get_logger("cardlens.app")
    get_data_loader().validate_all()

    app = FastAPI(
        title=settings.app_name,
        version=__version__,
        description="CardLens - credit-card and bank-account intelligence API.",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=[HeaderNames.REQUEST_ID],
    )
    app.add_middleware(RequestContextMiddleware)
    register_exception_handlers(app)

    app.include_router(health_router)

    api = APIRouter(prefix=settings.api_prefix)
    api.include_router(auth_router)
    api.include_router(users_router)
    api.include_router(registry_router)
    api.include_router(cards_router)
    api.include_router(card_accounts_router)
    api.include_router(bank_accounts_router)
    api.include_router(debit_cards_router)
    api.include_router(statements_router)
    api.include_router(dashboard_router)
    api.include_router(parsers_router)
    app.include_router(api)

    logger.info(
        "app.created",
        env=settings.env,
        api_prefix=settings.api_prefix,
        version=__version__,
    )
    return app


app = create_app()
