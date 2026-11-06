"""The declarative base every module's models are declared against.

One base, one `MetaData`, one Alembic history -- because a modular monolith with four
migration histories is harder to split than one with a single history, not easier. The
boundary that matters is *ownership*: a module reads only its own tables (T011).

The naming convention is not cosmetic. SQLite cannot drop an unnamed constraint, so
without it a later migration that alters a table has nothing to refer to.
"""

from __future__ import annotations

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)
