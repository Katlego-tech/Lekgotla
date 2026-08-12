"""Lekgotla local API: compile AI configs into a scoped AGENTS.md manifest.

This file is the app factory and nothing else. Routes live in `app.gateway`, the merge
lives in `app.compiler`, and Phases 3 and 6 add `app.identity` and `app.github` beside
them. The module boundaries are named for the services they become at Phase 9
(PLAN.md, *Architecture deviation*) and T011 enforces the one rule that keeps that split
cheap: no module reads another module's tables.

The API contract itself has not moved since the stdlib `http.server` version --
`tests/test_api_contract.py` was written against that server and still passes untouched.
"""

from __future__ import annotations

import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# Add backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from app.gateway import JsonResponse, install_error_handlers, router

ROOT = Path(__file__).parent.parent.parent.resolve() / "frontend"
PORT = 4173


def create_app() -> FastAPI:
    """Build the ASGI app. A factory, not a module global, so tests can boot their own."""
    app = FastAPI(
        title="Lekgotla",
        description="Compile AI configs into a scoped AGENTS.md manifest.",
        default_response_class=JsonResponse,
    )
    install_error_handlers(app)
    app.include_router(router)

    # The prototype frontend is served from the same origin, as it was before, so
    # `frontend/script.js` keeps working against relative /api paths with no CORS setup.
    # Mounted last: Starlette matches routes in registration order, and this one matches
    # everything.
    app.mount("/", StaticFiles(directory=ROOT, html=True), name="frontend")

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    print(f"Lekgotla running at http://localhost:{PORT}")
    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="info")
