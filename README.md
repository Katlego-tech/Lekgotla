# Lekgotla

Lekgotla resolves AI configuration bloat. It merges scattered agent instruction files into one optimized `AGENTS.md` and routes a minimal context bundle for each task.

The architecture is a Dockerized FastAPI service system with separate service databases, RabbitMQ, GitHub OAuth, and OpenAI-powered semantic compilation. The current single-process prototype is being replaced incrementally; its durable engineering constraints live in [`AGENTS.md`](./AGENTS.md).

## Run the demo

This is a dependency-free Python full-stack prototype. From this directory:

```bash
python3 server.py
```

Then open `http://localhost:4173`.

## Demo path

1. Toggle source files to show context compaction updating in real time.
2. Open a conflict and select its canonical rule.
3. Copy or export the generated `AGENTS.md`.
4. Switch agent tasks to show scoped context bundles.

## API

- `GET /api/health` – service health check
- `POST /api/compile` – accepts `sources: [{ name, content }]` and optional `resolutions`; returns a manifest, token metrics, and detected conflicts.
- `POST /api/context` – accepts a `manifest` and task (`ui`, `api`, or `review`); returns a minimal task-scoped bundle.

Run the compiler tests with `python3 -m unittest -v`.

## Quality tooling

The target Python toolchain is `uv`, Ruff, Pyright, pytest, and pytest-bdd. CI runs formatting, linting, type checking, unit/BDD tests, and a dependency-security audit for every pull request.

The supplied research PDFs are intentionally ignored by Git.
