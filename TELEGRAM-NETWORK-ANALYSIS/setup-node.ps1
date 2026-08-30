$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot

$node = Get-Command node -ErrorAction SilentlyContinue
$npm = Get-Command npm -ErrorAction SilentlyContinue
if (-not $node -or -not $npm) {
    throw 'Node.js and npm are required. Install Node.js from https://nodejs.org/, then reopen PowerShell.'
}

Write-Host "Node.js $(& node --version)" -ForegroundColor Green
Write-Host "npm $(& npm --version)" -ForegroundColor Green

Write-Host 'Creating the local Python .venv...' -ForegroundColor Cyan
& (Join-Path $PSScriptRoot 'setup-venv.ps1')
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host 'Installing dashboard packages into local node_modules...' -ForegroundColor Cyan
& npm install
if ($LASTEXITCODE -ne 0) { throw 'npm install failed.' }

Write-Host ''
Write-Host 'Setup complete. Start the dashboard with: npm run dev' -ForegroundColor Green
