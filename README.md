# Lekgotla

A single-service FastAPI prototype that merges scattered AI-agent instruction files (`CLAUDE.md`, `GEMINI.md`, `.cursorrules` and the like) into one `AGENTS.md`, flags rules that contradict each other so a person can choose one, and cuts the merged file down to a smaller bundle for a given task.

## Where it stands

- **One FastAPI process** serves the three API routes below and the static `frontend/` prototype on port 4173.
- **The merge is deterministic and rule-based.** `backend/app/compiler/` matches a fixed set of rule types (package manager, test command, TypeScript, commit style, secrets policy) with regular expressions and reports a conflict when two sources disagree on one. No model is called.
- **Task bundles** are built for three fixed demo tasks (`ui`, `api`, `review`) by keeping the manifest sections that match each task's keywords.
- **Token figures are estimates, not measurements**: word count × 1.28. In the demo, the source files are hardcoded in `frontend/script.js` and the "compacted" figure is a fixed 31.8% of the total. Replacing both is tracked as T025/T026.
- **Database plumbing only.** SQLAlchemy 2.x and Alembic are wired up over SQLite, but the schema is empty, so nothing is stored yet.
- **48 tests**: 47 pytest tests (30 HTTP contract tests, 5 validation, 6 migration, 4 module-boundary, 2 compiler) plus 1 BDD scenario.

## Planned, not built

The target design splits this into separate services (identity, GitHub, compiler, gateway), each with its own database, with RabbitMQ between them, GitHub OAuth sign-in, OpenAI-powered semantic merging, and Docker per service. **None of that exists yet.** `backend/app/identity/` and `backend/app/github/` are empty modules that mark where two of those services will go, and a module-boundary test keeps the code split along those lines. The plan is in [`PLAN.md`](./PLAN.md); the engineering constraints live in [`AGENTS.md`](./AGENTS.md).

## Run the demo

The API is FastAPI on uvicorn, serving the static `frontend/` prototype from the same origin. It needs the locked dependency set, so run it through `uv`:

```bash
uv run --project backend backend/app/main.py
```

Then open `http://localhost:4173` in your browser.

## Demo path

1. Toggle source files to see the merged manifest and the (estimated) token figures update.
2. Open a conflict and select its canonical rule.
3. Copy or export the generated `AGENTS.md`.
4. Switch agent tasks to show scoped context bundles.

## API

- `GET /api/health` – service health check
- `POST /api/compile` – accepts `sources: [{ name, content }]` and optional `resolutions`; returns a manifest, token metrics, and detected conflicts.
- `POST /api/context` – accepts a `manifest` and task (`ui`, `api`, or `review`); returns a minimal task-scoped bundle.

## Testing

To run the complete test suite (both unit tests and BDD scenarios) using `uv`:
```bash
uv run --project backend pytest
```

The suite includes `tests/test_api_contract.py`, which boots the app on an ephemeral port and asserts the HTTP contract — status codes, error bodies and static serving — end to end. It is the regression net for the ongoing migration and should not be edited to make a change pass.

## Quality tooling

The target Python toolchain is `uv`, Ruff, Pyright, pytest, and pytest-bdd. CI runs formatting, linting, type checking, unit/BDD tests, and a dependency-security audit for every pull request.

You can run quality checks locally using:
```bash
# Run Ruff linting and formatting checks
uv run --project backend ruff check backend

# Run Pyright type checking
uv run --project backend pyright
```

The supplied research PDFs are intentionally ignored by Git.
