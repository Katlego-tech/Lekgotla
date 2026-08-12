# Lekgotla

Lekgotla resolves AI configuration bloat. It merges scattered agent instruction files into one optimized `AGENTS.md` and routes a minimal context bundle for each task.

The architecture is a Dockerized FastAPI service system with separate service databases, RabbitMQ, GitHub OAuth, and OpenAI-powered semantic compilation. The current single-process prototype is being replaced incrementally; its durable engineering constraints live in [`AGENTS.md`](./AGENTS.md).

## Run the demo

The API is FastAPI on uvicorn, serving the static `frontend/` prototype from the same origin. It needs the locked dependency set, so run it through `uv`:

```bash
uv run --project backend backend/app/main.py
```

Then open `http://localhost:4173` in your browser.

## Demo path

1. Toggle source files to show context compaction updating in real time.
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
