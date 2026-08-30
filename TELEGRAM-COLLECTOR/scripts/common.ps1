Set-StrictMode -Version Latest

$script:ProjectRoot = Split-Path -Parent $PSScriptRoot
$script:VenvPath = Join-Path $script:ProjectRoot '.venv'
$script:VenvPython = Join-Path $script:VenvPath 'Scripts\python.exe'

function Get-ProjectRoot { return $script:ProjectRoot }
function Get-VenvPython { return $script:VenvPython }

function Ensure-Venv {
    if (Test-Path $script:VenvPython) { return }

    $pyLauncher = Get-Command py -ErrorAction SilentlyContinue
    if ($pyLauncher) {
        & $pyLauncher.Source -3.11 -m venv $script:VenvPath
        if ($LASTEXITCODE -ne 0) {
            & $pyLauncher.Source -3 -m venv $script:VenvPath
        }
    } else {
        $python = Get-Command python -ErrorAction SilentlyContinue
        if (-not $python) {
            throw 'Python 3 is required. Install Python from https://www.python.org/downloads/.'
        }
        & $python.Source -m venv $script:VenvPath
    }

    if ($LASTEXITCODE -ne 0 -or -not (Test-Path $script:VenvPython)) {
        throw 'Unable to create .venv.'
    }
}

function Install-Requirements {
    $requirements = Join-Path $script:ProjectRoot 'requirements.txt'
    & $script:VenvPython -m pip install --upgrade pip
    if ($LASTEXITCODE -ne 0) { throw 'Unable to upgrade pip in .venv.' }

    & $script:VenvPython -m pip install -r $requirements
    if ($LASTEXITCODE -ne 0) { throw 'Unable to install requirements into .venv.' }
}