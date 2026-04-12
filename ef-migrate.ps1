#!/usr/bin/env pwsh
# Usage: pwsh ef-migrate.ps1 AddUserProfiles
#
# 1. Creates the EF C# migration (C# files kept in git)
# 2. Generates Flyway-ready SQL (auto-versioned, cleaned)

param(
    [Parameter(Mandatory)]
    [string]$MigrationName
)

# Verify that dotnet-ef CLI tool is installed
dotnet ef --version > $null 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Error "EF Core CLI tools not found. Install with: dotnet tool install --global dotnet-ef"
    exit 1
}

$Project  = "backend/shared/persistence/ContentProcessing.Persistence.csproj"
$Startup  = "backend/auth/AuthService/AuthService.csproj"
$Context  = "ContentProcessingDbContext"
$FlywayDir = "backend/shared/flyway-sql"

# Step 1 — Capture last existing migration (before adding new one)
#   Files look like: 20260411120000_AddNewEntity.cs
#   Exclude Designer.cs and Snapshot.cs
$lastMigration = Get-ChildItem "$FlywayDir/../persistence/Migrations/*_*.cs" -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -notmatch 'Designer|Snapshot' } |
    Sort-Object Name |
    Select-Object -Last 1 |
    ForEach-Object { $_.BaseName }   # e.g. "20260411120000_AddNewEntity"

# Step 2 — Generate C# migration (no DB connection needed)
dotnet ef migrations add $MigrationName `
    --project $Project `
    --startup-project $Startup `
    --context $Context
if ($LASTEXITCODE -ne 0) { throw "dotnet ef migrations add failed" }

# Step 3 — Find next Flyway version number
#   Scans V1__xxx.sql, V2__xxx.sql, etc. and picks max + 1
$lastVersion = Get-ChildItem "$FlywayDir/V*__*.sql" -ErrorAction SilentlyContinue |
    ForEach-Object { if ($_.Name -match '^V(\d+)__') { [int]$Matches[1] } } |
    Sort-Object |
    Select-Object -Last 1
$nextVersion = ($lastVersion ?? 0) + 1

# Step 4 — Convert PascalCase to snake_case for Flyway filename
#   AddUserProfiles → add_user_profiles
$snakeName = ($MigrationName -creplace '([A-Z])', '_$1').TrimStart('_').ToLower()

$outputFile = "$FlywayDir/V${nextVersion}__${snakeName}.sql"

# Step 5 — Generate SQL (incremental if previous migration exists)
#   "0" means "from empty database" (first migration)
$from = if ($lastMigration) { $lastMigration } else { "0" }

$sql = dotnet ef migrations script $from `
    --project $Project `
    --startup-project $Startup `
    --context $Context
if ($LASTEXITCODE -ne 0) { throw "dotnet ef migrations script failed" }

# Step 6 — Strip EF history table lines and write Flyway file
$raw = $sql -join "`n"

# Remove everything before START TRANSACTION (EF history table, build output)
$raw = $raw -replace '(?s)^.*?(?=START TRANSACTION;)', ''

# Remove INSERT INTO / VALUES for EF history
$raw = $raw -replace '(?m)^.*__EFMigrationsHistory.*$', ''
$raw = $raw -replace "(?m)^VALUES\s*\(.*?\);.*$", ''
# Clean up excessive blank lines (3+ newlines → 2)
$raw = $raw -replace '(\r?\n){3,}', "`n`n"
$raw = $raw.Trim()

Set-Content -Path $outputFile -Value $raw -Encoding utf8

Write-Host "Created: $outputFile"