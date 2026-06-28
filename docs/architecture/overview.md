# CardLens - Architecture Overview

CardLens is a modular monolith with a decoupled, event-driven ingestion pipeline. One FastAPI
backend owns the synchronous API and the domain; a separate worker owns asynchronous statement
processing. The two halves are joined only by an object store and a blob-created event, so they
scale and fail independently. The same code runs locally and in Azure - only adapter configuration
changes (Local Environment Parity).

## 1. Containers

![CardLens system architecture - containers](architecture.svg)

## 2. Module boundaries

The backend is a modular monolith. Each feature module is a vertical slice with a strict internal
layering enforced by import-linter:

```
router  ->  service  ->  repository  ->  models
   |            |
   +-> schemas (Pydantic DTOs)   (entities never leave the service layer)
```

Modules: `auth`, `users`, `cards` (owns `CardAccount` + `Card` variants), `statements`,
`bank_accounts` (owns `BankAccount` + `DebitCard` variants), `registry`, `rewards`, `milestones`,
`anomalies`, `gmail`, `ingestion` (uploader + worker), `pdf`, `parsers`, `documents`,
`notifications`. The `shared` kernel holds config, logging, database, errors, pagination, and
security and never imports a feature module.

Layering rules (SOLID): routers translate HTTP only; services hold business logic; repositories
persist and always filter by the authenticated `user_id`; new banks/parsers/rules are added via data
files and interface implementations (open/closed), not edits to core workflows.

## 3. Ingestion: two decoupled workflows

![CardLens ingestion - two decoupled workflows](ingestion-flow.svg)

- Workflow A (uploader, dumb): triggered by a mailbox scan. Extracts every attachment (1..n) from a
  statement mail and uploads each PDF to Blob, deduplicated by content hash. It records attachment
  metadata. It does not parse and does not enqueue.
- Blob-to-queue bridge: in prod, Event Grid emits `BlobCreated` to Service Bus. Locally there is no
  Event Grid, so the bridge is a helper script / poller that publishes an Event-Grid-shaped message
  to the Azurite queue. The uploader never enqueues directly, keeping the local design identical to
  prod. The same helper is the manual fallback: if the mail connector is down, drop a PDF into Blob
  and run the helper to enqueue it.
- Workflow B (worker, smart): consumes the queue, decides which file to process, downloads the PDF,
  unlocks it using the config-driven password rules, extracts text (local first, Document
  Intelligence fallback), runs the versioned parser profile, performs mandatory reward extraction,
  and persists the result. Idempotent by content hash.

## 4. Ports, adapters, and environment parity

Storage, queue, and document-intelligence access go through ports with config-selected adapters.
Azurite speaks the real Azure Blob and Queue protocol, so the same Azure SDK code runs locally and in
the cloud; only the connection string or account URL changes.

| Concern | Local (no cloud) | Prod (Azure) |
|---|---|---|
| Object store | Azurite Blob | Azure Blob |
| Queue | Azurite Queue | Service Bus |
| Blob to queue bridge | helper script / poller | Event Grid BlobCreated |
| Worker | local process | Container Apps (scale-to-zero) |
| Document Intelligence | shared Azure resource | shared Azure resource |
| Auth to storage | dev connection string | Managed Identity / az login |
| Secrets | .env (gitignored) | Key Vault |
| Database | SQLite (dev) / Postgres (docker) | Azure Database for PostgreSQL |

To point local at real Azure Blob, set `CARDLENS_AZURE_BLOB_ACCOUNT_URL` (with `az login` / Managed
Identity) or `CARDLENS_AZURE_BLOB_CONNECTION_STRING`; no code change.

## 5. Domain model highlights

- CardAccount (companion/variant cards): an issuer billing account that owns multiple `Card` network
  variants. The variants share one statement date, one due amount, and one payment (settling one
  settles the account), but each variant has its own features and reward format. Statements attach
  to the account, so dashboards aggregate dues by account and never double-count a variant.
- BankAccount + DebitCard: a bank account owns multiple debit-card variants the same way, each with
  its own features.
- Statement: carries billing fields plus mandatory reward-extraction fields - `reward_parse_status`
  (FOUND / PARTIAL / NOT_FOUND), confidence, reason, evidence snippet, and a manual-review flag - so
  reward outcomes are never silently dropped.
- Registry: a versioned JSON Schema (Draft 2020-12) for card features; a detected card is matched to
  a registry entry by bank + name tokens.

## 6. Parser profiles and format evolution

Each bank parser is a versioned, config-driven profile (`parser_profiles/<bank>/vN.yaml`: anchors,
regex, field map). A generic engine selects the profile by bank and a layout fingerprint. When a
real statement does not match an assumed layout, the statement is flagged low-confidence and routed
to manual review (never silently wrong); the fix is a new profile version (data), not a code change.
Only a genuinely new extraction technique adds a small strategy class (open/closed). Azure Document
Intelligence is the fallback when local extraction is insufficient.

## 7. Security and isolation

OAuth-only mailbox access; refresh tokens encrypted at rest; per-user data isolation enforced at the
repository layer; card numbers stored as last 4 only; PII, tokens, and PDF passwords masked and never
logged; raw PDFs deleted after extraction unless the opt-in document vault is enabled. Production
secrets live in Key Vault; local secrets in a gitignored `.env`. mTLS secures internal hops
(backend-worker) and self-hosted datastores; Azure PaaS uses Managed Identity.

## 8. Observability

structlog JSON logs with a correlation id per request and ingestion/parser run ids in context;
rotating files at 10 MiB under `logs/local/`; Azure Application Insights in the cloud. The API
contract is verified by a Postman collection run with Newman against a live server before every push.

## References

- ADRs: docs/architecture/adr/
- Card registry schema: docs/card_registry_schema.md
- Rendered diagram: docs/architecture/architecture.svg
- Roadmap and domain detail: plan.md
