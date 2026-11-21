@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Avvia-HOLO.ps1" %*
set "HOLO_EXIT_CODE=%ERRORLEVEL%"
if not "%HOLO_EXIT_CODE%"=="0" pause
exit /b %HOLO_EXIT_CODE%
