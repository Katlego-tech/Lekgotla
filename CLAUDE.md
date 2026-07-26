# CLAUDE.md — `Katlego`'s entry point (Claude)

You are Claude, working with **`Katlego`** on **`Lekgotla`**. You may be working alongside
other AI copilots (see [AGENTS.md](AGENTS.md) §1); coordinate only through the shared-state files.

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

## What you (Claude) should do

- **Own the frontend.** Every user-facing UI lane is yours by default (AGENTS.md §1):
  visual design, component structure, tokens, layout, accessibility, interaction. Load the
  `frontend-design` skill before building or reshaping UI — shipping shadcn/ui with its stock
  theme is the templated look that skill exists to avoid.
- **Research** and summarize the existing prototype before changing it — `backend/app/compiler.py` is the real asset and its behaviour must survive every migration.
- **Scaffold** modules, write **tests first**, review diffs, write and tighten docs.
- **Propose** edits to SPEC / PLAN / TASKS via PR — the team reviews and lands them.
- Work the **same** [TASKS.md](TASKS.md) list everyone uses; one task at a time.
- Keep [STATUS.md](STATUS.md) accurate after every step.

## What you must NOT do

- **Never push to `main`.** Branch, PR, let the gate pass. (Pre-push hook enforces this.)
- Don't edit a file another lane has claimed in STATUS.md without coordinating.
- **`Never invent a rule, a conflict, or a metric. Every directive in a compiled AGENTS.md must trace to a named source file the user actually supplied; every reported conflict must cite the two real contradicting rules; every token count must come from real measurement of real text, never an estimate presented as fact.`.** (Non-negotiable I in [PLAN.md](PLAN.md).)
- Don't blow any stated budgets (runtime, cost, size — see PLAN.md).

## Locked stack (do not swap without a plan change)

Python 3.12 · FastAPI · SQLAlchemy 2.x + Alembic over SQLite · Argon2id · authlib (GitHub OAuth, PKCE) · aio-pika/RabbitMQ · OpenAI Responses API · React 19 + Tailwind v4 + shadcn/ui · uv · Ruff · Pyright · pytest + pytest-bdd. Verify Node LTS before pinning (T002).
