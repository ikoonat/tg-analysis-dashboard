# Run as Administrator
# PowerShell script to install NVM for Windows

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "NVM for Windows Installer" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    pause
    exit
}

# Download NVM installer
$nvmVersion = "1.1.12"
$installerUrl = "https://github.com/coreybutler/nvm-windows/releases/download/$nvmVersion/nvm-setup.exe"
$installerPath = "$env:TEMP\nvm-setup.exe"

Write-Host "Downloading NVM for Windows v$nvmVersion..." -ForegroundColor Green
try {
    Invoke-WebRequest -Uri $installerUrl -OutFile $installerPath
    Write-Host "Download complete!" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "Starting installer..." -ForegroundColor Yellow
    Start-Process -FilePath $installerPath -Wait
    
    Write-Host ""
    Write-Host "Installation complete!" -ForegroundColor Green
    Write-Host "Please restart your terminal/PowerShell" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "After restarting, run: nvm version" -ForegroundColor Cyan
}
catch {
    Write-Host "ERROR: Failed to download NVM installer" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}

pause