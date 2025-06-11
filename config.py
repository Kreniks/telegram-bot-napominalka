"""
Конфигурация для Telegram-бота "Напоминалка"
"""
import os
import logging
from dotenv import load_dotenv
import pytz

# Загружаем переменные окружения
load_dotenv()

# Настройки бота
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в переменных окружения! Создайте файл .env и добавьте BOT_TOKEN=your_token_here")

# Настройки базы данных
DB_PATH = os.getenv('DB_PATH', 'reminders.db')

# Часовой пояс Омска (+6 UTC)
OMSK_TIMEZONE = pytz.timezone('Asia/Omsk')

# Настройки логирования
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Сообщения бота
MESSAGES = {
    'start': (
        "Привет! Я бот-Напоминалка. Напиши время в формате ЧЧ:ММ и дату в формате ДД.ММ.ГГГГ, "
        "например, '18:00 12.06.2025'. Если дату не указать, я напомню сегодня. "
        "Все время по Омску (+6)!"
    ),
    'help': (
        "Я бот-Напоминалка. Напиши время в формате ЧЧ:ММ и дату в формате ДД.ММ.ГГГГ, "
        "например, '18:00 12.06.2025'. Если дату не указать, напомню сегодня. "
        "Все время по Омску (+6)!"
    ),
    'invalid_format': (
        "Пожалуйста, укажи время в формате ЧЧ:ММ и дату в формате ДД.ММ.ГГГГ, "
        "например, '18:00 12.06.2025'."
    ),
    'past_time': "Это время уже прошло. Укажи будущее время и дату!",
    'unknown_message': (
        "Я понимаю только время в формате ЧЧ:ММ и дату в формате ДД.ММ.ГГГГ, "
        "например, '18:00 12.06.2025'. Попробуй ещё раз!"
    ),
    'reminder_set_with_date': "Ок, напомню {date} в {time} (по омскому времени)!",
    'reminder_set_today': "Ок, напомню сегодня в {time} (по омскому времени)!",
    'reminder_text': "Напоминание! {date} в {time}!"
}

def setup_logging():
    """Настройка логирования"""
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('bot.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    # Отключаем избыточное логирование от aiohttp
    logging.getLogger('aiohttp.access').setLevel(logging.WARNING)
