"""Lekgotla local API: compile AI configs into a scoped AGENTS.md manifest.

T007 replaced the `http.server` implementation with a FastAPI app factory; T008 moved
validation onto Pydantic models (`app/schemas.py`). The routes, the response bodies and
the status codes are unchanged throughout -- `tests/test_api_contract.py` was written
against the original stdlib server and still passes untouched.

The one thing that had to be built by hand is the error envelope. FastAPI answers a bad
request body with a 422 and a Pydantic error list; this API has always answered 400 with
`{"error": "<a sentence>"}`, and the frontend reads that shape. `_validation_error`
below is the translation, and it is deliberately the only place the two vocabularies
meet.
"""

from __future__ import annotations

import re
import sys
from collections.abc import Callable, Coroutine
from http import HTTPStatus
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from fastapi.staticfiles import StaticFiles

# Add backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from app.compiler import compile_manifest, context_bundle
from app.schemas import (
    CompileRequest,
    CompileResponse,
    ContextRequest,
    ContextResponse,
    Error,
    Health,
)

ROOT = Path(__file__).parent.parent.parent.resolve() / "frontend"
PORT = 4173
MAX_BODY_BYTES = 1_000_000

# Which field failed -> what the client has always been told. Keyed on the first
# segment of the Pydantic error location under "body".
FIELD_ERRORS = {
    "sources": "sources must be an array of { name, content }",
    "resolutions": "resolutions must be a JSON object mapping keys to string values",
    "manifest": "manifest must be a string",
    "task": "task must be a string",
}

ERROR_RESPONSES: dict[int | str, dict[str, Any]] = {
    400: {"model": Error, "description": "The request body is malformed."},
    413: {"model": Error, "description": "The request body exceeds 1 MB."},
}


class JsonResponse(JSONResponse):
    """JSONResponse that keeps the old server's exact Content-Type.

    Starlette only appends `charset` to `text/*` media types, so the stock class would
    answer `application/json` where this API has always answered
    `application/json; charset=utf-8`.
    """

    media_type = "application/json; charset=utf-8"


def _error(status: HTTPStatus, message: str) -> JsonResponse:
    return JsonResponse(status_code=status, content={"error": message})


def _safe_field_name(value: object) -> str:
    """Render a field name for an error message without reflecting arbitrary input."""
    return re.sub(r"[^A-Za-z0-9_.\-]", "", str(value))[:60] or "field"


async def _validation_error(_: Request, exc: Exception) -> JsonResponse:
    """Translate Pydantic's 422 envelope into this API's 400 one."""
    assert isinstance(exc, RequestValidationError)
    errors = exc.errors()

    # An unparseable body is reported per-field as well, so check it first.
    if any(error["type"] == "json_invalid" for error in errors):
        return _error(HTTPStatus.BAD_REQUEST, "Invalid JSON body")

    for error in errors:
        location = error["loc"]
        # ("body",) alone means the body parsed but is not an object at all.
        if tuple(location) == ("body",):
            return _error(HTTPStatus.BAD_REQUEST, "Request body must be a JSON object")
        if len(location) >= 2 and location[0] == "body":
            field = location[1]
            if isinstance(field, str) and field in FIELD_ERRORS:
                return _error(HTTPStatus.BAD_REQUEST, FIELD_ERRORS[field])

    # Anything left is a field this endpoint does not accept. Name it -- sanitised, so
    # a hostile key cannot be reflected into a log or a page -- and say nothing else.
    unknown = next((error["loc"][-1] for error in errors if len(error["loc"]) > 1), "body")
    return _error(HTTPStatus.BAD_REQUEST, f"{_safe_field_name(unknown)} is not a valid field for this endpoint")


class BodyLimitedRoute(APIRoute):
    """Enforce the 1 MB limit before FastAPI parses or validates anything.

    A declared Content-Length is rejected without reading the body at all; the length of
    what actually arrived is checked too, so a chunked request cannot walk past the
    limit by declining to declare one.
    """

    def get_route_handler(self) -> Callable[[Request], Coroutine[Any, Any, Response]]:
        handle = super().get_route_handler()

        async def limited(request: Request) -> Response:
            declared = request.headers.get("content-length")
            if declared is not None and declared.isdigit() and int(declared) > MAX_BODY_BYTES:
                return _error(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, "Request body exceeds 1 MB")
            if len(await request.body()) > MAX_BODY_BYTES:
                return _error(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, "Request body exceeds 1 MB")
            return await handle(request)

        return limited


def create_app() -> FastAPI:
    """Build the ASGI app. A factory, not a module global, so tests can boot their own."""
    app = FastAPI(
        title="Lekgotla",
        description="Compile AI configs into a scoped AGENTS.md manifest.",
        default_response_class=JsonResponse,
    )
    app.router.route_class = BodyLimitedRoute
    app.add_exception_handler(RequestValidationError, _validation_error)

    @app.get("/api/health", response_model=Health)
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/api/compile", response_model=CompileResponse, responses=ERROR_RESPONSES)
    async def compile_endpoint(payload: CompileRequest) -> dict[str, Any]:
        sources = [source.model_dump() for source in payload.sources]
        return compile_manifest(sources, payload.resolutions)

    @app.post("/api/context", response_model=ContextResponse, responses=ERROR_RESPONSES)
    async def context_endpoint(payload: ContextRequest) -> dict[str, Any]:
        return context_bundle(payload.manifest, payload.task)

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
