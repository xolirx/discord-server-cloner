@echo off
chcp 65001 >nul
title Discord Server Cloner V6.2.0 - Installation

echo Installing Discord Server Cloner
echo.

echo Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found!
    echo Download Python 3.8+ from python.org
    pause
    exit /b 1
)

python --version
echo.

echo Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo Failed to create virtual environment
    pause
    exit /b 1
)
echo OK
echo.

echo Updating pip...
call venv\Scripts\python.exe -m pip install --upgrade pip >nul 2>&1
echo OK
echo.

echo Installing dependencies...
call venv\Scripts\python.exe -m pip install colorama requests aiohttp
if errorlevel 1 (
    echo Failed to install dependencies
    pause
    exit /b 1
)
echo OK
echo.

echo Installation complete!
echo Use start.bat to launch the program
echo.

pause