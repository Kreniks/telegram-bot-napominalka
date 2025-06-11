"""
Расширенная конфигурация для Telegram-бота "Напоминалка"
Включает дополнительные настройки для продакшена
"""
import os
import logging
from dotenv import load_dotenv
import pytz

# Загружаем переменные окружения
load_dotenv()

# Основные настройки бота
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в переменных окружения!")

# Настройки базы данных
DB_PATH = os.getenv('DB_PATH', 'reminders.db')
DB_BACKUP_ENABLED = os.getenv('DB_BACKUP_ENABLED', 'true').lower() == 'true'
DB_BACKUP_INTERVAL_HOURS = int(os.getenv('DB_BACKUP_INTERVAL_HOURS', '24'))
DB_CLEANUP_DAYS = int(os.getenv('DB_CLEANUP_DAYS', '30'))

# Часовой пояс
OMSK_TIMEZONE = pytz.timezone('Asia/Omsk')

# Настройки логирования
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'bot.log')
LOG_MAX_SIZE_MB = int(os.getenv('LOG_MAX_SIZE_MB', '10'))
LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', '5'))

# Настройки производительности
CHECK_INTERVAL_SECONDS = int(os.getenv('CHECK_INTERVAL_SECONDS', '60'))
MAX_CONCURRENT_REMINDERS = int(os.getenv('MAX_CONCURRENT_REMINDERS', '100'))
RATE_LIMIT_MESSAGES_PER_MINUTE = int(os.getenv('RATE_LIMIT_MESSAGES_PER_MINUTE', '30'))

# Настройки безопасности
ALLOWED_USERS = os.getenv('ALLOWED_USERS', '').split(',') if os.getenv('ALLOWED_USERS') else []
ADMIN_USER_ID = int(os.getenv('ADMIN_USER_ID', '0')) if os.getenv('ADMIN_USER_ID') else None
ENABLE_ANALYTICS = os.getenv('ENABLE_ANALYTICS', 'false').lower() == 'true'

# Настройки уведомлений
NOTIFICATION_RETRY_ATTEMPTS = int(os.getenv('NOTIFICATION_RETRY_ATTEMPTS', '3'))
NOTIFICATION_RETRY_DELAY_SECONDS = int(os.getenv('NOTIFICATION_RETRY_DELAY_SECONDS', '5'))

# Настройки мониторинга
HEALTH_CHECK_ENABLED = os.getenv('HEALTH_CHECK_ENABLED', 'true').lower() == 'true'
HEALTH_CHECK_PORT = int(os.getenv('HEALTH_CHECK_PORT', '8080'))
METRICS_ENABLED = os.getenv('METRICS_ENABLED', 'false').lower() == 'true'

# Расширенные сообщения
MESSAGES = {
    'start': (
        "🤖 Привет! Я бот-Напоминалка.\n\n"
        "📝 Напиши время в формате ЧЧ:ММ и дату в формате ДД.ММ.ГГГГ, "
        "например: '18:00 12.06.2025'\n\n"
        "⏰ Если дату не указать, я напомню сегодня.\n"
        "🌍 Все время по Омску (+6 UTC)!\n\n"
        "ℹ️ Используй /help для получения справки."
    ),
    'help': (
        "📖 СПРАВКА ПО БОТУ-НАПОМИНАЛКЕ\n\n"
        "🔹 Форматы времени:\n"
        "• '18:00' - напоминание на сегодня\n"
        "• '18:00 12.06.2025' - напоминание на конкретную дату\n\n"
        "🔹 Особенности:\n"
        "• Время указывается в 24-часовом формате\n"
        "• Дата в формате ДД.ММ.ГГГГ\n"
        "• Все время по Омску (+6 UTC)\n"
        "• Хранится только одно напоминание на пользователя\n\n"
        "🔹 Команды:\n"
        "• /start - запуск бота\n"
        "• /help - эта справка\n"
        "• /status - статус вашего напоминания"
    ),
    'invalid_format': (
        "❌ Неверный формат!\n\n"
        "Пожалуйста, укажи время в формате ЧЧ:ММ и дату в формате ДД.ММ.ГГГГ\n"
        "Примеры:\n"
        "• '18:00' (на сегодня)\n"
        "• '18:00 12.06.2025' (на конкретную дату)"
    ),
    'past_time': (
        "⏰ Это время уже прошло!\n\n"
        "Укажи будущее время и дату."
    ),
    'unknown_message': (
        "🤔 Я понимаю только время в формате ЧЧ:ММ и дату в формате ДД.ММ.ГГГГ\n\n"
        "Примеры:\n"
        "• '18:00 12.06.2025'\n"
        "• '09:30'\n\n"
        "Попробуй ещё раз или используй /help для справки!"
    ),
    'reminder_set_with_date': "✅ Ок, напомню {date} в {time} (по омскому времени)!",
    'reminder_set_today': "✅ Ок, напомню сегодня в {time} (по омскому времени)!",
    'reminder_text': "🔔 Напоминание!\n📅 {date} в {time}",
    'no_reminder': "ℹ️ У вас нет активных напоминаний.",
    'current_reminder': "📋 Ваше текущее напоминание:\n📅 {date} в {time} (по омскому времени)",
    'error_occurred': "❌ Произошла ошибка. Попробуйте позже.",
    'access_denied': "🚫 У вас нет доступа к этому боту.",
    'rate_limit': "⏳ Слишком много сообщений. Подождите немного."
}

# Настройки для разработки
DEBUG_MODE = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
TEST_MODE = os.getenv('TEST_MODE', 'false').lower() == 'true'

def setup_advanced_logging():
    """Расширенная настройка логирования с ротацией файлов"""
    from logging.handlers import RotatingFileHandler
    
    # Создаем форматтер
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    
    # Настраиваем корневой логгер
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, LOG_LEVEL.upper()))
    
    # Очищаем существующие обработчики
    root_logger.handlers.clear()
    
    # Обработчик для файла с ротацией
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=LOG_MAX_SIZE_MB * 1024 * 1024,
        backupCount=LOG_BACKUP_COUNT,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # Обработчик для консоли
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Настройка уровней для внешних библиотек
    logging.getLogger('aiohttp.access').setLevel(logging.WARNING)
    logging.getLogger('aiogram.event').setLevel(logging.WARNING)
    
    if not DEBUG_MODE:
        logging.getLogger('aiogram').setLevel(logging.WARNING)

def get_config_summary():
    """Получить сводку конфигурации для логирования"""
    return {
        'bot_token_set': bool(BOT_TOKEN),
        'db_path': DB_PATH,
        'log_level': LOG_LEVEL,
        'check_interval': CHECK_INTERVAL_SECONDS,
        'timezone': str(OMSK_TIMEZONE),
        'debug_mode': DEBUG_MODE,
        'test_mode': TEST_MODE,
        'backup_enabled': DB_BACKUP_ENABLED,
        'health_check_enabled': HEALTH_CHECK_ENABLED,
        'allowed_users_count': len(ALLOWED_USERS) if ALLOWED_USERS else 0,
        'admin_configured': bool(ADMIN_USER_ID)
    }
