# Lekgotla engineering manifest

## Product boundary

Lekgotla compiles fragmented AI-agent configuration into a reviewable `AGENTS.md`, then creates minimal context bundles for a task, branch, and Git diff. Treat repository configuration and model prompts as sensitive user data.

## Architecture

- Build a Python 3.12+ modular service system with FastAPI.
- Service boundaries are `identity`, `github`, `compiler`, and `api_gateway`.
- Each service owns its SQLite database, Alembic migrations, and Docker volume. Never join another service's database tables.
- Use RabbitMQ for asynchronous work and versioned event contracts. Use HTTP only for request/response interactions that need an immediate answer.
- The API gateway is the only browser-facing service. It owns authorization checks and issues short-lived internal service identity claims.
- Use OpenAI's Responses API for semantic merging and explanations. Keep deterministic parsing and validation in Python as a safety layer.
- Scope dynamic context from the task prompt, current-branch Git diff, and relevant paths.

## Security

- Use opaque server-side sessions in `Secure`, `HttpOnly`, `SameSite` cookies. Do not put browser JWTs in local storage.
- Support email/password accounts, Resend verification/reset mail, and GitHub OAuth using Authorization Code + PKCE.
- Hash passwords with Argon2id. Encrypt GitHub and user-supplied OpenAI keys at rest; never return saved secrets from an API.
- GitHub access is read-only by default. Writing is explicit per repository and creates or updates a branch pull request—never a direct commit to a selected branch.
- OpenAI analysis is disabled by default per repository. Store only encrypted source snapshots, defaulting to 45-day retention.
- Keep immutable audit records for security-sensitive actions and retain them for 90 days.
- Use the platform OpenAI key only as an opt-in, rate-limited, budget-capped fallback. Prefer a user-provided key.
- Never log secrets, raw authorization headers, session IDs, full source snapshots, or unredacted model payloads.

## Product behavior

- GitHub webhook pushes on every branch queue an analysis through RabbitMQ.
- The compiler always makes a recommendation. Save analyses by default.
- Automatic PR creation/update is a repository-level opt-in and is off by default.
- Organization roles are `owner`, `admin`, `member`, and `viewer`.

## Engineering workflow

- Practice TDD: write a failing test before behavior changes.
- Use pytest and pytest-bdd for unit, integration, and executable acceptance scenarios.
- Define service HTTP/event contracts and contract-test them before relying on cross-service behavior.
- Use Ruff for linting and formatting, Pyright for type checking, Alembic for migrations, and uv for dependencies/lockfiles.
- Instrument service boundaries with OpenTelemetry structured logs, traces, and metrics.
- Every pull request must pass tests, BDD scenarios, Ruff, Pyright, and dependency-security scanning.
- Run the smallest relevant tests locally before handoff; do not claim checks passed when a required tool is unavailable.

## Conventions

- Prefer explicit types, Pydantic request/response models, and small application-service functions.
- Keep domain rules independent of FastAPI, SQLAlchemy, RabbitMQ, and OpenAI adapters.
- Return actionable errors without leaking internal implementation or secret values.
- Add a migration for every persistence schema change.
