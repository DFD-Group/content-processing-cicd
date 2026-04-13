#!/usr/bin/env pwsh
# Usage:
#   pwsh scripts/git-push-all.ps1 -CommitMessage "feat: add new service" -SkipCi
#   pwsh scripts/git-push-all.ps1 -CommitMessage "fix: linter warnings" -Files ".github/workflows/ci-develop.yml",".github/workflows/_deploy.yml" -SkipCi
#
# Commits and pushes develop to all three branches (develop, staging, main).
# -Files    Optional. Stages only the specified files. If omitted, stages everything (git add -A).
# -SkipCi   Optional. Appends [skip ci] to prevent GitHub Actions from triggering.

param(
    [Parameter(Mandatory)]
    [string]$CommitMessage,

    [string[]]$Files,

    [switch]$SkipCi
)

if ($SkipCi) {
    $CommitMessage = "$CommitMessage [skip ci]"
}

git checkout develop
if ($LASTEXITCODE -ne 0) { throw "checkout develop failed" }

if ($Files) {
    git add @Files
} else {
    git add -A
}
if ($LASTEXITCODE -ne 0) { throw "git add failed" }

git commit -m $CommitMessage
if ($LASTEXITCODE -ne 0) { throw "git commit failed" }

git push origin develop
if ($LASTEXITCODE -ne 0) { throw "push to develop failed" }

git push origin develop:staging
if ($LASTEXITCODE -ne 0) { throw "push to staging failed" }

git push origin develop:main
if ($LASTEXITCODE -ne 0) { throw "push to main failed" }

Write-Host "Pushed to develop, staging, and main."
