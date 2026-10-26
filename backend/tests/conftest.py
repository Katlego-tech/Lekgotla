"""Test fixtures shared across the suite.

The `client` fixture is the seam that makes T006's contract tests portable. The tests
themselves speak only HTTP, so the migration from `http.server` to FastAPI (T007) was a
change to *this* file and nothing else -- which is the whole point of having written
them first.

The app is driven over a real socket rather than through an in-process ASGI transport.
That costs a thread and a few hundred milliseconds, and buys assertions about status
codes, headers and static file serving that an in-process shortcut cannot make.
"""

from __future__ import annotations

import sys
import threading
import time
from collections.abc import Iterator
from pathlib import Path

import httpx
import pytest
import uvicorn

sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from app.main import create_app

STARTUP_TIMEOUT_SECONDS = 10.0


@pytest.fixture(scope="session")
def base_url() -> Iterator[str]:
    """Boot the real app on an ephemeral port and yield its origin."""
    # Port 0 lets the OS pick a free port, so a dev server already on 4173 does not
    # collide with the suite.
    config = uvicorn.Config(create_app(), host="127.0.0.1", port=0, log_level="warning")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    deadline = time.monotonic() + STARTUP_TIMEOUT_SECONDS
    while not server.started:
        if not thread.is_alive() or time.monotonic() > deadline:
            raise RuntimeError("the test server did not start")
        time.sleep(0.01)

    port = server.servers[0].sockets[0].getsockname()[1]
    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        server.should_exit = True
        thread.join(timeout=STARTUP_TIMEOUT_SECONDS)


@pytest.fixture
def client(base_url: str) -> Iterator[httpx.Client]:
    with httpx.Client(base_url=base_url, timeout=10.0) as http_client:
        yield http_client
