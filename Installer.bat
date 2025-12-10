@echo off
chcp 65001 > nul
title Installing Dependencies

echo.
echo ========================================
echo    Installing Dependencies
echo ========================================
echo.

python --version > nul 2> nul
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed!
    echo.
    echo Download and install Python from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation!
    echo.
    pause
    exit /b 1
)

echo Installing required packages...
echo.

python -m pip install --upgrade pip

pip install aiohttp
pip install colorama
pip install certifi
pip install requests

echo.
echo ========================================
echo    Dependencies installed successfully!
echo ========================================
echo.
echo Now you can run start.bat
echo.
pause