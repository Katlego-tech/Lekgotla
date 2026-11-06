"""Alembic environment.

Two things differ from the stock template, both on purpose:

  - the URL comes from `app.settings`, not from alembic.ini, so there is one source of
    truth for the DSN and no connection string to commit by accident;
  - `render_as_batch` is on, because SQLite cannot ALTER a column. Batch mode rewrites
    the table instead, which is what makes a column change possible at all on the
    Phase 1-8 datastore.
"""

from __future__ import annotations

import sys
from pathlib import Path

from sqlalchemy import engine_from_config, pool

from alembic import context

sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from app.db.models import Base  # noqa: E402 -- must follow the sys.path insert
from app.settings import get_settings  # noqa: E402

config = context.config
config.set_main_option("sqlalchemy.url", get_settings().database_url)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
