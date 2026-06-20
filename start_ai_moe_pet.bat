@echo off
set "PY=%LOCALAPPDATA%\Programs\Python\Python312\pythonw.exe"
set "SCRIPT_DIR=%~dp0"
if exist "%SCRIPT_DIR%pet-shutdown.flag" del "%SCRIPT_DIR%pet-shutdown.flag"
start "" "%PY%" "%SCRIPT_DIR%nuomi_watchdog.py"
