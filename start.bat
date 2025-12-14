@echo off
chcp 65001 > nul
title Discord Server Cloner V3 - Blue Edition

echo.
echo ========================================
echo    Discord Server Cloner V3 - Blue Edition
echo ========================================
echo.

python --version > nul 2> nul
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH!
    echo.
    echo Please install Python 3.8+ from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation!
    echo.
    pause
    exit /b 1
)

echo Checking Python version...
python -c "import sys; print(f'Python {sys.version}')"

echo.
echo Checking dependencies...
python -c "import aiohttp, colorama" > nul 2> nul
if %errorlevel% neq 0 (
    echo ERROR: Some Python dependencies are missing!
    echo.
    echo Please run Installer.bat first to install dependencies.
    echo.
    pause
    exit /b 1
)

echo All dependencies found!
echo.
echo Starting Discord Server Cloner V3 - Blue Edition...
echo ========================================
echo.

timeout /t 2 > nul
python channel_copier.py

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Program exited with error code %errorlevel%
    echo.
    pause
    exit /b %errorlevel%
)

pause