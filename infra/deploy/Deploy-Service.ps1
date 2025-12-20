# infra/deploy/Deploy-Service.ps1
# Stub script (Step 1): proves the runner can execute repo scripts on the server.

param(
  [Parameter(Mandatory)][ValidateSet("staging","prod")][string]$Env,     # Target environment
  [Parameter(Mandatory)][ValidateSet("auth","pdf-renderer","text2image")][string]$Service,  # Target service
  [Parameter(Mandatory)][string]$Version                                # Release version
)

Set-StrictMode -Version Latest  # Fail fast on script issues

Write-Host "Deploy stub running. Env=$Env Service=$Service Version=$Version"  # Visible in Actions logs

if ($CheckServy) {
  # Import the Servy helper module from lib/
  Import-Module "$PSScriptRoot\lib\Servy.Common.psm1" -Force

  # Verify servy-cli is installed and callable on this machine (the server runner)
  Assert-ServyAvailable

  Write-Host "Servy CLI is available."  # Confirmation in logs
}
