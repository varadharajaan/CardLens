# CardLens Postman Collection

Executable API contract for CardLens. The collection is the runnable proof of the API, exercised
by Newman against a live server. Because this project runs NO GitHub CI (no Actions quota), the
local Newman run is the ONLY gate and is mandatory before every push that touches an HTTP surface.

## One-click import

1. Import `cardlens.postman_collection.json`. Folders: Health, Auth, Users, Registry, Error Scenarios.
2. Import the environment you need: `cardlens.postman_environment_local.json` (or staging / prod).
3. Select the environment, then Run the collection top to bottom. The Auth folder runs first and
   auto-populates `access_token` / `refresh_token`; later folders depend on those variables.

No manual edits are needed after import: Register generates a fresh unique user per run.

## Run with Newman (the gate)

```
# Boots uvicorn on an isolated DB, runs the collection live, tears down:
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke.ps1

# Or against an already-running server (default http://localhost:8000):
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\run_newman.ps1 -Environment local
```

`scripts/run_newman.ps1` runs with `--bail` and writes `logs/local/newman-results.xml` (JUnit).

## Environment variables

| Variable                 | Purpose                                  | local | staging | prod |
|--------------------------|------------------------------------------|-------|---------|------|
| base_url                 | API base URL                             | yes   | yes     | yes  |
| user_password            | bootstrap test credential                | yes   | no      | no   |
| user_email               | generated per run (Register pre-request) | yes   | yes     | yes  |
| access_token             | set by Register/Login/Refresh            | yes   | yes     | yes  |
| refresh_token            | set by Register/Login/Refresh            | yes   | yes     | yes  |
| consumed_refresh_token   | captured before Refresh; replay test     | yes   | yes     | yes  |
| reg_key                  | unique registry key per run              | yes   | yes     | yes  |
| reg_card_name            | unique card name per run                 | yes   | yes     | yes  |
| request_id               | fresh GUID per request (X-Request-Id)    | yes   | yes     | yes  |

Per PART 26.6: token vars are declared (empty) in all three env files; the bootstrap credential
`user_password` lives in local only. Operators fill staging/prod values at run time.

## Current request matrix

| Folder          | Request                              | Proves                                               |
|-----------------|--------------------------------------|------------------------------------------------------|
| Health          | Liveness (healthz)                   | 200, status=ok, version present                      |
| Health          | Readiness (readyz)                   | 200, status=ready, database=up                       |
| Auth            | Register                             | 201, bearer, tokens issued, user.email matches       |
| Auth            | Login                                | 200, access token issued                             |
| Auth            | Refresh Token                        | 200, rotated access token; captures consumed token   |
| Auth            | Logout                               | 204                                                  |
| Users           | Get Me                               | 200, email matches the registered user               |
| Registry        | Upsert Card                          | 201, returned key matches                             |
| Registry        | List Cards                           | 200, items array, total >= 1, pagination params      |
| Registry        | Get Card By Key                      | 200, bank=HDFC, key matches                           |
| Registry        | Match Card                           | 200, matched=true, key matches the upserted card     |
| Cards           | Add Card                             | 201, bank, is_primary defaults to false               |
| Cards           | List Cards                           | 200, items array, total >= 1                          |
| Cards           | Get Card                             | 200, id matches the created card                      |
| Card Accounts   | Create Account                       | 201, captures the companion billing account id        |
| Card Accounts   | Add Variant - Mastercard (primary)   | 201, is_primary true                                  |
| Card Accounts   | Add Variant - RuPay                  | 201                                                   |
| Card Accounts   | Get Account With Variants            | 200, 2 variants, primary first (companion grouping)   |
| Card Accounts   | List Accounts                        | 200, items array, total >= 1                          |
| Statements      | Record Statement                     | 201, reward_parse_status FOUND, captures statement id |
| Statements      | Get Statement                        | 200, total_due matches                                |
| Statements      | List Statements                      | 200, items array                                      |
| Bank Accounts   | Create Account                       | 201, captures the bank account id                     |
| Bank Accounts   | Add Debit Card - Visa (primary)      | 201, is_primary true                                  |
| Bank Accounts   | Add Debit Card - RuPay               | 201                                                   |
| Bank Accounts   | Get Account With Debit Cards         | 200, 2 debit cards, primary first (variant grouping)  |
| Bank Accounts   | List Accounts                        | 200, items array, total >= 1                          |
| Debit Cards     | List Debit Cards                     | 200, items array, total >= 2                          |
| Dashboard       | Overview                             | 200, counts, billing groups, dues aggregated by group |
| Dashboard       | Rewards Summary                      | 200, totals plus per-format breakdown                 |
| Dashboard       | Milestones                           | 200, progress toward configured thresholds            |
| Dashboard       | Anomalies                            | 200, rule-based anomaly list                          |
| Error Scenarios | Get Me - no token (401)              | 401, errorCode=UNAUTHENTICATED                        |
| Error Scenarios | Get Me - tampered token (401)        | 401, errorCode=UNAUTHENTICATED                        |
| Error Scenarios | Get Card - unknown key (404)         | 404, errorCode=NOT_FOUND                              |
| Error Scenarios | Register - invalid input (422)       | 422, errorCode=VALIDATION_FAILED, violations array    |
| Error Scenarios | Upsert Card - no token (401)         | 401, errorCode=UNAUTHENTICATED                        |
| Error Scenarios | Upsert Card - bad network (422)      | 422, errorCode=VALIDATION_FAILED                      |
| Error Scenarios | Refresh - replay consumed token (401)| 401, single-use refresh token replay rejected         |

Collection-level tests assert every response echoes `X-Request-Id` and responds under 3000 ms
(argon2 password hashing dominates auth-endpoint latency, so the threshold is intentionally above
the 500 ms target in PART 25.8).

## Chain semantics

The Auth folder runs first and populates `access_token` / `refresh_token`; Users and Registry
folders depend on them. `newman run --bail` is used so an early failure stops the run with a clear
signal. Run the whole collection in order; do not run individual later requests in isolation.
