@echo off
chcp 65001 >nul
title Discord Server Cloner V3

echo.
echo ========================================
echo    Discord Server Cloner V3
echo ========================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed!
    echo Please run Installer.bat first
    echo.
    pause
    exit /b 1
)

:: Check if dependencies are installed
python -c "import aiohttp, colorama, certifi, requests" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Some dependencies are missing!
    echo Please run Installer.bat first
    echo.
    pause
    exit /b 1
)

echo Starting Discord Server Cloner V3...
echo.
python channel_copier.py
pause