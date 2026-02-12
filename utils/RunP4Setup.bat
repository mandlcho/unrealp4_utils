@echo off
title P4 Context Menu Setup
echo ================================================
echo P4 Context Menu Setup Tool
echo ================================================
echo.
echo Initializing...
echo.

REM Change to the script directory
cd /d "%~dp0"

REM Run the Python setup tool
python P4MenuSetup.py

if errorlevel 1 (
    echo.
    echo ================================================
    echo ERROR: Failed to run setup tool
    echo ================================================
    echo.
    echo Please ensure:
    echo   - Python 3.7+ is installed
    echo   - Python is in your system PATH
    echo.
    echo You can download Python from: https://www.python.org/
    echo.
    pause
    exit /b 1
)

echo.
echo Setup tool closed.
pause
