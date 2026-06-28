# Card Registry Schema

The card registry is the source of truth for per-card features: fees, reward rules, milestones,
caps, exclusions, lounge access, forex markup, fuel-surcharge waivers, benefits, and redemption
values. Entries are JSON files validated against a versioned JSON Schema.

## Layout

```
card_registry/
  schema/
    v1/card-feature.schema.json     versioned contract (Draft 2020-12)
  india/
    <bank>/<card>.json              one validated entry per card
  README.md
```

Each entry declares the schema version it was authored against:

```json
{
  "schema_version": "1",
  "key": "axis-magnus",
  "bank": "AXIS",
  "card_name": "Axis Bank Magnus Credit Card",
  "network": "MASTERCARD",
  "version": 1,
  "source_confidence": 0.8,
  "last_verified_at": "2026-01-15",
  "features": { "annual_fee": 12500 }
}
```

## Versioning and evolution policy

The schema is versioned by directory (`schema/v1`, `schema/v2`, ...). The rules:

1. Additive, backward-compatible changes (new optional fields) stay within the current major version.
   The `features` object sets `additionalProperties: true`, so new optional feature keys validate
   immediately without a schema bump.
2. Breaking changes (a new required field, a removed field, a tightened type or enum) introduce a new
   schema directory (`schema/v2`) with `schema_version` const bumped to `"2"`. Existing `v1` entries
   keep validating against `v1`; they are not retroactively invalidated.
3. The loader selects the validator by the entry's declared `schema_version`, so multiple versions
   validate side by side during a migration window.
4. `version` (integer) is the per-entry content version. Bump it whenever a card's data changes; it is
   independent of `schema_version`.

## Validation points

- Load time: `RegistryLoader.load_files()` validates every file before it is upserted (used by the
  seed script). A malformed committed file fails loudly.
- API time: `POST /api/v1/registry/cards` validates the payload against the schema for its declared
  version. A schema violation returns RFC 7807 `422` with `errorCode = VALIDATION_FAILED`, never a 500.

## Matching

Detected cards are matched to registry entries by `POST /api/v1/registry/cards/match`. Scoring: an
exact bank-code match contributes half the score; the fraction of query card-name tokens found in the
candidate contributes the other half. A match at or above 0.5 is returned as `matched: true`.

## Seeding

```
scripts/seed_registry.ps1
```

Applies migrations, then loads and upserts every registry file (idempotent by `key`).

## Relationship to TOON

JSON Schema is the validation contract and JSON is the at-rest format. TOON is not used for the
registry; it is reserved for a future encoding optimization at the LLM boundary only. See
docs/architecture/adr/0002-json-schema-vs-toon.md.
