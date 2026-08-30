$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'scripts\common.ps1')
Set-Location (Get-ProjectRoot)
Ensure-Venv
. (Join-Path (Get-ProjectRoot) '.venv\Scripts\Activate.ps1')
Write-Host 'Activated .venv. Run: python collector.py' -ForegroundColor Green