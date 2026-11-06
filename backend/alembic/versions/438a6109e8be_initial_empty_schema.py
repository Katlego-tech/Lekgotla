"""initial empty schema

Revision ID: 438a6109e8be
Revises:
Create Date: 2026-08-12 20:52:11.982110
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "438a6109e8be"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
