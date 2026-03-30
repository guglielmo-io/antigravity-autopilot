@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "PY_SCRIPT=%SCRIPT_DIR%patch_antigravity.py"

if not exist "%PY_SCRIPT%" (
    echo [ERROR] patch_antigravity.py not found in %SCRIPT_DIR%
    exit /b 1
)

where python >nul 2>&1 && (
    python "%PY_SCRIPT%" %*
    exit /b %ERRORLEVEL%
)

where py >nul 2>&1 && (
    py "%PY_SCRIPT%" %*
    exit /b %ERRORLEVEL%
)

where python3 >nul 2>&1 && (
    python3 "%PY_SCRIPT%" %*
    exit /b %ERRORLEVEL%
)

echo [ERROR] Python not found. Install Python and try again.
exit /b 1
