# infra/deploy/lib/Servy.Common.psm1
# Minimal Servy helper (Step 1): only checks that servy-cli is installed on the server runner.

Set-StrictMode -Version Latest  # Fail fast

function Get-ServyCliPath {
  # Prefer default install location; fallback to PATH
  $default = "C:\Program Files\Servy\servy-cli.exe"
  if (Test-Path $default) { return $default }
  return "servy-cli.exe"
}

function Assert-ServyAvailable {
  # Throws if Servy is not present on the server runner
  $cli = Get-ServyCliPath
  & $cli --version | Out-Null
}

Export-ModuleMember -Function *

