"""Every module's models, imported in one place so Alembic can see them.

Alembic autogenerates against `Base.metadata`, and a model class that no one has
imported is not in it -- which produces an empty migration and a silent data loss the
first time someone trusts it. This module exists so `alembic/env.py` has a single thing
to import, and so adding a model to a new module is one line here.

This is emphatically *not* a shared model namespace. Importing it from inside a module
would defeat T011; it is imported by migration tooling only, which is why the boundary
test allows `alembic/` and forbids `app/*/`.

Phase 3 adds identity's models here, Phase 4 the compiler's.
"""

from __future__ import annotations

from app.db.base import Base

__all__ = ["Base"]
