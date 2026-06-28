# 0001. Stack selection and Java-rule adaptation

Status: Accepted

## Context

Two source documents govern this build. CardLens_autonomous_build_prompt.md specifies the product and
mandates a Python/FastAPI backend with a Next.js frontend on Azure. agent-strict-rules-prompts.md is a
generic, strict engineering ruleset written for Java/Spring Boot services (Maven, Lombok, MapStruct,
ArchUnit, JPA, Flyway, Spring profiles). The two disagree on technology stack. A single coherent
decision is required before any code is written.

## Decision

Build the product on the stack the product prompt mandates: Python 3.13, FastAPI, SQLAlchemy 2.0,
Alembic, Pydantic v2, structlog, and a Next.js web client. Adopt the strict-rules file only for its
stack-agnostic process and quality gates, translating each Java mechanism to its Python equivalent:

| Java rule mechanism      | Python equivalent adopted          |
|--------------------------|------------------------------------|
| Maven wrapper            | uv + requirements.txt              |
| Lombok / immutable DTOs  | Pydantic v2 models                 |
| MapStruct                | Pydantic model_validate / mappers  |
| ArchUnit                 | import-linter contracts            |
| JPA + Flyway             | SQLAlchemy 2.0 + Alembic           |
| Spring profiles          | pydantic-settings env config       |
| SLF4J + Logback          | structlog JSON + rotating handler  |
| springdoc + Postman      | FastAPI OpenAPI + Postman + Newman |

The process gates kept in force: tracking files (plan, checkpoint, memory, todo), ASCII-only output,
SOLID and clean layering, centralized structured logging, RFC 7807 errors, DTO/entity separation,
Conventional Commits with per-phase branches and PRs, the Postman+Newman pre-push gate, and gitignore
of meta files.

## Consequences

Easier: the product matches its intended ecosystem; contributors use idiomatic Python tooling; every
quality gate still has an enforcing mechanism (the meta-enforceability rule holds).

Harder: rule references in the strict-rules file that name Java tools must be mentally mapped to the
table above. The mapping is recorded in memory.md (override O1) so the translation is explicit, not
implicit.

## Rejected Alternatives

- Build in Java/Spring Boot to match the ruleset verbatim: rejected because it contradicts the explicit
  product stack and would ship a product the prompt did not ask for.
- Drop the strict-rules gates entirely and follow only the product prompt: rejected because the gates
  encode the user's durable engineering standards and are stack-agnostic in intent.
