"""T008 -- the behaviour Pydantic added on top of the frozen contract.

`test_api_contract.py` pins what the API has always done. This file pins what T008
changed: unknown fields are now refused rather than ignored, and no error body leaks
back what the client sent.
"""

from __future__ import annotations

import httpx
import pytest

SOURCES = [{"name": "CLAUDE.md", "content": "Use pnpm for package operations."}]


@pytest.mark.parametrize(
    ("path", "payload"),
    [
        ("/api/compile", {"sources": SOURCES, "sorces": SOURCES}),
        ("/api/context", {"manifest": "# Lekgotla Manifest", "tsk": "ui"}),
    ],
)
def test_an_unknown_field_is_refused_and_named(client: httpx.Client, path: str, payload: dict[str, object]) -> None:
    response = client.post(path, json=payload)

    assert response.status_code == 400
    # Actionable: a typo'd key gets named, so the caller can see which one it was.
    assert response.json()["error"] in {
        "sorces is not a valid field for this endpoint",
        "tsk is not a valid field for this endpoint",
    }


def test_a_hostile_field_name_is_not_reflected_back(client: httpx.Client) -> None:
    response = client.post("/api/compile", json={"sources": SOURCES, "<script>alert(1)</script>": 1})

    assert response.status_code == 400
    error = response.json()["error"]
    assert "<" not in error and ">" not in error and "(" not in error


def test_errors_never_echo_the_submitted_content(client: httpx.Client) -> None:
    # Deliberately not credential-shaped: the gate's secret sweep scans the tree, and a
    # realistic-looking token in a fixture would train everyone to ignore that alarm.
    canary = "DO-NOT-ECHO-THIS-CONTENT"
    response = client.post("/api/compile", json={"sources": [{"name": "CLAUDE.md", "content": canary}], "task": 1})

    assert response.status_code == 400
    assert canary not in response.text


def test_the_response_carries_only_the_declared_fields(client: httpx.Client) -> None:
    # The response model is the wire contract; a field the compiler grows later cannot
    # reach a client without being declared in app/schemas.py first.
    body = client.post("/api/compile", json={"sources": SOURCES}).json()

    assert set(body) == {"manifest", "conflicts", "directives", "inputTokens", "outputTokens", "reclaimed"}
    for conflict in body["conflicts"]:
        assert set(conflict) == {"key", "title", "options", "severity"}
