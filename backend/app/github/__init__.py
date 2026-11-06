"""GitHub module -- OAuth, repository listing, read-only fetch, PR writes.

Future service: `github`. Empty until Phase 6 (T036-T040).

Two constraints land here when it is built, both from PLAN.md: access is read-only
unless a repository is explicitly opted in, and a write only ever opens or updates a PR
branch -- never a direct commit.
"""
