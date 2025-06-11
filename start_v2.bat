@echo off
chcp 65001 >nul
title Запуск Telegram-бота v2.0 в Docker

echo.
echo ========================================
echo 🚀 Запуск Telegram-бота v2.0 в Docker
echo ========================================
echo.
echo ✨ Новые возможности v2.0:
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

REM Проверка Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker не найден! Установите Docker Desktop
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose не найден!
    pause
    exit /b 1
)

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

REM Остановка старых контейнеров
echo 🛑 Остановка старых контейнеров...
docker-compose down >nul 2>&1
docker-compose -f docker-compose.v2.yml down >nul 2>&1

echo 🔨 Сборка образа v2.0...
docker-compose -f docker-compose.v2.yml build telegram-bot-v2

if errorlevel 1 (
    echo ❌ Ошибка сборки образа!
    pause
    exit /b 1
)

echo 🚀 Запуск бота v2.0...
docker-compose -f docker-compose.v2.yml up -d telegram-bot-v2

if errorlevel 1 (
    echo ❌ Ошибка запуска контейнера!
    pause
    exit /b 1
)

echo.
echo ✅ Бот v2.0 успешно запущен!
echo.
echo 📊 Статус контейнера:
docker ps --filter "name=reminder-bot-v2" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo.
echo 📱 Найдите вашего бота в Telegram и отправьте /start
echo 📋 Попробуйте кнопку "Мои напоминания"
echo 📅 Протестируйте новые форматы: 18:00, 18:00 12.06, 18:00 12.06.25
echo.
echo 📝 Полезные команды:
echo   docker-compose -f docker-compose.v2.yml logs -f telegram-bot-v2  (логи)
echo   docker-compose -f docker-compose.v2.yml down                     (остановка)
echo.
echo 🛑 Для остановки закройте это окно или нажмите Ctrl+C
echo.

REM Показываем логи
echo 📋 Логи бота v2.0 (Ctrl+C для выхода):
echo ========================================
docker-compose -f docker-compose.v2.yml logs -f telegram-bot-v2
