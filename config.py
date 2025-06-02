"""
Конфигурация для Telegram-бота "Напоминалка"
"""
import os
from pathlib import Path

# Пытаемся загрузить python-dotenv
try:
    from dotenv import load_dotenv
    # Загружаем переменные окружения из .env файла
    env_path = Path('.') / '.env'
    load_dotenv(dotenv_path=env_path, encoding='utf-8')
    print("✅ .env файл загружен успешно")
except ImportError:
    print("⚠️ python-dotenv не установлен, используем системные переменные")
except Exception as e:
    print(f"⚠️ Ошибка загрузки .env файла: {e}")

# Получаем токен бота
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Дополнительная проверка - читаем .env файл напрямую если токен не найден
if not BOT_TOKEN:
    try:
        env_file = Path('.env')
        if env_file.exists():
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('BOT_TOKEN='):
                        BOT_TOKEN = line.split('=', 1)[1].strip()
                        print("✅ Токен найден в .env файле")
                        break
    except Exception as e:
        print(f"❌ Ошибка чтения .env файла: {e}")

print(f"🔑 Токен статус: {'✅ Найден' if BOT_TOKEN else '❌ Не найден'}")

# Настройки логирования
LOGGING_LEVEL = 'INFO'

# Настройки времени
TIMEZONE = 'UTC'  # По умолчанию UTC
CHECK_INTERVAL = 60  # Интервал проверки напоминаний в секундах

# Сообщения бота
MESSAGES = {
    'start': "Привет! Я бот-напоминалка. Введи время в формате ЧЧ:ММ, и я напомню тебе, когда оно наступит!",
    'help': "Инструкция по использованию:\n\n"
            "• Введи время в формате ЧЧ:ММ (например, 19:00)\n"
            "• Используй /cancel для отмены напоминания\n"
            "• Используй /help для повторного просмотра инструкции",
    'time_set': "Напоминание установлено на {time}. Я сообщу, когда время наступит!",
    'time_error': "Пожалуйста, введи время в формате ЧЧ:ММ, например, 19:00",
    'reminder': "Напоминание! Время {time}!",
    'cancelled': "Напоминание отменено",
    'no_reminders': "Нет активных напоминаний"
}

# Проверка наличия токена
if not BOT_TOKEN:
    print("❌ ОШИБКА: BOT_TOKEN не найден!")
    print("📋 Инструкция по настройке:")
    print("1. Откройте файл .env")
    print("2. Убедитесь, что строка выглядит так: BOT_TOKEN=ваш_токен_здесь")
    print("3. Получите токен от @BotFather в Telegram")
    print("4. Замените 'ваш_токен_здесь' на реальный токен")
    raise ValueError("BOT_TOKEN не найден в переменных окружения. Настройте .env файл с токеном бота.")

# Проверка корректности токена (базовая)
if BOT_TOKEN and len(BOT_TOKEN) < 20:
    print("⚠️ ВНИМАНИЕ: Токен выглядит некорректно (слишком короткий)")
    print("Токен должен быть примерно такой: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz")

print("🚀 Конфигурация загружена успешно!")
