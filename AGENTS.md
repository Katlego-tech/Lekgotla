# AGENTS.md — the Lekgotla contract

This is the single contract every contributor follows — **human or AI, whichever tool**.
Read it before you touch anything. If a rule here conflicts with a habit, the rule wins.

Entry points funnel here: every per-tool file (e.g. [CLAUDE.md](CLAUDE.md), [GEMINI.md](GEMINI.md))
says "read AGENTS.md first." This file is the source of truth for *how we work*; the
**Non-negotiables** in [PLAN.md](PLAN.md) are the source of truth for *what cannot be compromised*.

> **New session / new tab / new AI? Do this before anything else:**
> 1. Read **[STATUS.md](STATUS.md)** — the live board: what's done, in progress, and next.
> 2. Read this file — the rules below.
> 3. Check the **lane labels** so you don't collide with someone else's work.
> 4. When you finish a meaningful step, **update STATUS.md** before you stop.

---

## 1. Team & lanes

| Person | Role | AI copilot(s) |
|--------|------|----------------|
| Katlego | Project leader — sole contributor | Claude (frontend + primary driver), Gemini (backend lanes / second opinion) |

> 📝 **Customize:** add a row per contributor. Solo project? One row, and "lanes" still matter — they're
> how *you* avoid two of your own AI sessions colliding.

We do **not** hard-partition file ownership by person; we coordinate with **lane labels** in
[STATUS.md](STATUS.md) instead (e.g. `<lane-example-1>`, `<lane-example-2>`, `docs`, `infra`). Before
working a lane, claim it in the STATUS.md "Current focus" table so nobody else — human or AI — collides
with it.

**Rule:** never edit a file another active lane owns without saying so in STATUS.md first.

### Frontend work goes to Claude

Lanes are otherwise first-come — with one standing exception. **Any lane that produces
user-facing UI is assigned to Claude by default**: visual design, component structure,
styling and token systems, layout, accessibility, and interaction.

Why this one is pinned rather than claimed: the `frontend-design` skill in `.claude/skills/`
only loads for Claude, and it is the thing that keeps UI from drifting into the templated
look. A project's visual identity also degrades fastest when it is authored by several hands
in turn — palette and spacing decisions get re-litigated per session, and the result reads as
assembled rather than designed. One owner keeps it coherent.

In practice:

- Frontend lanes (`feat/<ui-lane>`) are Claude's unless the STATUS.md focus table says otherwise.
- Other AIs may still **use** existing components and read the token file; what they should not
  do is introduce a new palette, restyle a component, or hand-roll UI that bypasses the
  component layer.
- If another AI needs UI to finish its own lane, it wires up the existing components and notes
  in STATUS.md that the styling needs a Claude pass — rather than inventing a look in passing.
- Backend, data, infra and docs lanes carry no such default; claim whichever is free.

If the project has no frontend, this section is inert — delete it.

## 2. How we plan

Planning is driven directly by the team through living documents:

- [SPEC.md](SPEC.md) — the WHAT (user stories, acceptance criteria).
- [PLAN.md](PLAN.md) — the HOW (stack, non-negotiables, code layout, build phases).
- [TASKS.md](TASKS.md) — the checkbox task list (`T001…`).
- [STATUS.md](STATUS.md) — the live board.

The full loop is in [docs/planning-workflow.md](docs/planning-workflow.md).

- **Shared state lives in exactly three places:** AGENTS.md (rules), STATUS.md (live board),
  TASKS.md (the task list). Everything else is derived. If it isn't reflected in these three, it
  didn't happen.
- **Single writer per task.** One task ID (`T0xx`) is worked by one person/AI at a time. Claim it in
  STATUS.md before you start; release it when the PR merges.

See [docs/cross-ai-protocol.md](docs/cross-ai-protocol.md) for the collision-avoidance detail.

## 3. `main` is always green

- **Branch-only.** Nobody pushes to `main`, ever. The pre-push hook rejects it.
- Enable the hooks once per clone: `git config core.hooksPath .githooks`.
- The [pre-push hook](.githooks/pre-push) runs the test gate locally; CI re-runs it on every PR.
  A red `main` blocks the whole team, so it never happens.

## 4. Branch & commit flow

- Branch names: `feat/<lane>`, `fix/<thing>`, `docs/<thing>`, `chore/<thing>`.
- Open a PR into `main`. The gate must be green. Get a quick review from another contributor.
- Commit format ties work back to a task ID: `type(lane): T0xx short description`
  (e.g. `feat(audio): T012 faster-whisper HIP transcription`).

Full detail: [docs/git-workflow.md](docs/git-workflow.md).

## 5. Update STATUS.md every step

After any meaningful step, update [STATUS.md](STATUS.md):
1. Tick / add the relevant checkbox and task ID (in [TASKS.md](TASKS.md)).
2. Update the lane's **Status** column and the phase timeline.
3. Add a dated line to the **Log** at the bottom.

Format the header line as: `_Last updated: YYYY-MM-DD — by <name> (via <tool>)_`.

If you don't update STATUS.md, the next session (human or AI) starts blind and you get conflicts.
**Treat STATUS.md as part of "done."**

## 6. Grounding & honesty rules

Lekgotla's whole value is that a developer trusts the compiled `AGENTS.md` enough to commit it. One
fabricated rule destroys that, permanently. So:

- **Never invent a rule, a conflict, or a metric.** Every directive in a compiled `AGENTS.md` must
  trace to a named source file the user actually supplied; every reported conflict must cite the two
  real contradicting rules; every token count must come from real measurement of real text, never an
  estimate presented as fact. This is **Non-negotiable I** in [PLAN.md](PLAN.md).
  > This rule indicts code that exists today: `frontend/script.js` computes tokens as
  > `words × 1.28` and "compacted" as `total × 0.318`, a fixed ratio dressed up as a result.
  > Fixing it is T025.
- **Never leak a secret.** GitHub tokens, user OpenAI keys, password hashes and session IDs are
  never returned by an API, written to a log, or included in a model payload.
- **Respect the budgets.** A deterministic compile of a typical config set (~4 files, ~3k tokens)
  stays interactive — under a second, no model call on the critical path. Model usage is opt-in,
  rate-limited and budget-capped.
- **Deterministic I/O / graceful degradation.** With the model disabled or failing, the deterministic
  compiler must still produce a complete, well-formed manifest — and the UI must say the semantic
  merge was skipped rather than presenting the degraded result as the full one.
- **Report failures honestly.** If a stage breaks or a result comes out weak, say so in STATUS.md.
  Don't paper over a broken run.

## 7. Repository map

```
Lekgotla/
├── README.md · AGENTS.md · <per-tool>.md         shared-state entry points
├── STATUS.md · STATUS.template.md                the live board + its template
├── SPEC.md · PLAN.md · TASKS.md                  the planning documents
├── docs/                                         topic docs (incl. architecture-defaults.md)
├── .claude/                                      agents, /feature-dev command, frontend-design skill
├── .githooks/pre-push                            the local test gate + main-branch protection
├── .github/workflows/ci.yml                      the CI test gate
└── <your services/apps tree + docker-compose>    see docs/project-structure.md
```

Our default build shape (microservices · Kafka/RabbitMQ · shadcn/ui · Docker · latest-LTS-pinned)
lives in [docs/architecture-defaults.md](docs/architecture-defaults.md) — with per-project deviations
recorded in [PLAN.md](PLAN.md)'s Technical Context.

## 8. Definition of Done

A task is done when **all** of these hold:
- [ ] Code + tests written; tests were written **first** and now pass.
- [ ] Lint/format clean; the app still boots/imports; the golden-path example still works.
- [ ] Runs inside any stated budgets (no new regression in latency/memory/cost).
- [ ] STATUS.md updated (checkbox + lane status + Log line); task ID referenced in the commit.
- [ ] PR opened into `main`, CI green, reviewed by another contributor, merged.
