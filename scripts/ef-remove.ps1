#!/usr/bin/env pwsh
# Usage: pwsh ef-remove.ps1
#
# Removes the last EF migration and its corresponding Flyway SQL file.
# Reverses what ef-migrate.ps1 created.

$Project   = "backend/shared/persistence/ContentProcessing.Persistence.csproj"
$Startup   = "backend/auth/AuthService/AuthService.csproj"
$Context   = "ContentProcessingDbContext"
$FlywayDir = "backend/shared/flyway-sql"

# Step 1 — Find the latest Flyway SQL file (highest version number)
$latestSql = Get-ChildItem "$FlywayDir/V*__*.sql" -ErrorAction SilentlyContinue |
    Sort-Object { if ($_.Name -match '^V(\d+)__') { [int]$Matches[1] } } |
    Select-Object -Last 1

# Step 2 — Remove the last EF C# migration
dotnet ef migrations remove `
    --project $Project `
    --startup-project $Startup `
    --context $Context `
    --force
if ($LASTEXITCODE -ne 0) { throw "dotnet ef migrations remove failed" }

# Step 3 — Delete the corresponding Flyway SQL file
if ($latestSql) {
    Remove-Item $latestSql.FullName
    Write-Host "Removed: $($latestSql.FullName)"
} else {
    Write-Host "No Flyway SQL file found to remove."
}