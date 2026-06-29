"""Mailbox scan scheduler: every N hours, scan connected Gmail accounts.

The scheduler is opt-in through CARDLENS_SCHEDULER_ENABLED so tests and short-lived CLI commands do
not spawn background threads. scripts/run_scheduler_once.ps1 invokes the same job body for proof.
"""

from __future__ import annotations

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI

from app.config import settings
from app.mail.repository import MailRepository
from app.mail.service import MailService
from app.shared.database.session import session_scope
from app.shared.logging.context import get_logger

_logger = get_logger("cardlens.mail.scheduler")


def run_mail_scan_once() -> tuple[int, int]:
    """Scan all connected mailboxes once. Returns (accounts_scanned, statements_ingested)."""
    accounts = 0
    ingested = 0
    with session_scope() as db:
        repo = MailRepository(db)
        service = MailService(db)
        for user_id in repo.connected_user_ids():
            result = service.scan(user_id)
            accounts += 1
            ingested += result.statements_ingested
    _logger.info("mail.scheduler.scan_complete", accounts=accounts, statements_ingested=ingested)
    return accounts, ingested


def register_mail_scheduler(app: FastAPI) -> None:
    """Register lifecycle hooks for the 6-hour mailbox scanner when enabled."""
    if not settings.scheduler_enabled:
        return
    scheduler = BackgroundScheduler(timezone="UTC")
    scheduler.add_job(
        run_mail_scan_once,
        "interval",
        hours=settings.scan_interval_hours,
        id="gmail_pull_scan",
        replace_existing=True,
    )
    app.state.mail_scheduler = scheduler

    @app.on_event("startup")
    def _start_scheduler() -> None:
        scheduler.start()
        _logger.info("mail.scheduler.started", interval_hours=settings.scan_interval_hours)

    @app.on_event("shutdown")
    def _stop_scheduler() -> None:
        scheduler.shutdown(wait=False)
        _logger.info("mail.scheduler.stopped")