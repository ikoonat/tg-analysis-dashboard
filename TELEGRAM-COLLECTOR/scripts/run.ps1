param(
	[switch]$NoProgressBackup
)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'common.ps1')

Set-Location (Get-ProjectRoot)
Ensure-Venv
$pythonArgs = @()
if ($NoProgressBackup) { $pythonArgs += '--no-progress-backup' }
& (Get-VenvPython) 'collector.py' @pythonArgs
exit $LASTEXITCODE