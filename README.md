# CardLens

CardLens is a credit-card and bank-account intelligence platform. It reads card and bank statement
emails, unlocks and parses statement PDFs, and surfaces rewards, milestones, fees, anomalies, money
leaks, and card-feature intelligence. It is not a bill-payment app; the focus is tracking, auditing,
optimizing, and alerting.

## 1. Overview

- Connect a mailbox, scan statement emails (pull now, 6-hour scheduler, real-time later).
- Extract structured statement data including mandatory reward-point tracking.
- Match detected cards against a versioned JSON card-feature registry.
- Track milestones, detect fee/charge anomalies, and estimate reward leakage.

## 2. Architecture

Modular monolith. One FastAPI backend with strict module boundaries (router -> service ->
repository), one Next.js web client, a versioned JSON card registry, Azure as the target cloud.
See docs/architecture/overview.md.

```
[web (Next.js)] -> [FastAPI api] -> [services] -> [repositories] -> [Postgres]
                                  -> [gmail ingest] -> [pdf unlock] -> [parsers] -> [reward/anomaly]
```

## 3. Tech Stack

Backend: Python 3.13, FastAPI, SQLAlchemy 2.0, Alembic, Pydantic v2, pydantic-settings, structlog,
APScheduler, PyJWT, argon2, pypdf, pdfplumber, Azure Document Intelligence (abstracted).
Frontend: Next.js, React, TypeScript, Tailwind, shadcn/ui, framer-motion, ECharts.
Cloud: Azure (Container Apps, Postgres, Blob, Key Vault, Service Bus/Redis, Doc Intelligence,
App Insights). Full table in plan.md.

## 4. Design Decisions

- Python/FastAPI + Next.js product stack; strict-rules process gates adapted to Python (ADR-0001).
- Config-driven everything: bank names, password rules, reward values come from data files, not code.
- Versioned JSON Schema for the card registry so it can evolve without breaking older entries.
- Reward extraction is mandatory and never silently skipped.
See docs/architecture/adr/.

## 5. Layering (SOLID)

- SRP: routers translate HTTP, services hold logic, repositories persist.
- OCP: new banks/parsers/rules added via data files and interface implementations, not edits to core.
- LSP: every parser honors the BaseStatementParser contract.
- ISP: narrow module-local interfaces.
- DIP: services depend on repository and provider interfaces, not concretions.

## 6. Logging

structlog JSON, correlation id per request, ingestion/parser run ids in context, rotating files at
10 MiB under logs/local/ (app, ingestion, parser, scheduler, errors). Secrets, tokens, full card
numbers, and PDF passwords are never logged.

## 7. Run Locally

Backend:

```
./scripts/setup_local.ps1
./scripts/run_backend.ps1
```

Frontend (requires Node 20+):

```
./scripts/run_frontend.ps1
```

## 8. Scripts

setup_local, run_backend, run_frontend, run_all_tests, run_parser_tests, verify_boot, verify_logs,
scan_mailbox_pull, run_scheduler_once, seed_sample_data, generate_postman, run_newman. See scripts/.

## 9. API Documentation

OpenAPI at /openapi.json, Swagger UI at /docs, ReDoc at /redoc. Postman collection in postman/.

## 10. Future Improvements

Real-time Gmail Pub/Sub ingestion, desktop (Tauri), browser extension, mobile, live Azure deploy,
production billing. Tracked in plan.md (Out of Scope) and docs/.
