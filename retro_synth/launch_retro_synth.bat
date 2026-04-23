@echo off
echo =========================================
echo    Retro Synth Workstation Launcher
echo =========================================

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Error: Python is not installed or not in PATH.
    pause
    goto :EOF
)

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo Initializing virtual environment...
    python.exe -m venv venv
    if %ERRORLEVEL% neq 0 (
        echo Error: Failed to create virtual environment.
        pause
        goto :EOF
    )
    call venv\Scripts\activate.bat
    echo Installing dependencies...
    pip install -e .[dev]
) else (
    call venv\Scripts\activate.bat
)

echo Starting Retro Synth...
retro-synth
pause
