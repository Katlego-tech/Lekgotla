"""Compiler module -- the deterministic merge, and later the semantic one.

Future service: `compiler`. Owns rule extraction, conflict detection, resolution
application and context bundling. It is the real asset in this repository and its
behaviour must survive every migration (CLAUDE.md).

This package re-exports the module's public interface so callers depend on
`app.compiler`, not on the file layout inside it. Other modules call these functions;
nothing outside this package touches its internals or (from Phase 4) its tables.
"""

from app.compiler.compiler import compile_manifest, context_bundle, estimate_tokens

__all__ = ["compile_manifest", "context_bundle", "estimate_tokens"]
