# `<TOOL_NAME>`.md — `<PERSON>`'s entry point (`<TOOL_NAME>`)

Copy this file to `<TOOL_NAME>.md` (the filename your tool auto-reads — check its docs; some tools
need a specific name/location) whenever a contributor uses an AI tool not already covered by
[CLAUDE.md](CLAUDE.md) or [GEMINI.md](GEMINI.md). The content is identical in shape — only the tool
name and person change. This keeps the rule from [AGENTS.md](AGENTS.md) §2 true: **the rules are
identical for every assistant, no matter which one you switch to.**

> **Tool doesn't auto-read repo files?** At the start of a session, paste this file + the current
> `STATUS.md` into it. That's all any assistant needs to participate correctly.

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

## What you (`<TOOL_NAME>`) should do

- **Research** and summarize `<source material, if any>`.
- **Scaffold** modules, write **tests first**, review diffs, write and tighten docs.
- **Propose** edits to SPEC / PLAN / TASKS via PR — the team reviews and lands them.
- Work the **same** [TASKS.md](TASKS.md) list everyone uses; one task at a time.
- Keep [STATUS.md](STATUS.md) accurate after every step.

## What you must NOT do

- **Never push directly to `main`.** Always branch and open a PR.
- Edit a file another lane has claimed in STATUS.md without coordinating.
- **Own a frontend lane, or restyle the UI.** Visual design, component structure, tokens,
  layout and accessibility are Claude's by default (AGENTS.md §1). Use the existing
  components freely; don't introduce a new palette, restyle a component, or hand-roll UI
  that bypasses the component layer. If you need UI to finish your lane, wire up what
  exists and flag in STATUS.md that it needs a Claude pass.
- **`Never invent a rule, a conflict, or a metric. Every directive in a compiled AGENTS.md must trace to a named source file the user actually supplied; every reported conflict must cite the two real contradicting rules; every token count must come from real measurement of real text, never an estimate presented as fact.`.** (Non-negotiable I in [PLAN.md](PLAN.md).)
- Blow any stated budgets (runtime, cost, size — see PLAN.md).

## Locked stack (do not swap without a plan change)

`<the real, locked technology choices — same line across every entry-point file>`
