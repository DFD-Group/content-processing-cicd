#!/usr/bin/env python3
"""Create an EF Core migration and generate a Flyway-versioned SQL file.

Usage:
    python scripts/ef-migrate.py AddUserProfiles
"""

import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PROJECT = "backend/shared/persistence/ContentProcessing.Persistence.csproj"
STARTUP = "backend/auth/AuthService/AuthService.csproj"
CONTEXT = "ContentProcessingDbContext"
FLYWAY_DIR = REPO_ROOT / "backend" / "shared" / "flyway-sql"


def run(cmd: list[str], *, capture: bool = False) -> str | None:
    result = subprocess.run(cmd, capture_output=capture, text=True, cwd=REPO_ROOT)
    if result.returncode != 0:
        if capture and result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(f"Command failed: {' '.join(cmd)}")
    return result.stdout if capture else None


def to_snake_case(name: str) -> str:
    s = re.sub(r"([A-Z])", r"_\1", name).lstrip("_").lower()
    return s.replace(" ", "_")


def next_flyway_version() -> int:
    versions = []
    for f in FLYWAY_DIR.glob("V*__*.sql"):
        m = re.match(r"^V(\d+)__", f.name)
        if m:
            versions.append(int(m.group(1)))
    return max(versions, default=0) + 1


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit("Usage: python scripts/ef-migrate.py <MigrationName>")

    migration_name = sys.argv[1]

    # Verify dotnet-ef is installed
    subprocess.run(["dotnet", "ef", "--version"], capture_output=True, check=False)

    # Step 1 — Capture last existing migration (before adding new one)
    migrations_dir = REPO_ROOT / "backend" / "shared" / "persistence" / "Migrations"
    last_migration = None
    if migrations_dir.exists():
        candidates = sorted(
            f for f in migrations_dir.glob("*_*.cs")
            if not re.search(r"Designer|Snapshot", f.name)
        )
        if candidates:
            last_migration = candidates[-1].stem

    # Step 2 — Generate C# migration
    run(["dotnet", "ef", "migrations", "add", migration_name,
         "--project", PROJECT, "--startup-project", STARTUP, "--context", CONTEXT])

    # Step 3 — Next Flyway version
    version = next_flyway_version()
    snake_name = to_snake_case(migration_name)
    output_file = FLYWAY_DIR / f"V{version}__{snake_name}.sql"

    # Step 4 — Generate incremental SQL
    from_arg = last_migration if last_migration else "0"
    sql = run(["dotnet", "ef", "migrations", "script", from_arg,
               "--project", PROJECT, "--startup-project", STARTUP, "--context", CONTEXT],
              capture=True)

    # Step 5 — Strip EF history table lines
    raw = sql or ""
    raw = re.sub(r"(?s)^.*?(?=START TRANSACTION;)", "", raw)
    raw = re.sub(r"(?m)^.*__EFMigrationsHistory.*$", "", raw)
    raw = re.sub(r"(?m)^VALUES\s*\(.*?\);.*$", "", raw)
    raw = re.sub(r"(\r?\n){3,}", "\n\n", raw)
    raw = raw.strip()

    # Step 6 — Write Flyway file
    FLYWAY_DIR.mkdir(parents=True, exist_ok=True)
    output_file.write_text(raw, encoding="utf-8")
    print(f"Created: {output_file}")


if __name__ == "__main__":
    main()
