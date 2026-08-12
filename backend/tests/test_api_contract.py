"""T006 -- the HTTP contract of the API as it exists today.

Written against the stdlib `http.server` implementation *before* the FastAPI migration
(T007), so that the migration has something to be judged against. Every assertion here
pins observable behaviour -- status code, body shape, error string -- and none of them
reach into the implementation. If a line in this file has to change to make FastAPI
pass, that is a contract break, not a test that needs updating.

The 400-path cases are as load-bearing as the happy paths: FastAPI's default validation
failure is a 422 with a Pydantic error envelope, so keeping these green is what forces
T008's translation layer to exist.
"""

from __future__ import annotations

import httpx
import pytest

SOURCES = [
    {
        "name": ".cursorrules",
        "content": "Use pnpm for package operations.\nRun pnpm test before handoff.\nNever commit secrets.",
    },
    {"name": "CLAUDE.md", "content": "Install packages with npm only.\nFollow conventional commits."},
]


def _json_headers() -> dict[str, str]:
    return {"Content-Type": "application/json"}


# --------------------------------------------------------------------------- health


def test_health_returns_ok(client: httpx.Client) -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert response.headers["content-type"] == "application/json; charset=utf-8"


# -------------------------------------------------------------------------- compile


def test_compile_returns_the_full_result_shape(client: httpx.Client) -> None:
    response = client.post("/api/compile", json={"sources": SOURCES})

    assert response.status_code == 200
    body = response.json()
    assert set(body) == {
        "manifest",
        "conflicts",
        "directives",
        "inputTokens",
        "outputTokens",
        "reclaimed",
    }
    assert body["manifest"].startswith("# Lekgotla Manifest")
    assert isinstance(body["conflicts"], list)
    assert isinstance(body["directives"], int)


def test_compile_reports_the_package_manager_conflict(client: httpx.Client) -> None:
    body = client.post("/api/compile", json={"sources": SOURCES}).json()

    conflict = next(item for item in body["conflicts"] if item["key"] == "packageManager")
    assert conflict["severity"] == "high"
    # Non-negotiable I: a reported conflict cites the two real contradicting rules.
    assert {option["source"] for option in conflict["options"]} == {".cursorrules", "CLAUDE.md"}


def test_compile_applies_a_resolution(client: httpx.Client) -> None:
    response = client.post("/api/compile", json={"sources": SOURCES, "resolutions": {"packageManager": "npm"}})

    assert response.status_code == 200
    assert "Use npm for all package operations." in response.json()["manifest"]


def test_compile_accepts_an_empty_source_list(client: httpx.Client) -> None:
    response = client.post("/api/compile", json={"sources": []})

    assert response.status_code == 200
    assert response.json()["reclaimed"] == 0


@pytest.mark.parametrize(
    "payload",
    [
        pytest.param({}, id="sources-missing"),
        pytest.param({"sources": "nope"}, id="sources-not-a-list"),
        pytest.param({"sources": [{"name": ".cursorrules"}]}, id="item-missing-content"),
        pytest.param({"sources": [{"content": "Use pnpm."}]}, id="item-missing-name"),
        pytest.param({"sources": [{"name": 1, "content": "Use pnpm."}]}, id="name-not-a-string"),
        pytest.param({"sources": ["CLAUDE.md"]}, id="item-not-an-object"),
    ],
)
def test_compile_rejects_malformed_sources(client: httpx.Client, payload: dict[str, object]) -> None:
    response = client.post("/api/compile", json=payload)

    assert response.status_code == 400
    assert response.json() == {"error": "sources must be an array of { name, content }"}


@pytest.mark.parametrize(
    "resolutions",
    [
        pytest.param("packageManager=npm", id="not-an-object"),
        pytest.param({"packageManager": 3}, id="value-not-a-string"),
    ],
)
def test_compile_rejects_malformed_resolutions(client: httpx.Client, resolutions: object) -> None:
    response = client.post("/api/compile", json={"sources": SOURCES, "resolutions": resolutions})

    assert response.status_code == 400
    assert response.json() == {"error": "resolutions must be a JSON object mapping keys to string values"}


def test_compile_treats_null_resolutions_as_absent(client: httpx.Client) -> None:
    response = client.post("/api/compile", json={"sources": SOURCES, "resolutions": None})

    assert response.status_code == 200


# -------------------------------------------------------------------------- context


def test_context_returns_the_full_bundle_shape(client: httpx.Client) -> None:
    manifest = client.post("/api/compile", json={"sources": SOURCES}).json()["manifest"]

    response = client.post("/api/context", json={"manifest": manifest, "task": "review"})

    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"task", "bundle", "tokens", "rules", "areas", "reduction"}
    assert body["task"] == "Review payment PR"
    assert "Delivery" in body["bundle"]


def test_context_defaults_to_the_ui_task(client: httpx.Client) -> None:
    manifest = client.post("/api/compile", json={"sources": SOURCES}).json()["manifest"]

    response = client.post("/api/context", json={"manifest": manifest})

    assert response.status_code == 200
    assert response.json()["task"] == "Build checkout UI"


def test_context_falls_back_to_ui_for_an_unknown_task(client: httpx.Client) -> None:
    manifest = client.post("/api/compile", json={"sources": SOURCES}).json()["manifest"]

    response = client.post("/api/context", json={"manifest": manifest, "task": "not-a-task"})

    assert response.status_code == 200
    assert response.json()["task"] == "Build checkout UI"


@pytest.mark.parametrize(
    "payload",
    [
        pytest.param({}, id="manifest-missing"),
        pytest.param({"manifest": None}, id="manifest-null"),
        pytest.param({"manifest": ["# Lekgotla Manifest"]}, id="manifest-not-a-string"),
    ],
)
def test_context_rejects_a_non_string_manifest(client: httpx.Client, payload: dict[str, object]) -> None:
    response = client.post("/api/context", json=payload)

    assert response.status_code == 400
    assert response.json() == {"error": "manifest must be a string"}


def test_context_rejects_a_non_string_task(client: httpx.Client) -> None:
    response = client.post("/api/context", json={"manifest": "# Lekgotla Manifest", "task": 7})

    assert response.status_code == 400
    assert response.json() == {"error": "task must be a string"}


# ----------------------------------------------------------------- envelope + limits


@pytest.mark.parametrize("path", ["/api/compile", "/api/context"])
def test_rejects_a_body_that_is_not_a_json_object(client: httpx.Client, path: str) -> None:
    response = client.post(path, json=["sources"])

    assert response.status_code == 400
    assert response.json() == {"error": "Request body must be a JSON object"}


@pytest.mark.parametrize("path", ["/api/compile", "/api/context"])
def test_rejects_unparseable_json(client: httpx.Client, path: str) -> None:
    response = client.post(path, content=b"{not json", headers=_json_headers())

    assert response.status_code == 400
    assert response.json() == {"error": "Invalid JSON body"}


def test_rejects_a_body_over_one_megabyte(client: httpx.Client) -> None:
    oversized = b'{"sources": [{"name": "big", "content": "' + b"x" * 1_000_001 + b'"}]}'

    response = client.post("/api/compile", content=oversized, headers=_json_headers())

    assert response.status_code == 413
    assert response.json() == {"error": "Request body exceeds 1 MB"}


def test_unknown_api_route_is_a_json_404(client: httpx.Client) -> None:
    response = client.post("/api/nope", json={})

    assert response.status_code == 404
    assert response.json() == {"error": "Not found"}


# ---------------------------------------------------------------------- static files


def test_serves_the_frontend_index(client: httpx.Client) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "<title>" in response.text


def test_serves_the_frontend_assets(client: httpx.Client) -> None:
    for asset in ("/style.css", "/script.js"):
        assert client.get(asset).status_code == 200, asset


def test_missing_static_file_is_a_404(client: httpx.Client) -> None:
    assert client.get("/does-not-exist.html").status_code == 404
