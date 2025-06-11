#!/bin/bash
set -e

# Docker entrypoint скрипт для Telegram-бота "Напоминалка"
# Обеспечивает правильную инициализацию и запуск в production

echo "🚀 Запуск Telegram-бота 'Напоминалка' в Docker контейнере"
echo "============================================================"

# Функция логирования
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Проверка обязательных переменных окружения
check_env() {
    log "Проверка переменных окружения..."
    
    if [ -z "$BOT_TOKEN" ]; then
        log "❌ ОШИБКА: BOT_TOKEN не установлен!"
        log "Получите токен у @BotFather и установите переменную BOT_TOKEN"
        exit 1
    fi
    
    log "✅ BOT_TOKEN установлен"
    
    # Проверяем формат токена (базовая валидация)
    if [[ ! $BOT_TOKEN =~ ^[0-9]+:[A-Za-z0-9_-]+$ ]]; then
        log "⚠️ ПРЕДУПРЕЖДЕНИЕ: Формат BOT_TOKEN может быть неверным"
    fi
}

# Создание необходимых директорий
setup_directories() {
    log "Создание директорий..."
    
    mkdir -p /app/data /app/logs /app/backups
    
    # Проверяем права доступа
    if [ ! -w /app/data ]; then
        log "❌ ОШИБКА: Нет прав записи в /app/data"
        exit 1
    fi
    
    log "✅ Директории созданы и доступны для записи"
}

# Инициализация базы данных
init_database() {
    log "Инициализация базы данных..."
    
    # Проверяем, существует ли база данных
    if [ ! -f "$DB_PATH" ]; then
        log "Создание новой базы данных: $DB_PATH"
        python -c "
from database import db
print('База данных инициализирована успешно')
"
        if [ $? -eq 0 ]; then
            log "✅ База данных создана успешно"
        else
            log "❌ ОШИБКА: Не удалось создать базу данных"
            exit 1
        fi
    else
        log "✅ База данных уже существует: $DB_PATH"
    fi
}

# Проверка подключения к Telegram API
test_bot_connection() {
    log "Проверка подключения к Telegram API..."
    
    python -c "
import asyncio
from aiogram import Bot
from config import BOT_TOKEN

async def test_connection():
    bot = Bot(token=BOT_TOKEN)
    try:
        me = await bot.get_me()
        print(f'✅ Подключение успешно! Бот: @{me.username} ({me.first_name})')
        return True
    except Exception as e:
        print(f'❌ Ошибка подключения: {e}')
        return False
    finally:
        await bot.session.close()

result = asyncio.run(test_connection())
exit(0 if result else 1)
" 2>/dev/null

    if [ $? -eq 0 ]; then
        log "✅ Подключение к Telegram API успешно"
    else
        log "❌ ОШИБКА: Не удалось подключиться к Telegram API"
        log "Проверьте BOT_TOKEN и интернет-соединение"
        exit 1
    fi
}

# Запуск тестов (если включено)
run_tests() {
    if [ "$RUN_TESTS" = "true" ]; then
        log "Запуск тестов..."
        python test_bot.py
        if [ $? -eq 0 ]; then
            log "✅ Все тесты пройдены"
        else
            log "❌ ОШИБКА: Тесты не пройдены"
            exit 1
        fi
    fi
}

# Создание backup базы данных
create_backup() {
    if [ "$CREATE_BACKUP" = "true" ] && [ -f "$DB_PATH" ]; then
        log "Создание backup базы данных..."
        backup_file="/app/backups/reminders_$(date +%Y%m%d_%H%M%S).db"
        cp "$DB_PATH" "$backup_file"
        log "✅ Backup создан: $backup_file"
    fi
}

# Настройка логирования
setup_logging() {
    log "Настройка логирования..."
    
    # Создаем символическую ссылку для вывода логов в stdout
    if [ "$LOG_TO_STDOUT" = "true" ]; then
        ln -sf /dev/stdout /app/logs/bot.log
        log "✅ Логи будут выводиться в stdout"
    fi
}

# Запуск health check сервера (если включен)
start_health_check() {
    if [ "$HEALTH_CHECK_ENABLED" = "true" ]; then
        log "Запуск health check сервера на порту $HEALTH_CHECK_PORT..."
        python -c "
import asyncio
from aiohttp import web
import json
from datetime import datetime

async def health_check(request):
    return web.json_response({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'telegram-reminder-bot'
    })

async def init_app():
    app = web.Application()
    app.router.add_get('/health', health_check)
    return app

if __name__ == '__main__':
    web.run_app(init_app(), host='0.0.0.0', port=${HEALTH_CHECK_PORT})
" &
        log "✅ Health check сервер запущен"
    fi
}

# Определение режима запуска
determine_run_mode() {
    case "${RUN_MODE:-normal}" in
        "advanced")
            BOT_SCRIPT="bot_advanced.py"
            log "🔧 Режим: Расширенная версия бота"
            ;;
        "monitor")
            BOT_SCRIPT="monitor.py"
            log "📊 Режим: Мониторинг"
            ;;
        "test")
            BOT_SCRIPT="test_bot.py"
            log "🧪 Режим: Тестирование"
            ;;
        *)
            BOT_SCRIPT="main.py"
            log "🤖 Режим: Стандартная версия бота"
            ;;
    esac
}

# Главная функция
main() {
    log "Начало инициализации..."
    
    # Выполняем все проверки и настройки
    check_env
    setup_directories
    setup_logging
    init_database
    test_bot_connection
    run_tests
    create_backup
    start_health_check
    determine_run_mode
    
    log "✅ Инициализация завершена успешно"
    log "🚀 Запуск бота: $BOT_SCRIPT"
    log "============================================================"
    
    # Запускаем бота
    exec python "$BOT_SCRIPT"
}

# Обработка сигналов для graceful shutdown
cleanup() {
    log "🛑 Получен сигнал остановки, завершение работы..."
    # Здесь можно добавить логику для graceful shutdown
    exit 0
}

trap cleanup SIGTERM SIGINT

# Запуск
main "$@"
