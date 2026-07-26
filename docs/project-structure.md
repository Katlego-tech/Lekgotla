# Project structure

The actual directory layout and service architecture for **Lekgotla**.

## Current tree (Modular Monolith)

Lekgotla is starting as a **modular monolith** with service-shaped boundaries, designed to be split into microservices in Phase 9 (see [PLAN.md](../PLAN.md) *Architecture deviation*).

```
Lekgotla/
├── README.md                      <- human overview + quick start
├── AGENTS.md                      <- the rules (every session reads this)
├── STATUS.md                      <- LIVE board: done / in-progress / next (read first, update last)
├── CLAUDE.md / GEMINI.md          <- per-tool entry points
├── SPEC.md · PLAN.md · TASKS.md   <- the planning documents
├── docs/                          <- architecture, workflow, testing, and migration docs
├── .claude/                       <- agents, feature-dev command, frontend-design skill
├── .githooks/pre-push             <- local test gate (blocks direct pushes to main & failing tests)
├── .github/workflows/ci.yml       <- CI workflow
├── backend/                       <- Python 3.12 backend (uv-managed)
│   ├── app/
│   │   ├── identity/              <- accounts, sessions, password hashing (Argon2id), verification mail
│   │   ├── github/                <- OAuth (PKCE), repo listing, read-only fetch, PR writes
│   │   ├── compiler/              <- deterministic compiler + OpenAI Responses API semantic merge
│   │   ├── gateway/               <- FastAPI app factory, auth dependencies, browser-facing layer
│   │   ├── db/                    <- SQLAlchemy 2.x models & session factory
│   │   └── main.py                <- application entry point
│   ├── alembic/                   <- database migration scripts
│   └── tests/                     <- unit & pytest-bdd scenarios mirroring app/
├── frontend/                      <- static prototype (HTML/CSS/JS) — replaced by apps/web at Phase 5
└── apps/web/                      <- React 19 + Vite + shadcn/ui frontend (scaffolded at Phase 5)
```

## Target architecture (Phase 9 split)

In Phase 9, internal modules promote to standalone microservices communicating over RabbitMQ and HTTP:

```
services/
├── identity/       <- account verification, sessions, audit records (SQLite DB)
├── github/         <- OAuth integration, repo scanning, PR management (SQLite DB)
├── compiler/       <- deterministic compiler & OpenAI semantic merge worker (SQLite DB)
└── api_gateway/    <- browser-facing proxy, auth verification, internal token issuance

broker/             <- RabbitMQ config & versioned event contracts
docker-compose.yml  <- local development stack (services + RabbitMQ broker)
```

## Architectural choices

- **Modular Monolith First**: Monolith layout for rapid development in early phases while enforcing explicit module boundaries (no cross-module table joins).
- **Service Boundaries**: `identity`, `github`, `compiler`, `gateway`. Each service will eventually own its own database, Alembic migrations, and Docker volume.
- **Async Communication**: RabbitMQ for background tasks (e.g., GitHub webhook analysis queues) with versioned event contracts.
- **Browser Security**: Opaque server-side sessions stored in `Secure`, `HttpOnly`, `SameSite` cookies. No JWTs in local storage.

## How to run locally

```bash
# Run tests
cd backend && uv run pytest -q

# Run backend dev server
python3 backend/app/main.py
```
