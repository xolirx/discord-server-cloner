@echo off
chcp 65001 > nul
title Installing Dependencies - Discord Server Cloner

echo.
echo ========================================
echo    Installing Dependencies
echo ========================================
echo.

echo Checking Python installation...
python --version > nul 2> nul
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Python is not installed or not in PATH!
    echo.
    echo Please install Python 3.8 or newer from:
    echo https://www.python.org/downloads/
    echo.
    echo IMPORTANT: During installation, check "Add Python to PATH"!
    echo.
    pause
    exit /b 1
)

python -c "import sys; print(f'Python {sys.version}')"

echo.
echo ========================================
echo    Installing Required Packages
echo ========================================
echo.

echo Upgrading pip...
python -m pip install --upgrade pip --quiet

echo.
echo Installing packages from requirements.txt...
if exist requirements.txt (
    pip install -r requirements.txt
) else (
    echo requirements.txt not found, installing manually...
    pip install aiohttp colorama
)

echo.
echo ========================================
echo    Verification
echo ========================================
echo.

echo Checking installed packages...
python -c "
try:
    import aiohttp, colorama
    print('✓ All packages installed successfully!')
except ImportError as e:
    print(f'✗ Missing package: {e}')
    exit(1)
"

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to install all packages!
    echo Please check your internet connection and try again.
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo    Installation Complete!
echo ========================================
echo.
echo You can now run the program:
echo 1. Make sure you have a Discord token
echo 2. Run start.bat
echo 3. Follow the instructions
echo.
echo For help, read Инструкция.txt
echo.
pause