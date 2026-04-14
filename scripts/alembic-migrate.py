#!/usr/bin/env python3
"""Create an Alembic migration and generate a Flyway-versioned SQL file.

Usage:
    python scripts/alembic-migrate.py "create_text_jobs_and_text_images"
    python scripts/alembic-migrate.py --sql-only "create_text_jobs_and_text_images"

Options:
    --sql-only   Skip 'alembic revision'; just export existing head to Flyway SQL.

Prerequisites:
    - alembic importable (activate your venv)
    - CONTENT_PROCESSING_CONNECTION_STRING env var set (needed for autogenerate)
"""

import os
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TEXT2IMAGE_DIR = REPO_ROOT / "backend" / "text2image"
FLYWAY_DIR = REPO_ROOT / "backend" / "shared" / "flyway-sql"


def run(cmd: list[str], *, capture: bool = False) -> str | None:
    result = subprocess.run(cmd, capture_output=capture, text=True, cwd=TEXT2IMAGE_DIR)
    if result.returncode != 0:
        if capture and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(f"Command failed: {' '.join(cmd)}")
    return result.stdout if capture else None


def alembic_head() -> str | None:
    """Return the current Alembic head revision ID, or None if no migrations exist."""
    result = subprocess.run(
        ["alembic", "heads"],
        capture_output=True, text=True, cwd=TEXT2IMAGE_DIR,
    )
    if result.returncode != 0 or not result.stdout.strip():
        return None
    return result.stdout.strip().split()[0]


def to_snake_case(name: str) -> str:
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", s)
    return s.lower().replace(" ", "_")


def next_flyway_version() -> int:
    versions = []
    for f in FLYWAY_DIR.glob("V*__*.sql"):
        m = re.match(r"^V(\d+)__", f.name)
        if m:
            versions.append(int(m.group(1)))
    return max(versions, default=0) + 1


def strip_alembic_bookkeeping(sql: str) -> str:
    sql = re.sub(r"(?s)CREATE TABLE.*?alembic_version.*?\);", "", sql)
    sql = re.sub(r"(?s)INSERT INTO.*?alembic_version.*?;", "", sql)
    sql = re.sub(r"(?s)UPDATE.*?alembic_version.*?;", "", sql)
    sql = re.sub(r"(?m)^BEGIN;$", "START TRANSACTION;", sql)
    sql = re.sub(r"(\r?\n){3,}", "\n\n", sql)
    return sql.strip()


def main() -> None:
    # ── Parse arguments ──────────────────────────────────────────────
    args = sys.argv[1:]
    sql_only = False
    if "--sql-only" in args:
        sql_only = True
        args.remove("--sql-only")

    if not args:
        sys.exit(
            "Usage: python scripts/alembic-migrate.py [--sql-only] <migration_message>\n"
            "  --sql-only   Skip 'alembic revision'; just export existing head to Flyway SQL\n\n"
            "Examples:\n"
            "  python scripts/alembic-migrate.py create_text_jobs     # create + export\n"
            "  python scripts/alembic-migrate.py --sql-only create_text_jobs  # export only"
        )

    migration_msg = args[0]

    # ── Pre-flight checks ────────────────────────────────────────────
    if not os.environ.get("CONTENT_PROCESSING_CONNECTION_STRING"):
        sys.exit(
            "Error: CONTENT_PROCESSING_CONNECTION_STRING is not set.\n"
            "Export it first, e.g.:\n"
            "  export CONTENT_PROCESSING_CONNECTION_STRING='postgresql+psycopg://user:pass@localhost:5433/db'"
        )

    FLYWAY_DIR.mkdir(parents=True, exist_ok=True)

    # ── Step 1 — Capture current head ────────────────────────────────
    old_head = alembic_head()
    print(f"Current Alembic head: {old_head or '<none>'}")

    # ── Step 2 — Create migration (skipped with --sql-only) ─────────
    if not sql_only:
        print(f"Creating Alembic migration: {migration_msg}")
        run(["alembic", "revision", "--autogenerate", "-m", migration_msg])
    else:
        print("Skipping revision (--sql-only). Exporting existing migrations...")

    # ── Step 3 — Generate raw SQL (offline mode) ─────────────────────
    if sql_only or not old_head:
        sql_range = "head"
    else:
        sql_range = f"{old_head}:head"

    print(f"Generating SQL (range: {sql_range})...")
    raw_sql = run(["alembic", "upgrade", sql_range, "--sql"], capture=True) or ""

    # ── Step 4 — Strip bookkeeping ───────────────────────────────────
    clean_sql = strip_alembic_bookkeeping(raw_sql)

    # ── Step 5 — Write Flyway file ───────────────────────────────────
    version = next_flyway_version()
    snake_name = to_snake_case(migration_msg)
    output_file = FLYWAY_DIR / f"V{version}__{snake_name}.sql"

    output_file.write_text(clean_sql + "\n", encoding="utf-8")

    print()
    if not sql_only:
        print("Alembic migration created.")
    print(f"Flyway SQL written to: {output_file}")


if __name__ == "__main__":
    main()
