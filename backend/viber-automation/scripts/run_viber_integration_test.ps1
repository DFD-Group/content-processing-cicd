param(
    [string]$ChatName = "Калибровка #CAL-0001",

    [Parameter(Mandatory = $true)]
    [string]$Message
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path `
    $PSScriptRoot `
    -Parent

$CurrentRoot = Split-Path `
    $ProjectRoot `
    -Parent

$PythonExe = Join-Path `
    $CurrentRoot `
    "venv\Scripts\python.exe"

if (!(Test-Path $PythonExe)) {
    throw "Python executable not found: $PythonExe"
}

chcp 65001 | Out-Null

$env:PYTHONUTF8 = "1"
$env:RUN_VIBER_INTEGRATION = "1"
$env:VIBER_TEST_CHAT = $ChatName
$env:VIBER_TEST_MESSAGE = $Message

Push-Location $ProjectRoot

try {
    Write-Host "Starting Viber integration test."
    Write-Host "Chat: $ChatName"
    Write-Host "Message: $Message"

    & $PythonExe -m unittest discover `
        -s tests `
        -p "test_viber_integration.py" `
        -v

    if ($LASTEXITCODE -ne 0) {
        throw "Viber integration test failed."
    }

    Write-Host "Viber integration test completed successfully."
}
finally {
    Pop-Location

    Remove-Item Env:RUN_VIBER_INTEGRATION `
        -ErrorAction SilentlyContinue

    Remove-Item Env:VIBER_TEST_CHAT `
        -ErrorAction SilentlyContinue

    Remove-Item Env:VIBER_TEST_MESSAGE `
        -ErrorAction SilentlyContinue
}