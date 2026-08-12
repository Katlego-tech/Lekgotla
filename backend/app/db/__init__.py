"""Database module -- the engine, the session factory, and the declarative base.

Shared plumbing rather than a future service: every module declares its own models
against this base and reads only its own tables. That single rule is what keeps the
Phase 9 service split cheap, and T011 enforces it.

Filled in by T010.
"""
