#!/usr/bin/env python3
"""Remove the last EF Core migration and its corresponding Flyway SQL file.

Reverses what ef-migrate.py created.

Usage:
    python scripts/ef-remove.py
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


def main() -> None:
    # Step 1 — Find the latest Flyway SQL file (highest version number)
    sql_files = []
    for f in FLYWAY_DIR.glob("V*__*.sql"):
        m = re.match(r"^V(\d+)__", f.name)
        if m:
            sql_files.append((int(m.group(1)), f))
    sql_files.sort()
    latest_sql = sql_files[-1][1] if sql_files else None

    # Step 2 — Remove the last EF C# migration
    result = subprocess.run(
        ["dotnet", "ef", "migrations", "remove",
         "--project", PROJECT, "--startup-project", STARTUP,
         "--context", CONTEXT, "--force"],
        cwd=REPO_ROOT,
    )
    if result.returncode != 0:
        sys.exit("dotnet ef migrations remove failed")

    # Step 3 — Delete the corresponding Flyway SQL file
    if latest_sql:
        latest_sql.unlink()
        print(f"Removed: {latest_sql}")
    else:
        print("No Flyway SQL file found to remove.")


if __name__ == "__main__":
    main()
