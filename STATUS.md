# `Lekgotla` — STATUS

> Source of truth for "what's going on right now." Read first, update last. Treat updating it as
> part of "done."

_Last updated: 2026-10-18 — by Katlego (via Claude)_

---

## ⇄ HANDOFF: **none**

> Leave this block here even when dormant — it is the first thing every AI reads, and it only
> works as a signal if it always lives in the same spot. Set it to `ACTIVE` and fill the rows
> when handing work to another AI or another session. See
> [docs/cross-ai-protocol.md](docs/cross-ai-protocol.md) § Handoffs.

| Field | Value |
|---|---|
| Status | 🟢 **none** |
| Raised | — |
| Reason | — |
| Document | — |
| Branch | — |
| Resume at | — |
| Blocking | — |

---

## 🎯 Current focus (claim your lane here)

| Lane | Owner | AI | Status |
|------|-------|----|--------|
| `infra` | Katlego | Claude | done — kit scaffolded, hook fixed, plans written |
| `setup` | Katlego | Gemini | done — Phase 1 complete (T001–T005) |
| `api` | Katlego | Claude | **done — Phase 2 complete (T006–T011), on `feat/foundational`** |
| `web` | — | Claude (reserved) | not started — Phase 5, see AGENTS.md §1 |

> Phase 2 was Gemini's by the previous plan; Claude took it on Katlego's instruction.
> AGENTS.md §1 assigns frontend to Claude by default — it does not reserve the backend
> for anyone. Nothing was worked in parallel, so no lane was contended.

## ⏭️ Next action

1. **Open the PR for `feat/foundational`.** It stacks on `chore/kit-gate-realignment`
   (the single-source `scripts/gate.sh`), which is unmerged — land that one first or
   the base diff will read wrong.
2. Phase 3 (US1 Accounts, T012–T020) is unblocked. Start at T012/T013 — the failing
   tests, negative paths first — before any table exists.
3. Decide the two constraints T001 dropped (see *Open decisions* 6).

## 🗓️ Timeline to `TBD`

| Phase | What | Target window | Status |
|-------|------|---------------|--------|
| Phase 0 | Cultivation kit scaffold, plans | 2026-07-26 | ✅ |
| Phase 1 | Setup & truth-telling (T001–T005) | 2026-07-26 | ✅ |
| Phase 2 | Foundational — FastAPI, DB, modules (T006–T011) | 2026-08-12 | ✅ |
| Phase 3 | US1 Accounts (T012–T020) | | ⬜ |
| Phase 4 | US2 Real sources (T021–T026) | | ⬜ |
| Phase 5 | US3 shadcn port (T027–T035) | | ⬜ |
| Phase 6 | US4 GitHub (T036–T040) | | ⬜ |
| Phase 7 | US5 Semantic merge (T041–T044) | | ⬜ |
| Phase 8 | Hardening (T045–T048) | | ⬜ |
| Phase 9 | Split & polish (T049–T052) | | ⬜ |

## 🧱 What's built so far

- **Deterministic compiler** — `backend/app/compiler/compiler.py`, 170 lines. Merges sources,
  detects conflicts, applies resolutions, builds task-scoped bundles. This is the real asset.
  Phase 2 moved it into its module untouched; git records the move as a pure rename.
- **FastAPI app** — `backend/app/main.py` is an app factory; routes live in `app/gateway/`.
  Same three routes on `:4173`, same bodies, same status codes as the stdlib server it
  replaced. Serves `frontend/` from the same origin, so no CORS setup is needed.
- **Module skeleton** — `app/{identity,github,compiler,gateway,db}/`, named for the services
  they become at Phase 9. `identity` and `github` are empty and say so.
- **Pydantic contracts** — `app/gateway/schemas.py`. Request models are `extra="forbid"`;
  response models are declared too, so a field that is not on one cannot be returned. That is
  the mechanism Phase 3 relies on for "secrets never round-trip".
- **Database plumbing** — SQLAlchemy 2.x `Base` with a constraint naming convention, a cached
  engine + session factory, `PRAGMA foreign_keys=ON`, and Alembic with `render_as_batch`.
  `alembic upgrade head` runs from clean. **No tables yet** — the initial revision is empty.
- **Static prototype frontend** — 98 lines of HTML, 327 of JS, 10 KB of minified CSS. Wired to
  `/api/compile` and `/api/context`; everything else is hardcoded. Untouched by Phase 2 and
  verified working against the new server.
- **CI + gate** — one `scripts/gate.sh` run by both the pre-push hook and CI: Ruff lint +
  format, Pyright, pytest, `pip-audit`, a placeholder sweep and a secret sweep.
- **48 tests.** 30 pin the HTTP contract, 5 the validation behaviour, 6 the migrations, 4 the
  module boundaries, 3 the compiler. They pass.
- **Cultivation kit** — AGENTS/SPEC/PLAN/TASKS/STATUS, `docs/`, `.claude/`, `.githooks/pre-push`.

## 🚧 What is NOT built (despite appearances)

- **No accounts, no sessions, no rows.** There is a database *layer* and a migration history,
  but the schema is empty — nothing is saved anywhere yet. Phase 3 changes that.
- **No GitHub integration, no OpenAI calls, no RabbitMQ, no Docker.**
- **The demo's source files are fake** — `sourcesData` in `frontend/script.js` is a JS object
  literal. The dropzone accepts files but they never reach the backend.
- **The headline metrics are invented** — tokens are `words × 1.28`, and "compacted" is
  `total × 0.318`, a fixed ratio. Both violate Non-negotiable I. T025/T026.
- ~~12 declared-but-unused dependencies~~ — resolved. T004 cut the list to 7; Phase 2 put
  `fastapi`, `uvicorn`, `sqlalchemy`, `alembic`, `pydantic-settings` and `httpx` to real use.
  Only `argon2-cffi` is still declared ahead of its task (T015).

## 🛠️ Environment & access

- Python 3.12, `uv` 0.11.32 at `~/.local/bin/uv`. Ambient `pytest` is **not** installed — always
  `uv run` from `backend/`, never bare `python -m pytest`.
- Run the tests: `cd backend && uv run pytest -q` (48 pass, ~3s).
- Run the whole gate as CI does: `bash scripts/gate.sh` from the repo root.
- Run the demo: `uv run --project backend backend/app/main.py`, then `http://localhost:4173`.
  The bare `python3 backend/app/main.py` path is **gone** — it needs uvicorn now.
- Migrations: `cd backend && uv run alembic upgrade head`. The DSN comes from
  `app/settings.py` (`LEKGOTLA_DATABASE_URL`), not from `alembic.ini`.
- Hooks are live: `core.hooksPath` is set to `.githooks`.
- Remote: `git@github.com:Katlego-tech/Lekgotla.git`. `backend/uv.lock` is tracked (T003).
- **If `pip-audit` fails on a package that is not in `uv.lock`, the venv is stale rather than
  vulnerable.** `uv run` does not prune removed packages; `uv sync --all-groups` does.

## ⚠️ Open decisions / risks

1. ~~Monolith-first vs microservices-now~~ — **decided 2026-07-26: monolith first.** Modular
   monolith with service-shaped boundaries, split at Phase 9. Deviation from architecture-defaults
   §1 is written up in PLAN.md. The mitigation is T011's boundary test — **if that rule slips, the
   deviation stops being safe**, so treat T011 as load-bearing rather than a nicety.
2. ~~Bundler for `apps/web`~~ — **decided 2026-07-26: Vite SPA.** No SEO or SSR need behind a login.
   T027 is closed; T028 is unblocked (but still gated on Phases 1–4).
3. **Hosted deploy target undecided.** Does not block Phases 1–4.
4. **Risk: the manifest's scope is much larger than the build.** Nine phases of work sit between
   today's prototype and what the original engineering manifest describes. Sequencing matters more than
   any individual choice in it.
5. ~~Risk: 3 tests is not a regression net.~~ — **closed 2026-08-12.** T006 built one: 30
   contract tests written against the stdlib server, which then passed **unedited** against
   FastAPI through T007–T011. The rule going forward is that
   `backend/tests/test_api_contract.py` is not edited to make a change pass — if an
   assertion there has to move, that is a contract break and belongs in a decision, not a
   diff.
6. **Two constraints from the engineering manifest were dropped without a home, and T001
   required saying so.** Recording it now (T001 said "if one has no home, say so in
   STATUS.md"; it was ticked without this note). Both are verified absent from PLAN.md,
   SPEC.md, TASKS.md and docs/project-structure.md:
   - **Organization roles — `owner`, `admin`, `member`, `viewer`.** Not a clerical slip:
     SPEC.md US1 scopes accounts as single-user, so multi-tenancy has left the plan
     entirely. That may be correct for this cycle, but nobody recorded choosing it.
     **Blocking Phase 3** in the weak sense that T014's `users` table is cheaper to shape
     right than to migrate later. **Needs Katlego's call.**
   - **"The compiler always makes a recommendation. Save analyses by default."** A product
     rule, not a security one — the difference between *"3 conflicts, you decide"* and
     *"3 conflicts, here's what I'd pick."* The current UI does the former. Belongs in
     SPEC.md US5 if it stands.

## 🗒️ Log

- 2026-07-26 — Katlego (via Claude) — Ran `setup-project.sh` from the Cultivation kit. Scaffolded
  AGENTS/SPEC/PLAN/TASKS/STATUS, `docs/`, `.claude/`, `.githooks/pre-push`, CLAUDE.md + GEMINI.md.
- 2026-07-26 — Katlego (via Claude) — Preserved the pre-kit `AGENTS.md` (the engineering manifest,
  which the script overwrote) verbatim to `docs/engineering-manifest.md`. Merging it is T001.
- 2026-07-26 — Katlego (via Claude) — Fixed the generated pre-push hook: it scanned only root,
  `services/*` and `apps/*`, so it found **zero** projects in this repo and reported "Test gate
  passed" without running a test. Now scans `backend/`, uses `uv`, and fails when it finds nothing.
- 2026-07-26 — Katlego (via Claude) — Wrote SPEC (US1–US5), PLAN (incl. the monolith-first
  deviation), TASKS (T001–T052) and docs/frontend-shadcn-migration.md. No product code written.
- 2026-07-26 — Katlego (via Claude) — Decisions locked: **modular monolith first** (split at Phase 9,
  guarded by T011) and **Vite SPA** for `apps/web`. T027 closed.
- 2026-08-12 — Katlego (via Claude) — Completed Phase 2 (T006–T011) on `feat/foundational`.
  T006 pinned the HTTP contract against the stdlib server *first*; T007–T011 then passed it
  unedited. FastAPI app factory, Pydantic request **and** response models, the
  `identity/github/compiler/gateway/db` skeleton, SQLAlchemy + Alembic (`upgrade head` runs
  from clean, schema still empty), and the T011 boundary test — verified by introducing two
  real violations and watching it fail with file and line. Gate green: 6 checks, 48 tests.
- 2026-08-12 — Katlego (via Claude) — Two things the gate caught that are worth remembering:
  a `pip-audit` failure that was a **stale venv**, not a vulnerability (`uv run` does not
  prune packages removed from the lock — `uv sync` does), and a test fixture string shaped
  like an OpenAI key, which the secret sweep flagged correctly. Fixture renamed rather than
  the sweep loosened.
- 2026-08-12 — Katlego (via Claude) — Recorded the two manifest constraints T001 dropped
  silently (org roles; always-recommends / save-by-default). See *Open decisions* 6. Neither
  is restored yet — the first is a product-scope call.
- 2026-10-18 — Katlego (via Claude) — README rewritten to describe what is built: one FastAPI
  process, a regex-based deterministic compiler, estimated (not measured) token figures, an
  empty schema, 48 tests (47 pytest + 1 BDD scenario). The multi-service design (RabbitMQ,
  GitHub OAuth, OpenAI merge, Docker, per-service databases) moved under "Planned, not built".
  No code changed. Branch `docs/honest-readme`, stacked on `feat/foundational`.
- 2026-07-26 — Katlego (via Gemini) — Completed Phase 1 (T001–T005): committed kit scaffold on main, created feat/setup branch, merged engineering manifest into docs/project-structure.md and PLAN.md, pinned Node v24 LTS, committed uv.lock, pruned unused dependencies in pyproject.toml and uv.lock, updated pre-push hook with ruff format, pyright, and pip-audit checks.
