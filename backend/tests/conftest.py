"""Test fixtures shared across the suite.

The `client` fixture is the seam that makes T006's contract tests portable. The tests
themselves speak only HTTP, so the migration from `http.server` to FastAPI (T007) is a
change to *this* file and nothing else -- which is the whole point of writing them first.
"""

from __future__ import annotations

import sys
import threading
from collections.abc import Iterator
from http.server import ThreadingHTTPServer
from pathlib import Path

import httpx
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from app.main import LekgotlaHandler


@pytest.fixture(scope="session")
def base_url() -> Iterator[str]:
    """Boot the real server on an ephemeral port and yield its origin."""
    # Port 0 lets the OS pick a free port, so a running dev server on 4173 does not
    # collide with the suite.
    server = ThreadingHTTPServer(("127.0.0.1", 0), LekgotlaHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_address[1]}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


@pytest.fixture
def client(base_url: str) -> Iterator[httpx.Client]:
    with httpx.Client(base_url=base_url, timeout=10.0) as http_client:
        yield http_client
