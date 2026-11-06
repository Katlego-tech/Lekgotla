"""T011 -- the rule that keeps the Phase 9 service split cheap.

PLAN.md records a deliberate deviation from the kit's microservices default: Lekgotla
starts as a modular monolith and is promoted to services at Phase 9. The deviation is
only safe while one rule holds --

    no module reads another module's tables

-- because a cross-module table read is the one thing a network hop cannot replace. If
this file starts failing, the honest responses are to fix the import or to reopen the
deviation in PLAN.md. Deleting the test is neither.

Two rules are enforced, not one. The second exists to keep the first from being true by
accident: if a module may only reach another module's *package root*, then a model class
that is not re-exported there is unreachable by construction, and the first rule stops
depending on anyone remembering it.
"""

from __future__ import annotations

import ast
from pathlib import Path

APP = Path(__file__).parent.parent.resolve() / "app"

# Every package under app/ is a module boundary. Named for the services they become.
MODULES = {"identity", "github", "compiler", "gateway", "db"}

# app/db is shared plumbing rather than a peer: it owns the engine, the session factory
# and the declarative Base that every module declares its own models against. Reaching
# `app.db` is allowed from anywhere; reaching `app.db.models` is not -- that is the
# aggregate import list Alembic uses, and importing it from a module would pull every
# other module's tables into scope, which is the exact thing this file forbids.
ALWAYS_FORBIDDEN = {"app.db.models"}


def _source_files() -> list[Path]:
    return sorted(path for path in APP.rglob("*.py") if "__pycache__" not in path.parts)


def _owning_module(path: Path) -> str | None:
    """Which module a file belongs to, or None for app/main.py and app/settings.py."""
    relative = path.relative_to(APP).parts
    return relative[0] if len(relative) > 1 and relative[0] in MODULES else None


def _imported_modules(path: Path) -> list[tuple[str, int]]:
    """Every absolute `app.*` module name this file imports, with its line number."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    found: list[tuple[str, int]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.extend((alias.name, node.lineno) for alias in node.names if alias.name.startswith("app."))
        # A relative import cannot leave its own package, so it cannot cross a
        # boundary; only absolute `app.*` imports can.
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and (node.module or "").startswith("app."):
            found.append((node.module or "", node.lineno))
    return found


def test_the_scan_actually_finds_the_modules() -> None:
    # A boundary test that silently scanned nothing would report green forever, which is
    # the failure mode gate.sh exists to make impossible. Same principle, smaller scope.
    files = _source_files()
    assert len(files) > 5, f"expected to scan the app tree, found {files}"
    assert {path.parent.name for path in files} >= MODULES


def test_no_module_reaches_into_another_modules_internals() -> None:
    violations: list[str] = []
    for path in _source_files():
        owner = _owning_module(path)
        for imported, line in _imported_modules(path):
            parts = imported.split(".")
            target = parts[1] if len(parts) > 1 else None
            if target not in MODULES or target == owner:
                continue
            if len(parts) > 2:
                violations.append(
                    f"{path.relative_to(APP.parent)}:{line} imports {imported}; "
                    f"cross-module imports may only reach app.{target}"
                )
    assert not violations, "module boundaries crossed:\n  " + "\n  ".join(violations)


def test_no_module_imports_the_aggregate_model_registry() -> None:
    violations: list[str] = []
    for path in _source_files():
        for imported, line in _imported_modules(path):
            if imported in ALWAYS_FORBIDDEN:
                violations.append(f"{path.relative_to(APP.parent)}:{line} imports {imported}")
    assert not violations, (
        "app.db.models is for Alembic only -- importing it from a module puts every "
        "other module's tables in scope:\n  " + "\n  ".join(violations)
    )


def test_no_module_declares_a_model_outside_its_own_package() -> None:
    # The rule as PLAN.md states it: tables belong to the module that owns them. A
    # DeclarativeBase subclass at app/ root, or in the gateway, would be a table with no
    # owner -- and nothing to move when Phase 9 splits the services apart.
    homeless: list[str] = []
    for path in _source_files():
        if _owning_module(path) is not None:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and any(
                isinstance(base, ast.Name) and base.id == "Base" for base in node.bases
            ):
                homeless.append(f"{path.relative_to(APP.parent)}:{node.lineno} declares {node.name}")
    assert not homeless, "models must live inside the module that owns them:\n  " + "\n  ".join(homeless)
