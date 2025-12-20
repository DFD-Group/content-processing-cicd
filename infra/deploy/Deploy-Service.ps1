# infra/deploy/Deploy-Service.ps1
# Stub script (Step 1): proves the runner can execute repo scripts on the server.

param(
  [Parameter(Mandatory)][ValidateSet("staging","prod")][string]$Env,     # Target environment
  [Parameter(Mandatory)][ValidateSet("auth","pdf-renderer","text2image")][string]$Service,  # Target service
  [Parameter(Mandatory)][string]$Version                                # Release version
  [Parameter()][switch]$CheckServy # Optional flag: when supplied, verify servy-cli is available
)

Set-StrictMode -Version Latest  # Fail fast on script issues

Write-Host "Deploy stub running. Env=$Env Service=$Service Version=$Version"  # Visible in Actions logs

# Important: use PSBoundParameters to avoid StrictMode errors in case the flag is not present
if ($PSBoundParameters.ContainsKey('CheckServy')) {

  # Import Servy helper module from infra/deploy/lib
  Import-Module "$PSScriptRoot\lib\Servy.Common.psm1" -Force

  # Verify Servy CLI exists on this machine (the staging server runner)
  Assert-ServyAvailable

  Write-Host "Servy CLI is available."  # Confirmation in logs
}
