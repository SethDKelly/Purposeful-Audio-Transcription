#!/usr/bin/env python3
"""Run Alembic upgrade head (ECS one-off migration entrypoint)."""

from __future__ import annotations

from backend.db.migrations import upgrade_head


def main() -> None:
    try:
        upgrade_head()
    except Exception:
        import traceback

        traceback.print_exc()
        raise
    print("alembic upgrade head OK", flush=True)


if __name__ == "__main__":
    main()
