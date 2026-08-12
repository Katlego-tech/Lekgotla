"""T008 -- the request and response contracts, as Pydantic models.

Response models are declared as well as request models on purpose. They are what stops
a future change to `compiler.py` from quietly adding a field to the wire format, and --
once Phase 3 lands accounts -- they are the layer that makes "secrets never round-trip"
(PLAN.md, Non-negotiable II) something the framework enforces rather than something
every handler has to remember. A field that is not on the response model cannot be
returned, however it got into the dict.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class Strict(BaseModel):
    """Base for request models: unknown fields are rejected, not silently ignored."""

    model_config = ConfigDict(extra="forbid")


# ------------------------------------------------------------------------- requests


class Source(Strict):
    name: str
    content: str


class CompileRequest(Strict):
    sources: list[Source]
    resolutions: dict[str, str] | None = None


class ContextRequest(Strict):
    manifest: str
    task: str = "ui"


# ------------------------------------------------------------------------ responses


class Health(BaseModel):
    status: str


class ConflictOption(BaseModel):
    value: str
    # Non-negotiable I: a conflict cites the real contradicting rule and the real file
    # it came from. Both are required fields precisely so neither can be omitted.
    text: str
    source: str


class Conflict(BaseModel):
    key: str
    title: str
    options: list[ConflictOption]
    severity: str


class CompileResponse(BaseModel):
    manifest: str
    conflicts: list[Conflict]
    directives: int
    inputTokens: int  # noqa: N815 -- the wire format the frontend already consumes
    outputTokens: int  # noqa: N815
    reclaimed: int


class ContextResponse(BaseModel):
    task: str
    bundle: str
    tokens: int
    rules: int
    areas: str
    reduction: int


class Error(BaseModel):
    error: str
