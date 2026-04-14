#!/usr/bin/env python3
"""Commit and push develop to all three branches (develop, staging, main).

Usage:
    python scripts/git-push-all.py "feat: add new service"
    python scripts/git-push-all.py --skip-ci "fix: linter warnings"
    python scripts/git-push-all.py --skip-ci --files .github/workflows/ci-develop.yml .github/workflows/_deploy.yml "fix: ci"

Options:
    --files FILE [FILE ...]   Stage only the specified files. If omitted, stages everything (git add -A).
    --skip-ci                 Append [skip ci] to prevent GitHub Actions from triggering.
"""

import subprocess
import sys


def run(cmd: list[str]) -> None:
    result = subprocess.run(cmd)
    if result.returncode != 0:
        sys.exit(f"Command failed: {' '.join(cmd)}")


def main() -> None:
    args = sys.argv[1:]
    skip_ci = False
    files: list[str] = []

    if "--skip-ci" in args:
        skip_ci = True
        args.remove("--skip-ci")

    if "--files" in args:
        idx = args.index("--files")
        rest = args[idx + 1:]
        # Everything until the last arg (commit message) belongs to --files
        files = rest[:-1]
        args = args[:idx] + [rest[-1]]

    if not args:
        sys.exit(
            "Usage: python scripts/git-push-all.py [--skip-ci] [--files FILE ...] <commit_message>"
        )

    commit_message = args[0]
    if skip_ci:
        commit_message += " [skip ci]"

    run(["git", "checkout", "develop"])

    if files:
        run(["git", "add"] + files)
    else:
        run(["git", "add", "-A"])

    run(["git", "commit", "-m", commit_message])
    run(["git", "push", "origin", "develop"])
    run(["git", "push", "origin", "develop:staging"])
    run(["git", "push", "origin", "develop:main"])

    print("Pushed to develop, staging, and main.")


if __name__ == "__main__":
    main()
