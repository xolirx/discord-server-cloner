@echo off
chcp 65001 >nul
title Discord Server Cloner V6.2.0

if not exist "venv" (
    echo Virtual environment not found!
    echo Run install.bat to set up dependencies
    pause
    exit /b 1
)

if not exist "venv\Scripts\python.exe" (
    echo Python not found in virtual environment!
    echo Run install.bat to set up dependencies
    pause
    exit /b 1
)

echo Starting Discord Server Cloner...
echo.

call venv\Scripts\python.exe channel_copier.py

if errorlevel 1 (
    echo.
    echo Program exited with an error
    echo Check error_log.txt for details
)

echo.
pause