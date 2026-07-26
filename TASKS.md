# `Lekgotla` — Tasks

**Plan:** [PLAN.md](PLAN.md) · **Spec:** [SPEC.md](SPEC.md)

> One of the three shared-state files (with [AGENTS.md](AGENTS.md) and [STATUS.md](STATUS.md)).
> **One writer per task** — claim it in STATUS.md before you start.

## Legend

Format: `[ID] [P?] [Story] Description`

- **[ID]** — task identifier `Tnnn`, monotonically increasing, never reused.
- **[P]** — parallelizable: touches different files from its siblings and has no unmet dependency.
- **[Story]** — `US1`–`US5`, `SET` setup, `FND` foundational, `POL` polish.
- Commit format: `feat(scope): Tnnn short description`.

Each user-story phase is ordered **Tests FIRST (must FAIL) → Implementation → Checkpoint**.

**Lane ownership:** Phase 5 (`lane:web`) is Claude's by default — see [AGENTS.md](AGENTS.md) §1.
Everything else is unclaimed; Gemini should work top-down from Phase 1.

---

## Phase 1 — Setup & truth-telling

The repo currently claims things that are not true. Fix that before building on it.

- [x] T001 [SET] Merge [docs/engineering-manifest.md](docs/engineering-manifest.md) into its proper
      homes: security/product constraints → PLAN.md Non-negotiables (already drafted, verify nothing
      was dropped); architecture detail → docs/project-structure.md. Then delete the preserved file.
      **Do not silently drop a constraint** — if one has no home, say so in STATUS.md.
- [x] T002 [P] [SET] Verify and pin exact versions (architecture-defaults §5). Python is confirmed
      3.12; confirm the current Node LTS **against the source**, do not assume. Record both in
      PLAN.md's Technical Context.
- [x] T003 [P] [SET] Commit `backend/uv.lock`. It exists on disk but is untracked, so the pinned
      dependency set is not reproducible for anyone else.
- [x] T004 [SET] Resolve the 12 declared-but-unused dependencies (`fastapi`, `sqlalchemy`, `alembic`,
      `aio-pika`, `argon2-cffi`, `authlib`, `cryptography`, `openai`, `uvicorn`, `pydantic-settings`,
      `opentelemetry-api`, `httpx`). Each is either used by end of Phase 3 or removed from
      `pyproject.toml` now. A dependency list that implies integrations we have not built is exactly
      the "claims a capability it does not have" failure in SPEC.md.
- [x] T005 [SET] Add `ruff format --check`, `pyright` and `pip-audit` to the pre-push hook, or record
      in PLAN.md why they are CI-only. The hook currently runs Ruff + pytest only.

**Checkpoint:** the repo describes itself honestly. CI green, hook green, no unused declarations.

---

## Phase 2 — Foundational (blocking)

Everything below depends on this. Do not start Phase 3 until the checkpoint holds.

- [ ] T006 [FND] Write failing tests asserting the existing `/api/health`, `/api/compile` and
      `/api/context` contracts — **against the current stdlib server**, before replacing it. These
      are the regression net for the whole migration. Include the existing 400-path validations.
- [ ] T007 [FND] Replace `backend/app/main.py`'s `http.server` with a FastAPI app factory + uvicorn.
      Same three routes, same request/response shapes, same status codes. T006 must pass unchanged.
- [ ] T008 [FND] Convert the hand-rolled validation in `main.py` to Pydantic request/response models.
      The error bodies stay actionable and leak nothing.
- [ ] T009 [FND] Create the module skeleton from PLAN.md: `app/identity/`, `app/github/`,
      `app/compiler/`, `app/gateway/`, `app/db/`. Move today's `compiler.py` into `app/compiler/`
      untouched — a pure move, no behaviour change, tests still pass.
- [ ] T010 [FND] Wire SQLAlchemy 2.x + a session factory + Alembic. Ship the initial empty migration
      and prove `alembic upgrade head` runs from clean.
- [ ] T011 [FND] Add the module-boundary test: no module imports another module's ORM models. This is
      the single rule that keeps the Phase 9 service split cheap (PLAN.md, *Architecture deviation*).

**Checkpoint:** the app boots on FastAPI, the frontend still works untouched against it, migrations
run, and the boundary test passes.

---

## Phase 3 — US1 Accounts

The thing that turns a demo into a product. Acceptance criteria in [SPEC.md](SPEC.md) §US1.

- [ ] T012 [US1] Write failing tests: register, verify, sign in, sign out, reset. Cover the negative
      paths first — wrong password, unverified account, reused reset token, expired session.
- [ ] T013 [US1] Write the failing test that every data endpoint returns 401 unauthenticated. Add a
      route-walking test so a new unprotected endpoint fails the suite automatically.
- [ ] T014 [US1] `users` and `sessions` tables + Alembic migration. Sessions are opaque server-side
      records; the cookie carries an ID and nothing else.
- [ ] T015 [US1] Argon2id password hashing via `argon2-cffi`. Never log the password or the hash.
- [ ] T016 [US1] Registration + sign-in + sign-out endpoints, issuing the `Secure`, `HttpOnly`,
      `SameSite` cookie. No JWT reaches the browser.
- [ ] T017 [US1] FastAPI auth dependency; apply it to `/api/compile` and `/api/context`.
- [ ] T018 [P] [US1] Resend integration for verification and reset mail, behind an interface with a
      console-logging fake for local dev, so no test or dev run sends real mail.
- [ ] T019 [P] [US1] Password reset: single-use, expiring tokens.
- [ ] T020 [US1] Audit records for register / sign-in / sign-out / reset. Immutable, 90-day retention
      (manifest constraint). No secrets, no session IDs in the record.

**Checkpoint:** a real account can register, verify by mail, sign in, compile, sign out — and the
compile is rejected when signed out.

---

## Phase 4 — US2 Real sources, really saved

- [ ] T021 [US2] Write failing tests for source upload, persistence, retrieval, and the
      cross-account isolation case (user B cannot read user A's compile by ID).
- [ ] T022 [US2] `sources`, `compiles`, `resolutions` tables + migration, all owned by a user.
- [ ] T023 [US2] Upload endpoint accepting the dropzone's files. Enforce the existing 1 MB limit and
      a sane per-account quota.
- [ ] T024 [US2] Persist compiles with sources, resolutions, manifest and conflicts; add list and
      fetch-by-ID endpoints, scoped to the owner.
- [ ] T025 [US2] Replace estimated token counts with real measurement. The current frontend multiplies
      word count by 1.28 and the compacted figure by a fixed 0.318 — both are invented numbers and
      both violate Non-negotiable I.
- [ ] T026 [US2] Delete the `sourcesData` literal from `frontend/script.js` and point the existing
      prototype at the real endpoints. Keep the prototype working — Phase 5 replaces it, and until
      then it is the only way to demo.

**Checkpoint:** upload your own four config files, compile, refresh the page, and the compile is
still there.

---

## Phase 5 — US3 The UI on shadcn (`lane:web` — **Claude's lane**, AGENTS.md §1)

Full brief, including the extracted token system: [docs/frontend-shadcn-migration.md](docs/frontend-shadcn-migration.md).

- [x] T027 [US3] ~~Decide the bundler.~~ **Decided 2026-07-26: Vite SPA**, recorded in PLAN.md.
      Lekgotla is entirely behind a login, so there is no SEO/SSR need; the gateway serves the build.
- [ ] T028 [US3] Scaffold `apps/web` with React 19 + Vite + Tailwind v4 + shadcn/ui. Add it to the
      pre-push hook's scan and to CI.
- [ ] T029 [US3] Port the token system from the migration doc into `tailwind.config` / CSS variables
      **before** installing a single component. The 76 hardcoded hex values in today's `style.css`
      get resolved into a real scale here, not copy-pasted forward.
- [ ] T030 [US3] Port the shell: nav, hero, ambient orbs, noise overlay, footer.
- [ ] T031 [P] [US3] Port the three workspace panels: sources, resolution engine, manifest output.
- [ ] T032 [P] [US3] Port the routing section and task tabs.
- [ ] T033 [US3] Build the auth screens US1 needs — sign in, register, verify, reset. These have no
      current design; they are new work in the established language.
- [ ] T034 [US3] Accessibility and responsive pass: visible focus, `prefers-reduced-motion`, mobile
      width. Screenshot diff against the current build.
- [ ] T035 [US3] Delete `frontend/` once `apps/web` is at parity, and update README's run instructions.

**Checkpoint:** side-by-side screenshots are near-indistinguishable, and the app is signed-in real.

---

## Phase 6 — US4 GitHub

- [ ] T036 [US4] Failing tests, including the one that proves a direct commit to a selected branch is
      impossible.
- [ ] T037 [US4] Encrypted-at-rest secret storage via `cryptography`, with a test that no API
      response and no log line ever contains a stored token.
- [ ] T038 [US4] GitHub OAuth (Authorization Code + PKCE) via `authlib`; connect and disconnect flows.
- [ ] T039 [US4] Read-only repo listing and config-file discovery.
- [ ] T040 [US4] Per-repository write opt-in; PR branch create/update only.

**Checkpoint:** connect a real repo, compile its real config files, open a real PR.

---

## Phase 7 — US5 Semantic merge

- [ ] T041 [US5] Failing tests: model disabled by default; deterministic compile still complete when
      the model fails; every output rule traces to a named source.
- [ ] T042 [US5] OpenAI Responses API adapter behind the deterministic layer, per-repo opt-in.
- [ ] T043 [US5] User-provided key preferred; platform key opt-in, rate-limited, budget-capped.
- [ ] T044 [US5] Encrypted source snapshots with 45-day default retention.

**Checkpoint:** semantic merge measurably improves a real config set, and turning it off changes
nothing about correctness.

---

## Phase 8 — Hardening

- [ ] T045 [POL] Retention jobs for snapshots (45d) and audit records (90d).
- [ ] T046 [P] [POL] Rate limits on auth and model endpoints.
- [ ] T047 [P] [POL] OpenTelemetry at service boundaries; assert no secret reaches a span or log.
- [ ] T048 [POL] The system-level test from SPEC.md: walk every route, assert no secret in any response.

---

## Phase 9 — Split & polish

- [ ] T049 [POL] RabbitMQ via `aio-pika` with versioned event contracts; contract tests first.
- [ ] T050 [POL] Dockerfile per module + root `docker-compose.yml`.
- [ ] T051 [POL] Promote the modules to services — only if the boundary test (T011) has held.
- [ ] T052 [POL] Final docs pass: README, project-structure, architecture-defaults deviations.
