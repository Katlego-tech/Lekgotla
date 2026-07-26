# `Lekgotla` — STATUS

> Source of truth for "what's going on right now." Read first, update last. Treat updating it as
> part of "done."

_Last updated: 2026-07-26 — by Katlego (via Claude)_

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
| `setup` | — | — | **unclaimed — Gemini starts here (T001–T005)** |
| `web` | — | Claude (reserved) | not started — Phase 5, see AGENTS.md §1 |

## ⏭️ Next action

1. Gemini: claim `lane:setup`, work T001–T005 in order. Phase 1 is about making the repo describe
   itself honestly — no new features.
2. Nothing here is committed yet. The kit scaffold + plans want one commit before Phase 1 starts,
   so Gemini branches from a clean base.

## 🗓️ Timeline to `TBD`

| Phase | What | Target window | Status |
|-------|------|---------------|--------|
| Phase 0 | Cultivation kit scaffold, plans | 2026-07-26 | ✅ |
| Phase 1 | Setup & truth-telling (T001–T005) | | ⬜ |
| Phase 2 | Foundational — FastAPI, DB, modules (T006–T011) | | ⬜ |
| Phase 3 | US1 Accounts (T012–T020) | | ⬜ |
| Phase 4 | US2 Real sources (T021–T026) | | ⬜ |
| Phase 5 | US3 shadcn port (T027–T035) | | ⬜ |
| Phase 6 | US4 GitHub (T036–T040) | | ⬜ |
| Phase 7 | US5 Semantic merge (T041–T044) | | ⬜ |
| Phase 8 | Hardening (T045–T048) | | ⬜ |
| Phase 9 | Split & polish (T049–T052) | | ⬜ |

## 🧱 What's built so far

- **Deterministic compiler** — `backend/app/compiler.py`, 170 lines. Merges sources, detects
  conflicts, applies resolutions, builds task-scoped bundles. This is the real asset.
- **Stdlib HTTP server** — `backend/app/main.py`, `http.server` + `ThreadingHTTPServer` on `:4173`.
  Three routes: `/api/health`, `/api/compile`, `/api/context`. Serves `frontend/` statically.
- **Static prototype frontend** — 98 lines of HTML, 327 of JS, 10 KB of minified CSS. Wired to
  `/api/compile` and `/api/context`; everything else is hardcoded.
- **CI** — Ruff format + lint, Pyright, pytest, `pip-audit`, all scoped to `backend/`.
- **3 tests.** Two unit, one BDD scenario. They pass.
- **Cultivation kit** — AGENTS/SPEC/PLAN/TASKS/STATUS, `docs/`, `.claude/`, `.githooks/pre-push`.

## 🚧 What is NOT built (despite appearances)

- **No accounts, no sessions, no persistence, no database.** Nothing is saved anywhere.
- **No GitHub integration, no OpenAI calls, no RabbitMQ, no Docker.**
- **12 declared-but-unused dependencies** — `fastapi`, `sqlalchemy`, `alembic`, `aio-pika`,
  `argon2-cffi`, `authlib`, `cryptography`, `openai`, `uvicorn`, `pydantic-settings`,
  `opentelemetry-api`, `httpx`. Every one is in `pyproject.toml`; not one is imported. The
  dependency list describes the intended architecture, not the built one.
- **The demo's source files are fake** — `sourcesData` in `frontend/script.js` is a JS object
  literal. The dropzone accepts files but they never reach the backend.
- **The headline metrics are invented** — tokens are `words × 1.28`, and "compacted" is
  `total × 0.318`, a fixed ratio. Both violate what is now Non-negotiable I.

## 🛠️ Environment & access

- Python 3.12, `uv` 0.11.32 at `~/.local/bin/uv`. Ambient `pytest` is **not** installed — always
  `uv run`, never bare `python -m pytest`.
- Run the tests: `cd backend && uv run pytest -q` (3 pass, ~0.02s).
- Run the demo: `python3 backend/app/main.py`, then `http://localhost:4173`.
- Hooks are live: `core.hooksPath` is set to `.githooks`.
- `backend/uv.lock` exists but is **untracked** — T003.
- No git remote configured yet.

## ⚠️ Open decisions / risks

1. ~~Monolith-first vs microservices-now~~ — **decided 2026-07-26: monolith first.** Modular
   monolith with service-shaped boundaries, split at Phase 9. Deviation from architecture-defaults
   §1 is written up in PLAN.md. The mitigation is T011's boundary test — **if that rule slips, the
   deviation stops being safe**, so treat T011 as load-bearing rather than a nicety.
2. ~~Bundler for `apps/web`~~ — **decided 2026-07-26: Vite SPA.** No SEO or SSR need behind a login.
   T027 is closed; T028 is unblocked (but still gated on Phases 1–4).
3. **Hosted deploy target undecided.** Does not block Phases 1–4.
4. **Risk: the manifest's scope is much larger than the build.** Nine phases of work sit between
   today's prototype and what `docs/engineering-manifest.md` describes. Sequencing matters more than
   any individual choice in it.
5. **Risk: 3 tests is not a regression net.** T006 exists specifically to build one before the
   FastAPI migration touches the working code.

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
