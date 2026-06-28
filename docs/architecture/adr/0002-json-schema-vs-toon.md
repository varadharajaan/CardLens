# 0002. JSON Schema for the card registry; TOON deferred to the LLM boundary

Status: Accepted

## Context

The card feature registry needs a versioned, evolvable, validated data contract. During P7 the
question arose whether TOON (Token-Oriented Object Notation) could replace JSON Schema for that
contract. TOON is a compact serialization format whose purpose is to reduce token usage when feeding
structured data into a language model. It is strongest on uniform, tabular arrays of objects. It is
not a validation language and has no standardized, versioned schema/validation semantics equivalent to
JSON Schema Draft 2020-12.

The registry entries are nested and non-uniform (features, reward rules, milestones, lounge rules,
caps, exclusions), are consumed by the API, the frontend, and the test suite, and are edited directly
in the IDE where the `$schema` reference provides live validation.

## Decision

Keep JSON Schema (Draft 2020-12) as the registry's validation contract and keep registry entries as
JSON files. Validation is enforced at load time and at the upsert endpoint by the `jsonschema`
validator selected per the entry's declared `schema_version`.

Treat TOON as a complementary, later optimization confined to the LLM boundary. When LLM-assisted
features arrive (statement-parse assistance, community-intelligence summarization, best-card
recommendation), uniform arrays passed into a model may be encoded as TOON to cut token cost. TOON is
an encoding applied on top of JSON-Schema-validated data, never a replacement for the validation
contract or the at-rest storage format.

## Consequences

Easier: the registry keeps standard tooling (`jsonschema`, IDE validation, git-diffable JSON), a
first-class versioning story, and universal consumption by non-LLM clients. Token-efficiency gains are
still available exactly where they matter (the model boundary) without compromising the data contract.

Harder: a future TOON encoder/decoder utility must be added and tested when the first LLM feature
lands; that work is tracked on the roadmap rather than done now (no dependency added prematurely).

## Rejected Alternatives

- Replace JSON Schema with a "TOON schema": rejected. TOON has no mature, versioned validation system,
  which is the exact capability the registry requires, and it would remove live IDE validation.
- Store registry entries as TOON files: rejected. The data is nested and non-uniform, so TOON's
  compression benefit is small here, while every non-LLM consumer would need a decoder.
