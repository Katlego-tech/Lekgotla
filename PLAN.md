# `Lekgotla` — Implementation Plan (the HOW)

**Companions:** [SPEC.md](SPEC.md) (the WHAT) · [TASKS.md](TASKS.md) (the task list)

---

## Summary

Lekgotla merges scattered AI agent-instruction files into one reviewable `AGENTS.md` and routes each
agent a minimal task-scoped context bundle. What exists today is a **demo shell**: a static
`frontend/` (hand-written HTML/CSS/JS) talking to a stdlib `http.server` that wraps a 170-line
deterministic compiler. There are no accounts, no persistence, no GitHub integration, and no model
calls — the source files the UI "compiles" are a JavaScript object literal in `frontend/script.js`.

The work ahead is to turn that shell into a real product: a FastAPI backend with identity,
persistence and migrations; a React + shadcn/ui frontend that keeps the current visual identity
exactly; and the GitHub + OpenAI integrations the
[engineering manifest](docs/engineering-manifest.md) already commits to. The key technical bet is
that the **deterministic compiler stays the source of truth** and the model is only ever a
semantic-merge assistant layered on top of it — never the thing that decides what a rule says.

---

## Non-negotiables (project principles)

1. **Never invent a rule, a conflict, or a metric.** Every directive in a compiled `AGENTS.md` must
   trace to a named source file the user actually supplied; every reported conflict must cite the two
   real contradicting rules; every token count must come from real measurement of real text, never an
   estimate presented as fact. This is the grounding rule in [AGENTS.md](AGENTS.md) §6.
2. **Secrets never round-trip.** GitHub tokens and user OpenAI keys are encrypted at rest and are
   never returned by any API, logged, or included in a model payload. Sessions are opaque and
   server-side; no browser JWTs in local storage.
3. **Read-only by default.** GitHub access is read-only unless a repository is explicitly opted in,
   and writes only ever open or update a PR branch — never a direct commit. OpenAI analysis is
   off per repository until enabled.
4. **Test-first.** Each user story writes failing tests before implementation.
5. **Phased delivery.** Independent user stories; each phase ends demoable.
6. **Coordinate through shared state.** STATUS.md, AGENTS.md, and TASKS.md are the only coordination
   surfaces; one writer per task.
7. **Branch-only, always-green `main`.** No direct pushes; every change lands via PR with a green gate.

The full product/security constraint set these are distilled from is preserved verbatim in
[docs/engineering-manifest.md](docs/engineering-manifest.md).

---

## Technical Context

> Versions marked **verify** must be confirmed against the source before being pinned
> (architecture-defaults §5) — they are deliberately not guessed here.

| Dimension | Value |
| --- | --- |
| **Language(s) + versions** | Python **3.12** (confirmed: `requires-python = ">=3.12"`, `.venv` is 3.12). Node: **verify current LTS** before pinning — T002. |
| **Architecture** | **Modular monolith first, service-shaped.** One FastAPI app with hard module boundaries named for the eventual services (`identity`, `github`, `compiler`, `api_gateway`), split into real services at Phase 6. See *Architecture deviation* below. |
| **Messaging / async** | RabbitMQ (`aio-pika`, already declared). Not wired until Phase 5 — until then, in-process background tasks behind the same interface. |
| **Frontend** | React 19 + **Vite** + shadcn/ui (Radix + Tailwind v4 + CVA), **preserving the existing dark-lime identity exactly** — see [docs/frontend-shadcn-migration.md](docs/frontend-shadcn-migration.md). Vite over Next.js: Lekgotla sits entirely behind a login, so there is no SEO or SSR need to pay for, and the gateway can serve the built assets directly. |
| **Containerization** | Docker per service + one `docker-compose.yml` for local dev. Deferred to Phase 5, when there is a broker and a datastore worth composing. |
| **Runtime/deploy target** | Local dev only today (`127.0.0.1:4173`). Hosted target **undecided** — does not block Phases 1–4. |
| **Data layer** | SQLAlchemy 2.x + Alembic over SQLite (both already declared, neither used). One schema per module; no cross-module joins, so the Phase 6 split stays cheap. |
| **Key external services/models** | GitHub OAuth (Authorization Code + PKCE, via `authlib`); Resend for verification/reset mail; OpenAI Responses API for semantic merge. All three are **declared but unused** today. |
| **Testing** | pytest + pytest-bdd; Ruff (lint + format); Pyright (`standard`); `pip-audit`. Frontend test tooling **undecided** — pick with the bundler. |
| **Perf/cost goals** | Compile of a 4-file, ~3k-token config set stays interactive (<1s deterministic path). Model calls are opt-in, budget-capped, and never on the critical path for a deterministic compile. |
| **Constraints** | Repository configuration and model prompts are sensitive user data. 45-day default retention on encrypted source snapshots; 90-day retention on audit records. |
| **Scale** | Single-user local dev today. Design for tens of repositories per account, not thousands. |

### Architecture deviation — monolith first, on purpose

**Status: confirmed by Katlego, 2026-07-26.**

[docs/architecture-defaults.md](docs/architecture-defaults.md) §1 defaults to microservices; the
[engineering manifest](docs/engineering-manifest.md) already specifies four of them with a database
each. **We are deliberately starting as a modular monolith**, because standing up four services, four
databases and a broker before there is a single real user account would be pure overhead — exactly
the "small enough that service boundaries are overhead" case §1 names as a legitimate reason to
deviate.

This is a sequencing choice, not a rejection of the target. The mitigation is that the module
boundaries are drawn **now**, with the service names, and enforced by the one rule that makes a later
split cheap: **no module reads another module's tables** — they call each other through explicit
in-process interfaces that a network hop can later replace. Phase 6 promotes those modules to
services. If that rule slips, the deviation stops being safe.

---

## Project structure (target through Phase 4)

```
Lekgotla/
├── backend/
│   ├── app/
│   │   ├── identity/        accounts, sessions, password hashing, email verification
│   │   ├── github/          OAuth, repo listing, read-only fetch, PR writes
│   │   ├── compiler/        the deterministic compiler (today's compiler.py) + model merge
│   │   ├── gateway/         FastAPI routers, auth dependencies, the only browser-facing layer
│   │   ├── db/              SQLAlchemy models, session factory
│   │   └── main.py          app factory (replaces today's http.server)
│   ├── alembic/             migrations — one per schema change, no exceptions
│   └── tests/               unit + BDD, mirroring the module tree
├── frontend/                today's static prototype — replaced by apps/web at Phase 4
└── apps/web/                React + shadcn/ui (Phase 4)
```

The long-form write-up lives in [docs/project-structure.md](docs/project-structure.md); update it as
each phase lands rather than in one pass at the end.

---

## Build phases (MVP-first)

Mirrors [TASKS.md](TASKS.md). Each phase is independently demoable at its checkpoint.

1. **Setup & truth-telling** — commit the lockfile, fix the test gate, merge the manifest, delete the
   dependencies we do not use (or start using them). End state: the repo describes itself honestly.
2. **Foundational** — FastAPI app factory replaces `http.server`; SQLAlchemy + Alembic; the module
   skeleton above; existing compiler behaviour preserved under new routing, proven by the existing tests.
3. **US1 Accounts** — email/password registration, Argon2id, opaque server-side sessions, verification
   and reset mail. The first thing that makes Lekgotla multi-user rather than a demo.
4. **US2 Real sources** — file upload and persistence replace the hardcoded `sourcesData` literal; a
   compile is saved, retrievable, and belongs to an account.
5. **US3 Frontend on shadcn** — port the UI to React + shadcn/ui with the identity preserved, wired to
   real endpoints. **Claude's lane** ([AGENTS.md](AGENTS.md) §1).
6. **US4 GitHub** — OAuth connect, read-only repo scan, opt-in PR writes.
7. **US5 Model merge** — OpenAI Responses API behind the deterministic layer, opt-in and budget-capped.
8. **Hardening** — audit records, retention jobs, rate limits, encryption-at-rest verification.
9. **Split & polish** — RabbitMQ, Docker per service, the microservices promotion, docs.

---

## Testing gate

- **Test-first:** every story phase writes failing tests before implementation.
- **Gate:** the [pre-push hook](.githooks/pre-push) runs Ruff + the fast suite in every project it
  finds, and **fails if it finds nothing to run** — a gate that silently checks zero projects is the
  failure mode it exists to prevent. CI re-runs it plus format-check, Pyright, and `pip-audit`.

See [docs/testing-strategy.md](docs/testing-strategy.md).
