# infra/deploy/Deploy-Service.ps1
# Stub script (Step 1): proves the runner can execute repo scripts on the server.

param(
  [Parameter(Mandatory)][ValidateSet("staging","prod")][string]$Env,     # Target environment
  [Parameter(Mandatory)][ValidateSet("auth","pdf-renderer","text2image")][string]$Service,  # Target service
  [Parameter(Mandatory)][string]$Version                                # Release version
)

Set-StrictMode -Version Latest  # Fail fast on script issues

Write-Host "Deploy stub running. Env=$Env Service=$Service Version=$Version"  # Visible in Actions logs

