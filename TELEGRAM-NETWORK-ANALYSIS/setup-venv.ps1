$ErrorActionPreference = 'Stop'
$projectRoot = $PSScriptRoot
$venvPath = Join-Path $projectRoot '.venv'
$venvPython = Join-Path $venvPath 'Scripts\python.exe'

if (-not (Test-Path $venvPython)) {
    $pyLauncher = Get-Command py -ErrorAction SilentlyContinue
    if ($pyLauncher) {
        & $pyLauncher.Source -3.11 -m venv $venvPath
        if ($LASTEXITCODE -ne 0) { & $pyLauncher.Source -3 -m venv $venvPath }
    } else {
        $python = Get-Command python -ErrorAction SilentlyContinue
        if (-not $python) { throw 'Python 3 is required to create this project venv.' }
        & $python.Source -m venv $venvPath
    }
}

if ($LASTEXITCODE -ne 0 -or -not (Test-Path $venvPython)) {
    throw 'Unable to create TELEGRAM-NETWORK-ANALYSIS\.venv.'
}

Write-Host "Created $venvPath" -ForegroundColor Green
Write-Host 'This project uses npm for its application dependencies.' -ForegroundColor Cyan