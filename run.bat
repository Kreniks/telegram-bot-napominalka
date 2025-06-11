@echo off
chcp 65001 >nul
title Telegram-бот "Напоминалка" v2.0

echo.
echo ========================================
echo 🚀 Telegram-бот "Напоминалка" v2.0
echo ========================================
echo.
echo ✨ Новые возможности:
echo   - Множественные напоминания
echo   - Кнопки управления  
echo   - Расширенные форматы дат
echo.
echo 📝 Поддерживаемые форматы:
echo   - 18:00 (на сегодня)
echo   - 18:00 12.06 (без года)
echo   - 18:00 12.06.25 (короткий год)
echo   - 18:00 12.06.2025 (полный формат)
echo.
echo ========================================
echo.

REM Проверка наличия Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python не найден! Установите Python 3.8+
    pause
    exit /b 1
)

REM Проверка виртуального окружения
if not exist "venv\Scripts\activate.bat" (
    echo 🔧 Создание виртуального окружения...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Ошибка создания виртуального окружения
        pause
        exit /b 1
    )
)

REM Активация виртуального окружения
echo 🔧 Активация виртуального окружения...
call venv\Scripts\activate.bat

REM Установка зависимостей
echo 🔧 Проверка зависимостей...
pip install -r requirements.txt --quiet

REM Проверка .env файла
if not exist ".env" (
    echo.
    echo ⚠️  Файл .env не найден!
    echo 📝 Создайте .env файл на основе .env.example
    echo 🤖 Получите токен у @BotFather в Telegram
    echo.
    pause
    exit /b 1
)

REM Проверка токена в .env
findstr /C:"BOT_TOKEN=" .env >nul
if errorlevel 1 (
    echo.
    echo ⚠️  BOT_TOKEN не найден в .env файле!
    echo 🤖 Добавьте строку: BOT_TOKEN=ваш_токен_от_BotFather
    echo.
    pause
    exit /b 1
)

findstr /C:"BOT_TOKEN=your_bot_token_here" .env >nul
if not errorlevel 1 (
    echo.
    echo ⚠️  Замените your_bot_token_here на реальный токен!
    echo 🤖 Получите токен у @BotFather в Telegram
    echo.
    pause
    exit /b 1
)

echo ✅ Конфигурация проверена
echo.
echo 🚀 Запуск бота v2.0...
echo 📱 Найдите вашего бота в Telegram и отправьте /start
echo 🛑 Для остановки нажмите Ctrl+C
echo.

REM Запуск бота v2.0
python main_v2.py

echo.
echo 🛑 Бот остановлен
pause
