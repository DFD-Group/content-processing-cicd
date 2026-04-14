#!/usr/bin/env python3
"""Remove the last Alembic migration and its corresponding Flyway SQL file.

Reverses what alembic-migrate.py created.

Usage:
    python scripts/alembic-remove.py

Prerequisites:
    - alembic importable (activate your venv)
"""

import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TEXT2IMAGE_DIR = REPO_ROOT / "backend" / "text2image"
FLYWAY_DIR = REPO_ROOT / "backend" / "shared" / "flyway-sql"
VERSIONS_DIR = TEXT2IMAGE_DIR / "alembic" / "versions"


def alembic_head() -> str | None:
    result = subprocess.run(
        ["alembic", "heads"],
        capture_output=True, text=True, cwd=TEXT2IMAGE_DIR,
    )
    if result.returncode != 0 or not result.stdout.strip():
        return None
    return result.stdout.strip().split()[0]


def main() -> None:
    # ── Step 1 — Find the current head revision ─────────────────────
    head = alembic_head()
    if not head:
        sys.exit("No Alembic migrations found.")
    print(f"Current Alembic head: {head}")

    # ── Step 2 — Find and delete the head revision file ──────────────
    candidates = list(VERSIONS_DIR.glob(f"{head}_*.py"))
    if not candidates:
        sys.exit(f"Could not find revision file for head {head} in {VERSIONS_DIR}")

    revision_file = candidates[0]
    revision_file.unlink()
    print(f"Removed Alembic revision: {revision_file.name}")

    # ── Step 3 — Find and delete the latest Flyway SQL file ─────────
    sql_files = []
    for f in FLYWAY_DIR.glob("V*__*.sql"):
        m = re.match(r"^V(\d+)__", f.name)
        if m:
            sql_files.append((int(m.group(1)), f))
    sql_files.sort()

    if sql_files:
        latest = sql_files[-1][1]
        latest.unlink()
        print(f"Removed Flyway SQL:      {latest.name}")
    else:
        print("No Flyway SQL file found to remove.")

    # ── Step 4 — Show new state ──────────────────────────────────────
    new_head = alembic_head()
    print(f"\nNew Alembic head: {new_head or '<none>'}")


if __name__ == "__main__":
    main()
