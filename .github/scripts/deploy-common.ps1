# Shared helpers for the _deploy.yml workflow.
# Dot-source it from a workflow step:  . .\.github\scripts\deploy-common.ps1
#
# Expects these environment variables (set at job level in _deploy.yml):
#   ENV_ROOT, WINSW_SUFFIX, REL_VERSION, HEALTH_PORT_BASE (health step only)

$ErrorActionPreference = 'Stop'
# PowerShell 7.4+: native commands (.exe) with a non-zero exit code throw.
$PSNativeCommandUseErrorActionPreference = $true

$EnvRoot   = $env:ENV_ROOT
$Suffix    = $env:WINSW_SUFFIX
$Version   = $env:REL_VERSION
$StateFile = Join-Path $env:RUNNER_TEMP 'deploy-state.json'

if ([string]::IsNullOrWhiteSpace($EnvRoot)) { throw "ENV_ROOT is empty" }
if ([string]::IsNullOrWhiteSpace($Version)) { throw "REL_VERSION is empty" }

$Out = Join-Path $env:GITHUB_WORKSPACE '_out'
$Services = @(
  @{ Name = 'auth';             Source = "$Out\auth\app";         Winsw = 'AuthService';        Venv = $false; PortOffset = 0 },
  @{ Name = 'pdf-renderer';     Source = "$Out\pdf-renderer\app"; Winsw = 'PdfRendererService'; Venv = $false; PortOffset = 1 },
  @{ Name = 'text2image';       Source = "$Out\text2image";       Winsw = 'Text2Image';         Venv = $true;  PortOffset = 2 },
  @{ Name = 'viber-automation'; Source = "$Out\viber-automation"; Winsw = 'ViberAutomation';    Venv = $true;  PortOffset = 3 }
)

function Get-SvcRoot($Svc)  { Join-Path $EnvRoot $Svc.Name }
function Get-WinswExe($Svc) { Join-Path (Get-SvcRoot $Svc) "winsw\$($Svc.Winsw)-$Suffix.exe" }

function Normalize-Path([string]$Path) {
  if ([string]::IsNullOrEmpty($Path)) { return $null }
  return ($Path -replace '^\\\?\?\\', '').TrimEnd('\')
}

function Ensure-Dirs($Svc) {
  $root = Get-SvcRoot $Svc
  foreach ($d in 'releases', 'shared\config', 'shared\logs', 'shared\data', 'winsw') {
    New-Item -ItemType Directory -Force -Path (Join-Path $root $d) | Out-Null
  }
}

# Returns the folder the "current" junction points to, or $null if there is none.
function Get-CurrentTarget($Svc) {
  $item = Get-Item -LiteralPath (Join-Path (Get-SvcRoot $Svc) 'current') -ErrorAction SilentlyContinue
  if (-not $item) { return $null }
  return Normalize-Path ([string]$item.Target)
}

# Repoints "current" to $Target and verifies the result.
function Set-CurrentJunction($Svc, [string]$Target) {
  $current = Join-Path (Get-SvcRoot $Svc) 'current'
  $item = Get-Item -LiteralPath $current -ErrorAction SilentlyContinue
  if ($item) {
    if ($item.LinkType -ne 'Junction') { throw "'$current' exists and is not a junction" }
    [System.IO.Directory]::Delete($current)   # removes only the junction, never the target contents
  }
  New-Item -ItemType Junction -Path $current -Target $Target | Out-Null
  if ((Get-CurrentTarget $Svc) -ne (Normalize-Path $Target)) {
    throw "Junction verification failed for $($Svc.Name): expected '$Target', got '$(Get-CurrentTarget $Svc)'"
  }
}

# WinSW 'stop' can return non-zero when the service is already stopped / not installed yet.
function Stop-Svc($Svc) {
  try { & (Get-WinswExe $Svc) stop }
  catch { Write-Warning "stop failed for $($Svc.Name) (maybe already stopped): $_" }
}
function Start-Svc($Svc) { & (Get-WinswExe $Svc) start }

function Wait-Health([string]$Url, [string]$Name) {
  for ($i = 1; $i -le 20; $i++) {
    try {
      $r = Invoke-RestMethod -Uri $Url -TimeoutSec 5
      Write-Host "$Name healthy: $r"
      return
    } catch {
      Write-Host "$Name attempt ${i}/20 failed: $($_.Exception.Message)"
      Start-Sleep -Seconds 3
    }
  }
  throw "$Name health check failed: $Url"
}
