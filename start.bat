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
    echo ERROR: Python is not installed!
    echo Please run Installer.bat first
    echo.
    pause
    exit /b 1
)

python -c "import aiohttp, colorama, certifi, requests" > nul 2> nul
if %errorlevel% neq 0 (
    echo ERROR: Some dependencies are missing!
    echo Please run Installer.bat first
    echo.
    pause
    exit /b 1
)

echo Starting Discord Server Cloner V3 - Blue Edition...
echo.
python channel_copier.py
pause