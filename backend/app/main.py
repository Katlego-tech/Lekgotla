"""Lekgotla local API: compile AI configs into a scoped AGENTS.md manifest.

T007 replaced the `http.server` implementation with a FastAPI app factory. The routes,
the response bodies and the status codes are unchanged -- `tests/test_api_contract.py`
was written against the old server and passes here untouched.

Validation is still hand-rolled at this stage, deliberately: T008 converts it to
Pydantic models, and doing both in one step would leave no way to tell a migration bug
from a validation bug. The one thing that must survive T008 is the *400* -- FastAPI's
default answer to a bad request body is a 422 with a Pydantic error envelope, and this
API has always answered 400 with `{"error": "..."}`.
"""

from __future__ import annotations

import json
import sys
from http import HTTPStatus
from pathlib import Path
from typing import Any, cast

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

# Add backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from app.compiler import compile_manifest, context_bundle

ROOT = Path(__file__).parent.parent.parent.resolve() / "frontend"
PORT = 4173
MAX_BODY_BYTES = 1_000_000


class JsonResponse(JSONResponse):
    """JSONResponse that keeps the old server's exact Content-Type.

    Starlette only appends `charset` to `text/*` media types, so the stock class would
    answer `application/json` where this API has always answered
    `application/json; charset=utf-8`.
    """

    media_type = "application/json; charset=utf-8"


def _error(status: HTTPStatus, message: str) -> JsonResponse:
    return JsonResponse(status_code=status, content={"error": message})


async def _read_json_object(request: Request) -> dict[str, Any] | JsonResponse:
    """Return the parsed request body, or the error response that replaces it."""
    declared = request.headers.get("content-length")
    if declared is not None and declared.isdigit() and int(declared) > MAX_BODY_BYTES:
        return _error(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, "Request body exceeds 1 MB")

    raw = await request.body()
    # A chunked request declares no length, so the limit is enforced again on what
    # actually arrived rather than on what the client claimed.
    if len(raw) > MAX_BODY_BYTES:
        return _error(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, "Request body exceeds 1 MB")

    try:
        body = json.loads(raw or b"{}")
    except (json.JSONDecodeError, ValueError):
        return _error(HTTPStatus.BAD_REQUEST, "Invalid JSON body")
    if not isinstance(body, dict):
        return _error(HTTPStatus.BAD_REQUEST, "Request body must be a JSON object")
    return cast(dict[str, Any], body)


def create_app() -> FastAPI:
    """Build the ASGI app. A factory, not a module global, so tests can boot their own."""
    app = FastAPI(
        title="Lekgotla",
        description="Compile AI configs into a scoped AGENTS.md manifest.",
        default_response_class=JsonResponse,
    )

    @app.get("/api/health")
    async def health() -> JsonResponse:
        return JsonResponse(status_code=HTTPStatus.OK, content={"status": "ok"})

    @app.post("/api/compile")
    async def compile_endpoint(request: Request) -> JsonResponse:
        body = await _read_json_object(request)
        if isinstance(body, JsonResponse):
            return body

        sources = body.get("sources")
        invalid_sources = not isinstance(sources, list) or any(
            not isinstance(item, dict)
            or not isinstance(item.get("name"), str)
            or not isinstance(item.get("content"), str)
            for item in sources
        )
        if invalid_sources:
            return _error(HTTPStatus.BAD_REQUEST, "sources must be an array of { name, content }")

        resolutions = body.get("resolutions")
        if resolutions is not None and (
            not isinstance(resolutions, dict)
            or any(not isinstance(k, str) or not isinstance(v, str) for k, v in resolutions.items())
        ):
            return _error(
                HTTPStatus.BAD_REQUEST,
                "resolutions must be a JSON object mapping keys to string values",
            )

        result = compile_manifest(cast(list[dict[str, str]], sources), resolutions)
        return JsonResponse(status_code=HTTPStatus.OK, content=result)

    @app.post("/api/context")
    async def context_endpoint(request: Request) -> JsonResponse:
        body = await _read_json_object(request)
        if isinstance(body, JsonResponse):
            return body

        manifest = body.get("manifest")
        if not isinstance(manifest, str):
            return _error(HTTPStatus.BAD_REQUEST, "manifest must be a string")
        task = body.get("task", "ui")
        if not isinstance(task, str):
            return _error(HTTPStatus.BAD_REQUEST, "task must be a string")

        return JsonResponse(status_code=HTTPStatus.OK, content=context_bundle(manifest, task))

    # Anything else under /api is a JSON 404, not the static mount's HTML one. Declared
    # before the mount because Starlette matches routes in registration order.
    @app.api_route(
        "/api/{unmatched:path}",
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"],
        include_in_schema=False,
    )
    async def unknown_api_route(unmatched: str) -> JsonResponse:
        return _error(HTTPStatus.NOT_FOUND, "Not found")

    # The prototype frontend is served from the same origin, as it was before, so
    # `frontend/script.js` keeps working against relative /api paths with no CORS setup.
    app.mount("/", StaticFiles(directory=ROOT, html=True), name="frontend")

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    print(f"Lekgotla running at http://localhost:{PORT}")
    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="info")
