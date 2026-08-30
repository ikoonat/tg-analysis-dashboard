$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'common.ps1')

Set-Location (Get-ProjectRoot)
Write-Host 'Telegram Collector - Python venv setup' -ForegroundColor Cyan
Ensure-Venv
Write-Host 'Installing packages into .venv...' -ForegroundColor Cyan
Install-Requirements
Write-Host ''
Write-Host 'Setup complete.' -ForegroundColor Green
Write-Host 'Run the collector with .\run-collector.ps1' -ForegroundColor White