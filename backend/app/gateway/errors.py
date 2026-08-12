"""Translation from Pydantic's error vocabulary into this API's.

FastAPI answers a bad request body with a 422 and a Pydantic error list. This API has
always answered 400 with `{"error": "<a sentence>"}`, and the frontend reads that shape.
This module is deliberately the only place the two vocabularies meet.
"""

from __future__ import annotations

import re
from http import HTTPStatus

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError

from app.gateway.responses import JsonResponse, json_error

# Which field failed -> what the client has always been told. Keyed on the first
# segment of the Pydantic error location under "body".
FIELD_ERRORS = {
    "sources": "sources must be an array of { name, content }",
    "resolutions": "resolutions must be a JSON object mapping keys to string values",
    "manifest": "manifest must be a string",
    "task": "task must be a string",
}


def safe_field_name(value: object) -> str:
    """Render a field name for an error message without reflecting arbitrary input."""
    return re.sub(r"[^A-Za-z0-9_.\-]", "", str(value))[:60] or "field"


async def validation_error(_: Request, exc: Exception) -> JsonResponse:
    assert isinstance(exc, RequestValidationError)
    errors = exc.errors()

    # An unparseable body is reported per-field as well, so check it first.
    if any(error["type"] == "json_invalid" for error in errors):
        return json_error(HTTPStatus.BAD_REQUEST, "Invalid JSON body")

    for error in errors:
        location = error["loc"]
        # ("body",) alone means the body parsed but is not an object at all.
        if tuple(location) == ("body",):
            return json_error(HTTPStatus.BAD_REQUEST, "Request body must be a JSON object")
        if len(location) >= 2 and location[0] == "body":
            field = location[1]
            if isinstance(field, str) and field in FIELD_ERRORS:
                return json_error(HTTPStatus.BAD_REQUEST, FIELD_ERRORS[field])

    # Anything left is a field this endpoint does not accept. Name it -- sanitised, so
    # a hostile key cannot be reflected into a log or a page -- and say nothing else.
    unknown = next((error["loc"][-1] for error in errors if len(error["loc"]) > 1), "body")
    return json_error(HTTPStatus.BAD_REQUEST, f"{safe_field_name(unknown)} is not a valid field for this endpoint")


def install_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(RequestValidationError, validation_error)
