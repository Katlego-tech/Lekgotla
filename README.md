# Lekgotla

Lekgotla resolves AI configuration bloat. It merges scattered agent instruction files into one optimized `AGENTS.md` and routes a minimal context bundle for each task.

The architecture is a Dockerized FastAPI service system with separate service databases, RabbitMQ, GitHub OAuth, and OpenAI-powered semantic compilation. The current single-process prototype is being replaced incrementally; its durable engineering constraints live in [`AGENTS.md`](./AGENTS.md).

## Run the demo

This is a dependency-free Python full-stack prototype. From this directory, you can run the server using either standard Python or the `uv` toolchain:

Using standard Python:
```bash
python3 backend/app/main.py
```

Using `uv`:
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

Alternatively, to run only the standard unit tests using Python's built-in `unittest` framework (no external dependencies required):
```bash
python3 -m unittest backend/tests/test_server.py -v
```

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
