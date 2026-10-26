"""The browser-facing routes.

The gateway is the only module the browser talks to. It validates, calls into the other
modules through their public functions, and shapes the reply -- it holds no domain logic
of its own, so that Phase 9 can put a network hop under each of those calls without
rewriting anything here.
"""

from __future__ import annotations

from http import HTTPStatus
from typing import Any

from fastapi import APIRouter

from app.compiler import compile_manifest, context_bundle
from app.gateway.responses import BodyLimitedRoute, JsonResponse, json_error
from app.gateway.schemas import (
    CompileRequest,
    CompileResponse,
    ContextRequest,
    ContextResponse,
    Error,
    Health,
)

ERROR_RESPONSES: dict[int | str, dict[str, Any]] = {
    400: {"model": Error, "description": "The request body is malformed."},
    413: {"model": Error, "description": "The request body exceeds 1 MB."},
}

router = APIRouter(route_class=BodyLimitedRoute, default_response_class=JsonResponse)


@router.get("/api/health", response_model=Health)
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/api/compile", response_model=CompileResponse, responses=ERROR_RESPONSES)
async def compile_endpoint(payload: CompileRequest) -> dict[str, Any]:
    sources = [source.model_dump() for source in payload.sources]
    return compile_manifest(sources, payload.resolutions)


@router.post("/api/context", response_model=ContextResponse, responses=ERROR_RESPONSES)
async def context_endpoint(payload: ContextRequest) -> dict[str, Any]:
    return context_bundle(payload.manifest, payload.task)


# Anything else under /api is a JSON 404, not the static mount's HTML one. Registered
# last within this router, and the router is included before the mount, because
# Starlette matches routes in registration order.
@router.api_route(
    "/api/{unmatched:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"],
    include_in_schema=False,
)
async def unknown_api_route(unmatched: str) -> JsonResponse:
    return json_error(HTTPStatus.NOT_FOUND, "Not found")
