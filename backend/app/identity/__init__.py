"""Identity module -- accounts, sessions, password hashing, email verification.

Future service: `identity`. Empty until Phase 3 (T012-T020); the boundary exists now so
that the code written then has an obvious home and the module-boundary test (T011) is
already watching it.

Nothing here may be reached by another module through its tables. Callers use the
functions this package exports.
"""
