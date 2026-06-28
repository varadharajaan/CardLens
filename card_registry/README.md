# CardLens Card Registry

JSON card-feature entries, validated against a versioned JSON Schema so the registry can evolve
without breaking older entries.

## Layout

```
card_registry/
  schema/
    v1/card-feature.schema.json    JSON Schema 2020-12 contract (schema major v1)
  india/
    <bank>/<card>.json             one entry per card, declares its schema_version
```

## Versioning policy

- Every entry declares `schema_version` (the schema contract it was authored against) and `version`
  (the content revision of that specific card's data).
- Additive, optional fields are added within schema major v1. The loader tolerates unknown optional
  keys, so a newer entry still validates on an older deployment and vice versa.
- A breaking change (renamed or removed required field, changed type) introduces `schema/v2/` with a
  new schema. Existing v1 entries continue to validate against v1. Entries are migrated deliberately.
- The loader selects the schema file by the entry's declared `schema_version`.

## Adding a card

1. Create `india/<bank>/<card>.json` with `schema_version: "1"` and a unique kebab-case `key`.
2. Set `bank` to a code present in `backend/app/shared/config/data/banks.yaml`.
3. Run `scripts/load_registry.ps1` (validates against the schema and upserts into the database).
