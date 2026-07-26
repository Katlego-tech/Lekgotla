# `Lekgotla` — Specification (the WHAT)

**Related:** [PLAN.md](PLAN.md) (the HOW) · [TASKS.md](TASKS.md) (the backlog)

---

## Overview

Lekgotla is a web application for developers who run more than one AI coding agent on the same
repository. It takes the instruction files those agents read — `.cursorrules`, `CLAUDE.md`,
`GEMINI.md`, `.github/copilot-instructions.md` and friends — merges them into a single reviewable
`AGENTS.md`, surfaces the places where they contradict each other so a human can pick the canonical
rule, and then serves each agent task a minimal context bundle instead of the whole manifest.

It is called by a human through a browser. It produces a compiled `AGENTS.md`, a list of resolved and
unresolved conflicts, honest token metrics, and per-task context bundles.

### Goals

- Merge N instruction files into one manifest without inventing, dropping, or paraphrasing a rule
  away from its meaning.
- Detect contradictions between sources and make a human resolve them, remembering the resolution.
- Report real token counts, before and after.
- Persist all of the above against a user account, so work survives a page refresh.
- Read a real GitHub repository's config files, and optionally open a PR with the compiled result.

### Non-goals

- Editing or generating application code. Lekgotla only ever touches agent-instruction files.
- Being an agent runtime. It prepares context; it does not execute tasks.
- Direct commits to a user's branches. Writes are always a PR, always opt-in per repository.
- Supporting non-Git config sources (Notion, Confluence, chat history) in this cycle.

---

## Actors

### The developer (primary, human, authenticated)

Signs up, connects a repository or uploads files by hand, reviews the detected conflicts, chooses the
canonical rule for each, and exports or PRs the compiled `AGENTS.md`. They judge success on one
thing: **do they trust the output enough to commit it.** That trust is destroyed by a single
fabricated rule, which is why the grounding rule is Non-negotiable I in [PLAN.md](PLAN.md).

### The consuming agent (secondary, automated)

Any AI coding tool that reads the compiled `AGENTS.md` or requests a task-scoped bundle. It expects a
deterministic, complete, well-formed manifest. It never authenticates as itself in this cycle — it
reads a file the developer committed.

---

## User stories

### US1 — Accounts (P1)

**As a** developer, **I want** to create an account and stay signed in, **so that** my compiled
manifests and conflict resolutions are mine and persist between sessions.

**Acceptance criteria:**
- [ ] I can register with email + password; the password is hashed with Argon2id and is never stored
      or logged in plaintext.
- [ ] Registering sends a verification email; unverified accounts can sign in but cannot connect a
      GitHub repository.
- [ ] Signing in sets an opaque session ID in a `Secure`, `HttpOnly`, `SameSite` cookie. No token is
      readable from JavaScript.
- [ ] I can sign out, which invalidates the session server-side, not just in the browser.
- [ ] I can request a password reset by email and complete it with a single-use, expiring token.
- [ ] Every endpoint that touches user data rejects an unauthenticated request with 401, proven by a
      test per endpoint.

### US2 — Real sources, really saved (P1)

**As a** developer, **I want** to upload my actual config files and have the compile persist, **so
that** Lekgotla works on my repository instead of on a canned demo.

**Acceptance criteria:**
- [ ] The hardcoded `sourcesData` object in `frontend/script.js` is gone; every source shown in the
      UI came from something I supplied.
- [ ] I can upload files via the existing dropzone; contents are stored against my account.
- [ ] Token counts shown are measured from the real content, not derived from a fixed ratio.
- [ ] A compile is saved with its sources, resolutions, manifest and conflicts, and I can reopen it.
- [ ] Another signed-in user cannot read my compile by guessing its ID.

### US3 — The UI on shadcn, unchanged to look at (P2)

**As a** developer, **I want** the interface rebuilt on a real component layer, **so that** it can
grow auth, settings and repo screens without the CSS collapsing — without losing the look.

**Acceptance criteria:**
- [ ] Every screen is React + shadcn/ui; no hand-rolled markup bypassing the component layer.
- [ ] The visual identity is preserved: same palette, same three typefaces, same tight radii, same
      ambient orbs and noise. Judged by side-by-side screenshot against the current build.
- [ ] Nothing renders in stock shadcn zinc/slate.
- [ ] Keyboard focus is visible everywhere, and `prefers-reduced-motion` is respected.
- [ ] The app is usable down to mobile width.

### US4 — GitHub (P2)

**As a** developer, **I want** to connect a repository, **so that** Lekgotla reads my real config
files and can open a PR with the result.

**Acceptance criteria:**
- [ ] I connect GitHub via Authorization Code + PKCE; the token is encrypted at rest and never
      returned by any API.
- [ ] Access is read-only by default; write access is enabled per repository, explicitly.
- [ ] Writing opens or updates a **pull request branch**. A direct commit to a selected branch is
      impossible, proven by a test.
- [ ] Disconnecting deletes the stored token.

### US5 — Semantic merge (P3)

**As a** developer, **I want** the merge to understand that two differently-worded rules mean the
same thing, **so that** the manifest is genuinely deduplicated rather than concatenated.

**Acceptance criteria:**
- [ ] Model analysis is off per repository by default and requires an explicit opt-in.
- [ ] Every rule in the output still traces to a named source file — the model may merge and reword,
      never originate.
- [ ] With the model disabled or failing, the deterministic compile still produces a complete
      manifest. Degradation is graceful and stated in the UI.
- [ ] A user-provided OpenAI key is preferred; the platform key is opt-in, rate-limited and
      budget-capped.

---

## Acceptance criteria (system-level)

- [ ] No endpoint returns a secret — GitHub token, OpenAI key, password hash, or session ID — in any
      response, at any verbosity. Enforced by a test that walks every route.
- [ ] Nothing in the repository claims a capability it does not have: no unused dependency implying
      an integration that is not built, no README instruction that does not run.
- [ ] `main` is green: Ruff, Pyright, pytest, pytest-bdd and `pip-audit` all pass in CI.
- [ ] Every persistence schema change shipped with an Alembic migration.
