# GEMINI.md — `Katlego`'s entry point (Gemini)

You are Gemini, working with **`Katlego`** on **`Lekgotla`**. This applies whether you are
the Gemini app, the Gemini CLI, or Antigravity — all read this file automatically. You may be working
alongside other AI copilots (see [AGENTS.md](AGENTS.md) §1); coordinate only through the shared-state
files.

## Before you do anything

Read, in this order:

0. **The `## ⇄ HANDOFF` block at the top of [STATUS.md](STATUS.md).** If it says `ACTIVE`,
   another AI has handed work to you: read the handoff document it links, end to end, before
   touching a single file — then resume from its "Resume at" pointer. Do not re-plan or
   re-decide anything it records as locked; that re-derivation wastes the very budget the
   handoff exists to protect. Verify any file, function or identifier it names still exists
   before relying on it. Full rules: [docs/cross-ai-protocol.md](docs/cross-ai-protocol.md)
   § Handoffs.
1. [STATUS.md](STATUS.md) — what's happening right now and who owns which lane.
2. [AGENTS.md](AGENTS.md) — the universal contract (rules, git flow, Definition of Done).
3. [docs/cross-ai-protocol.md](docs/cross-ai-protocol.md) — how multiple AIs share state here.

Then claim a lane in STATUS.md before you start editing.

## What `Lekgotla` is

`Lekgotla resolves AI configuration bloat. It merges scattered agent instruction files (.cursorrules, CLAUDE.md, GEMINI.md, copilot-instructions.md) into one reviewable, optimized AGENTS.md, surfaces the contradictions between them for a human to resolve, and then routes each agent a minimal task-scoped context bundle drawn from the task prompt, the current-branch Git diff, and the relevant paths.`

The plan lives in [PLAN.md](PLAN.md); the WHAT in [SPEC.md](SPEC.md); the task list in [TASKS.md](TASKS.md).

## What you (Gemini) should do

**Start here: claim `lane:setup` in STATUS.md and work [TASKS.md](TASKS.md) Phase 1 (T001–T005) in
order.** Phase 1 is deliberately not feature work — the repo currently declares twelve dependencies
it never imports and ships a UI whose "sources" and token metrics are hardcoded fiction. Make it
describe itself honestly first, then Phase 2 replaces the stdlib server with FastAPI, then Phase 3
builds accounts. Do not skip ahead to Phase 3: it depends on the database and module skeleton that
Phase 2 lands.

- **Research** and summarize the existing prototype before changing it — `backend/app/compiler.py` is the real asset and its behaviour must survive every migration.
- **Scaffold** modules, write **tests first**, review diffs, write and tighten docs.
- **Propose** edits to SPEC / PLAN / TASKS via PR — the team reviews and lands them.
- Work the **same** [TASKS.md](TASKS.md) list everyone uses; one task at a time.
- Keep [STATUS.md](STATUS.md) accurate after every step.

## What you must NOT do

- **Never push directly to `main`.** Always branch and open a PR. (Pre-push hook enforces this.)
- Edit a file another lane has claimed in STATUS.md without coordinating.
- **Own a frontend lane, or restyle the UI.** Visual design, component structure, tokens,
  layout and accessibility are Claude's by default (AGENTS.md §1). Use the existing
  components freely; don't introduce a new palette, restyle a component, or hand-roll UI
  that bypasses the component layer. If you need UI to finish your lane, wire up what
  exists and flag in STATUS.md that it needs a Claude pass.
- **`Never invent a rule, a conflict, or a metric. Every directive in a compiled AGENTS.md must trace to a named source file the user actually supplied; every reported conflict must cite the two real contradicting rules; every token count must come from real measurement of real text, never an estimate presented as fact.`.** (Non-negotiable I in [PLAN.md](PLAN.md).)
- Blow any stated budgets (runtime, cost, size — see PLAN.md).

## Locked stack (do not swap without a plan change)

Python 3.12 · FastAPI · SQLAlchemy 2.x + Alembic over SQLite · Argon2id · authlib (GitHub OAuth, PKCE) · aio-pika/RabbitMQ · OpenAI Responses API · React 19 + Tailwind v4 + shadcn/ui · uv · Ruff · Pyright · pytest + pytest-bdd. Verify Node LTS before pinning (T002).
