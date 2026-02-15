@echo off
chcp 65001 >nul
title Discord Server Cloner V6.0.0
color 0B

echo ═════════════════════════════════════════════════════════════
echo                     Discord Server Cloner V6.0.0
echo                      Автор: xolirx
echo ═════════════════════════════════════════════════════════════
echo.

if not exist "venv" (
    echo [-] Виртуальное окружение не найдено!
    echo [*] Запустите install.bat для установки зависимостей
    echo.
    pause
    exit /b 1
)

if not exist "venv\Scripts\python.exe" (
    echo [-] Python в виртуальном окружении не найден!
    echo [*] Запустите install.bat для установки зависимостей
    echo.
    pause
    exit /b 1
)

echo [*] Проверка зависимостей...
call venv\Scripts\python.exe -c "import colorama, requests, aiohttp" 2>nul
if errorlevel 1 (
    echo [-] Зависимости не установлены!
    echo [*] Запустите install.bat для установки зависимостей
    echo.
    pause
    exit /b 1
)

echo [+] Все зависимости установлены
echo [*] Версия: 5.1.0
echo [*] Автор: qtiq0
echo [*] Поддержка: Telegram @xolirx
echo.
echo [*] Запуск программы...
timeout /t 2 /nobreak >nul
echo.

call venv\Scripts\python.exe channel_copier.py

if errorlevel 1 (
    echo.
    echo [-] Программа завершилась с ошибкой
    echo [*] Проверьте установку зависимостей
    echo [*] Если проблема повторяется, напишите автору: @qtiq0
)

echo.
pause