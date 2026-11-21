@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Avvia-HOLO.ps1" -ConfigureDatabase
set "HOLO_EXIT_CODE=%ERRORLEVEL%"
pause
exit /b %HOLO_EXIT_CODE%
