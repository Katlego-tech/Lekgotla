"""Lekgotla local API: compile AI configs into a scoped AGENTS.md manifest."""

from __future__ import annotations

import json
import sys
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, cast

# Add backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from app.compiler import compile_manifest, context_bundle

ROOT = Path(__file__).parent.parent.parent.resolve() / "frontend"
PORT = 4173


class LekgotlaHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self) -> None:
        if self.path == "/api/health":
            return self.send_json(HTTPStatus.OK, {"status": "ok"})
        return super().do_GET()

    def do_POST(self) -> None:
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length > 1_000_000:
                return self.send_json(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, {"error": "Request body exceeds 1 MB"})
            body = json.loads(self.rfile.read(length) or "{}")
            if not isinstance(body, dict):
                return self.send_json(HTTPStatus.BAD_REQUEST, {"error": "Request body must be a JSON object"})

            if self.path == "/api/compile":
                sources = body.get("sources")
                invalid_sources = not isinstance(sources, list) or any(
                    not isinstance(item, dict)
                    or not isinstance(item.get("name"), str)
                    or not isinstance(item.get("content"), str)
                    for item in sources
                )
                if invalid_sources:
                    return self.send_json(
                        HTTPStatus.BAD_REQUEST,
                        {"error": "sources must be an array of { name, content }"},
                    )
                resolutions = body.get("resolutions")
                if resolutions is not None and (
                    not isinstance(resolutions, dict)
                    or any(not isinstance(k, str) or not isinstance(v, str) for k, v in resolutions.items())
                ):
                    return self.send_json(
                        HTTPStatus.BAD_REQUEST,
                        {"error": "resolutions must be a JSON object mapping keys to string values"},
                    )
                return self.send_json(HTTPStatus.OK, compile_manifest(cast(list[dict[str, str]], sources), resolutions))

            if self.path == "/api/context":
                if not isinstance(body.get("manifest"), str):
                    return self.send_json(HTTPStatus.BAD_REQUEST, {"error": "manifest must be a string"})
                task = body.get("task", "ui")
                if not isinstance(task, str):
                    return self.send_json(HTTPStatus.BAD_REQUEST, {"error": "task must be a string"})
                return self.send_json(HTTPStatus.OK, context_bundle(body["manifest"], task))

            return self.send_json(HTTPStatus.NOT_FOUND, {"error": "Not found"})
        except (json.JSONDecodeError, ValueError):
            return self.send_json(HTTPStatus.BAD_REQUEST, {"error": "Invalid JSON body"})
        except Exception as error:  # pragma: no cover - final API safety net
            return self.send_json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": str(error)})

    def send_json(self, status: HTTPStatus, payload: dict[str, Any]) -> None:
        encoded = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", PORT), LekgotlaHandler)
    print(f"Lekgotla running at http://localhost:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
