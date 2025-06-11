"""
Конфигурация для Telegram-бота "Напоминалка" v2.0
"""
import os
import logging
from datetime import timezone, timedelta
from pathlib import Path

# Получение токена бота из переменных окружения
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в переменных окружения. Добавьте его в .env файл.")

# Часовой пояс Омска (+6 UTC)
OMSK_TIMEZONE = timezone(timedelta(hours=6))

# Пути к файлам
PROJECT_ROOT = Path(__file__).parent
DB_PATH = os.getenv('DB_PATH', PROJECT_ROOT / 'reminders.db')
LOG_FILE = os.getenv('LOG_FILE', PROJECT_ROOT / 'bot.log')

# Настройки логирования
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
LOG_MAX_SIZE_MB = int(os.getenv('LOG_MAX_SIZE_MB', '50'))
LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', '10'))
LOG_TO_STDOUT = os.getenv('LOG_TO_STDOUT', 'false').lower() == 'true'

# Настройки производительности
CHECK_INTERVAL_SECONDS = int(os.getenv('CHECK_INTERVAL_SECONDS', '60'))
NOTIFICATION_RETRY_ATTEMPTS = int(os.getenv('NOTIFICATION_RETRY_ATTEMPTS', '3'))
NOTIFICATION_RETRY_DELAY_SECONDS = int(os.getenv('NOTIFICATION_RETRY_DELAY_SECONDS', '5'))

# Настройки мониторинга
HEALTH_CHECK_ENABLED = os.getenv('HEALTH_CHECK_ENABLED', 'true').lower() == 'true'
HEALTH_CHECK_PORT = int(os.getenv('HEALTH_CHECK_PORT', '8080'))

# Сообщения бота
MESSAGES = {
    'start': (
        "🤖 Привет! Я бот-Напоминалка v2.0!\n\n"
        "✨ Новые возможности:\n"
        "• Множественные напоминания\n"
        "• Удобные кнопки управления\n"
        "• Расширенные форматы дат\n\n"
        "📝 Поддерживаемые форматы:\n"
        "• <code>18:00</code> - на сегодня\n"
        "• <code>18:00 12.06</code> - без года\n"
        "• <code>18:00 12.06.25</code> - короткий год\n"
        "• <code>18:00 12.06.2025</code> - полный формат\n\n"
        "🌍 Все время по Омску (+6 UTC)"
    ),
    'help': (
        "ℹ️ <b>Справка по боту-напоминалке v2.0</b>\n\n"
        "📝 <b>Поддерживаемые форматы:</b>\n"
        "• <code>18:00</code> - напоминание на сегодня\n"
        "• <code>18:00 12.06</code> - 12 июня текущего года\n"
        "• <code>18:00 12.06.25</code> - 12 июня 2025 года\n"
        "• <code>18:00 12.06.2025</code> - полный формат\n\n"
        "✨ <b>Возможности:</b>\n"
        "• Неограниченное количество напоминаний\n"
        "• Удобное управление через кнопки\n"
        "• Автоматическое определение года\n"
        "• Все время по Омску (+6 UTC)\n\n"
        "🔧 <b>Команды:</b>\n"
        "• /start - главное меню\n"
        "• /list - список напоминаний\n"
        "• /help - эта справка"
    ),
    'invalid_format': (
        "❌ Неверный формат!\n\n"
        "Поддерживаемые форматы:\n"
        "• <code>18:00</code> - на сегодня\n"
        "• <code>18:00 12.06</code> - без года\n"
        "• <code>18:00 12.06.25</code> - короткий год\n"
        "• <code>18:00 12.06.2025</code> - полный формат"
    ),
    'past_time': "⏰ Это время уже прошло!\n\nУкажите будущее время и дату.",
    'reminder_set': "✅ Напоминание установлено на {date} в {time}!",
    'reminder_sent': "🔔 <b>Напоминание!</b>\n📅 {date} в {time}",
    'error': "❌ Произошла ошибка. Попробуйте еще раз."
}


def setup_logging():
    """Настройка системы логирования"""
    # Создаем директорию для логов если её нет
    log_dir = Path(LOG_FILE).parent
    log_dir.mkdir(exist_ok=True)
    
    # Настройка форматирования
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Корневой логгер
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, LOG_LEVEL))
    
    # Очищаем существующие обработчики
    root_logger.handlers.clear()
    
    # Обработчик для файла с ротацией
    if LOG_FILE:
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(
            LOG_FILE,
            maxBytes=LOG_MAX_SIZE_MB * 1024 * 1024,
            backupCount=LOG_BACKUP_COUNT,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Обработчик для консоли
    if LOG_TO_STDOUT:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # Настройка уровня для aiogram
    logging.getLogger('aiogram').setLevel(logging.WARNING)
    logging.getLogger('aiohttp').setLevel(logging.WARNING)


# Инициализация логирования при импорте модуля
setup_logging()
