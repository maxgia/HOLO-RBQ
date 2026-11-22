@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Ambiente Python non trovato. Avvia prima Avvia-HOLO.cmd per prepararlo, poi ferma il server.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" seed_demo.py --apply
set "HOLO_DEMO_EXIT=%ERRORLEVEL%"
pause
exit /b %HOLO_DEMO_EXIT%
