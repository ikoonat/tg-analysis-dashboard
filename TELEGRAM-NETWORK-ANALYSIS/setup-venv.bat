@echo off
set "ROOT=%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%ROOT%setup-venv.ps1" %*
exit /b %errorlevel%