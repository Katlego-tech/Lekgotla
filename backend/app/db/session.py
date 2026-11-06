"""Engine and session factory.

Sessions are synchronous. SQLAlchemy's async layer buys nothing over SQLite -- the
driver has no async story and every statement is a local file read -- and it costs an
extra dependency plus a second set of idioms. Route handlers that touch the database are
therefore declared `def`, not `async def`, so FastAPI runs them in its threadpool and a
slow query cannot block the event loop. This is the one thing to remember when Phase 3
writes the first data endpoint.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from functools import lru_cache
from typing import Any

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from app.settings import get_settings


@event.listens_for(Engine, "connect")
def _enforce_sqlite_foreign_keys(connection: Any, _: Any) -> None:
    """SQLite ignores foreign keys unless asked, per connection, every time.

    Without this, a cascade or a reference to a deleted row fails silently rather than
    raising -- which is exactly the kind of bug that only shows up in production data.
    """
    if isinstance(connection, sqlite3.Connection):
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


@lru_cache
def get_engine() -> Engine:
    settings = get_settings()
    connect_args: dict[str, Any] = {}
    if settings.database_url.startswith("sqlite"):
        # FastAPI serves sync handlers from a threadpool, so a connection legitimately
        # moves between threads. SQLite's own guard would reject that.
        connect_args["check_same_thread"] = False
    return create_engine(settings.database_url, connect_args=connect_args, future=True)


@lru_cache
def get_sessionmaker() -> sessionmaker[Session]:
    return sessionmaker(bind=get_engine(), autoflush=False, expire_on_commit=False)


def get_session() -> Iterator[Session]:
    """FastAPI dependency. One session per request, closed whatever happens."""
    with get_sessionmaker()() as session:
        yield session
