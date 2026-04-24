@echo off
setlocal

echo Starting Enemy Fight Planner Preview...

:: Check if npm is available in PATH
where npm >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo.
    echo ERROR: 'npm' is not recognized.
    echo Node.js does not appear to be installed, or it is not in your system's PATH.
    echo Please install Node.js from https://nodejs.org/ or run this script from a Terminal where Node is accessible.
    echo.
    goto end
)

cd enemy-fight-planner

echo Installing dependencies...
call npm install

echo Launching web preview server...
call npm run dev

:end
pause
