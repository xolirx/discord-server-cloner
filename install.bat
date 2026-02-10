@echo off
chcp 65001 >nul
title Discord Server Cloner V5 - Установка
color 0B

echo ═════════════════════════════════════════════════════════════
echo                  Установка Discord Server Cloner
echo                     Версия 5.1.0 by qtiq0
echo ═════════════════════════════════════════════════════════════
echo.

echo [*] Проверка наличия Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [-] Python не найден!
    echo [*] Скачайте и установите Python 3.8+ с официального сайта:
    echo [*] https://python.org/downloads/
    echo [*] Не забудьте поставить галочку "Add Python to PATH"
    pause
    exit /b 1
)

echo [+] Python найден
python --version

echo.
echo [*] Создание виртуального окружения...
python -m venv venv
if errorlevel 1 (
    echo [-] Ошибка создания виртуального окружения
    echo [*] Попробуйте выполнить: python -m pip install virtualenv
    echo [*] Затем снова запустите install.bat
    pause
    exit /b 1
)

echo [+] Виртуальное окружение создано

echo.
echo [*] Активация виртуального окружения...
if not exist "venv\Scripts\activate.bat" (
    echo [-] Файл активации не найден
    echo [*] Попробуйте удалить папку venv и запустить заново
    pause
    exit /b 1
)

echo.
echo [*] Обновление pip внутри виртуального окружения...
call venv\Scripts\python.exe -m pip install --upgrade pip
if errorlevel 1 (
    echo [-] Ошибка обновления pip
    echo [*] Пропускаем обновление...
)

echo.
echo [*] Установка зависимостей...
call venv\Scripts\python.exe -m pip install colorama>=0.4.6 requests>=2.31.0 aiohttp>=3.9.0

if errorlevel 1 (
    echo [-] Ошибка установки зависимостей
    echo [*] Попробуйте выполнить вручную:
    echo [*] venv\Scripts\python.exe -m pip install colorama requests aiohttp
    pause
    exit /b 1
)

echo [+] Зависимости установлены

echo.
echo [*] Проверка установки...
call venv\Scripts\python.exe -c "import colorama, requests, aiohttp; print('[+] Все модули успешно импортированы')"

echo.
echo ═════════════════════════════════════════════════════════════
echo                    УСТАНОВКА ЗАВЕРШЕНА
echo ═════════════════════════════════════════════════════════════
echo.
echo [*] Для запуска программы используйте start.bat
echo [*] Или запустите вручную: venv\Scripts\python.exe channel_copier.py
echo.
echo [*] Поддержка: Telegram @qtiq0 | Discord zlafik
echo [*] При обнаружении ошибок пишите автору
echo.
pause