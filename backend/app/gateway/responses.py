"""Response types and the body-size limit -- the parts of the gateway that sit in
front of routing rather than inside it."""

from __future__ import annotations

from collections.abc import Callable, Coroutine
from http import HTTPStatus
from typing import Any

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute

MAX_BODY_BYTES = 1_000_000


class JsonResponse(JSONResponse):
    """JSONResponse that keeps the original server's exact Content-Type.

    Starlette only appends `charset` to `text/*` media types, so the stock class would
    answer `application/json` where this API has always answered
    `application/json; charset=utf-8`.
    """

    media_type = "application/json; charset=utf-8"


def json_error(status: HTTPStatus, message: str) -> JsonResponse:
    """The one error envelope this API emits: `{"error": "<a sentence>"}`."""
    return JsonResponse(status_code=status, content={"error": message})


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
                return json_error(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, "Request body exceeds 1 MB")
            if len(await request.body()) > MAX_BODY_BYTES:
                return json_error(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, "Request body exceeds 1 MB")
            return await handle(request)

        return limited
