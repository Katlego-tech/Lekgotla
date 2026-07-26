# Planning workflow

`Lekgotla` is planned with plain, self-driven documents — no external orchestrator required.
Four living documents are all you need.

> 📝 **Customize:** this describes the lightweight path (what OmniCaption used, after actively
> *removing* a heavier tool mid-project). If your project instead drives builds through a formal
> spec-lifecycle tool (e.g. GitHub's Spec-Kit / `specify` CLI, run via an AI like IBM Bob), see
> **"The heavier alternative"** below — the two are not meant to run at once.

## The planning documents

| Document | Role | Analogue |
|----------|------|----------|
| [SPEC.md](../SPEC.md) | **The WHAT** — user stories, acceptance criteria, scoring. | the requirements |
| [PLAN.md](../PLAN.md) | **The HOW** — stack, non-negotiables, code layout, build phases, test gate. | the design |
| [TASKS.md](../TASKS.md) | **The task list** — dependency-ordered `T001…`, checkbox per task. | the backlog |
| [STATUS.md](../STATUS.md) | **The live board** — who owns what right now, timeline, log. | the standup |

## The loop

1. **Agree the WHAT.** Edit [SPEC.md](../SPEC.md) — user stories + acceptance criteria. Keep it
   implementation-agnostic.
2. **Design the HOW.** Edit [PLAN.md](../PLAN.md) — stack, module layout, phases. Check it against
   the **non-negotiables** listed there before building.
3. **Break it down.** Edit [TASKS.md](../TASKS.md) — one checkbox task per unit of work, each tagged
   with its user story and marked `[P]` if parallelizable.
4. **Claim & build.** Claim a task/lane in [STATUS.md](../STATUS.md), branch, write the test first,
   implement, open a PR. One writer per task.
5. **Land & update.** Merge via a green PR, tick the task in TASKS.md, update STATUS.md.

## Who ratifies changes

There is no automated "system of record." Changes to SPEC/PLAN/TASKS land like any other change —
via a PR reviewed by another contributor. `<the project leader / decision-maker>` has the final call
on scope and the non-negotiables; everyone keeps the documents current.

---

## The heavier alternative: a formal Spec-Kit lifecycle

If the project is built with an AI whose whole workflow is spec-driven (e.g. `/speckit.constitution →
/speckit.specify → /speckit.clarify → /speckit.plan → /speckit.tasks → /speckit.implement`), let that
tool own the generated artifacts and treat SPEC.md/PLAN.md/TASKS.md in this kit as the **human-written
seed** you feed into it:

- `constitution` ← your **non-negotiables** (PLAN.md)
- `specify` ← [SPEC.template.md](../SPEC.template.md)
- `plan` ← [PLAN.template.md](../PLAN.template.md)
- `tasks` ← [TASKS.template.md](../TASKS.template.md)

The generated versions (typically under a `specs/` directory) become the system of record for
implementation; **STATUS.md and AGENTS.md stay the coordination layer regardless** — every AI still
reads them first and updates them last (see [cross-ai-protocol.md](cross-ai-protocol.md)). Only one
assistant should own the `implement` step; parallel assistants work research, scaffolding, tests, and
docs around it, never the same task simultaneously.

**Switching from heavy to light mid-project is fine** — fold the constitution's substance into PLAN.md's
Non-negotiables, delete the spec-tool's generated tree, and go back to editing SPEC/PLAN/TASKS
directly. Document the switch in STATUS.md's Log so nobody wonders where the old artifacts went.
