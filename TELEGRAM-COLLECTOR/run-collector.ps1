param(
	[switch]$NoProgressBackup
)
$ErrorActionPreference = 'Stop'

$pythonArgs = @()
if ($NoProgressBackup) { $pythonArgs += '--no-progress-backup' }
& (Join-Path $PSScriptRoot 'scripts\run.ps1') @pythonArgs
exit $LASTEXITCODE