@echo off
setlocal

:: Try repo venv first (portable)
if exist "%~dp0..\.venv\Scripts\python.exe" (
    "%~dp0..\.venv\Scripts\python.exe" "%~dp0manifest_gate.py" %*
    exit /b %ERRORLEVEL%
)
if exist "%~dp0..\venv\Scripts\python.exe" (
    "%~dp0..\venv\Scripts\python.exe" "%~dp0manifest_gate.py" %*
    exit /b %ERRORLEVEL%
)

:: Try hermes agent venv (common Cursor AI dev setup)
if exist "%LOCALAPPDATA%\hermes\hermes-agent\venv\Scripts\python.exe" (
    "%LOCALAPPDATA%\hermes\hermes-agent\venv\Scripts\python.exe" "%~dp0manifest_gate.py" %*
    exit /b %ERRORLEVEL%
)

:: Fall back to py launcher (Windows Python Launcher — most reliably on PATH)
py "%~dp0manifest_gate.py" %*
exit /b %ERRORLEVEL%
