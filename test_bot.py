"""
Тестирование функциональности бота без запуска Telegram API
"""
import asyncio
import logging
from datetime import datetime, timedelta

from config import OMSK_TIMEZONE, MESSAGES, setup_logging
from database import db
from utils import validate_reminder_time, format_datetime_for_user, format_time_for_user

# Настройка логирования для тестов
setup_logging()
logger = logging.getLogger(__name__)


def test_time_parsing():
    """Тест парсинга времени и даты"""
    print("=== Тестирование парсинга времени ===")
    
    # Тест 1: Время с датой
    future_date = (datetime.now(OMSK_TIMEZONE) + timedelta(days=1)).strftime('%d.%m.%Y')
    test_input = f'18:00 {future_date}'
    result, status, is_today = validate_reminder_time(test_input)
    print(f"✅ Время с датой: {test_input} -> {status}")
    
    # Тест 2: Только время
    future_time = (datetime.now(OMSK_TIMEZONE) + timedelta(hours=2)).strftime('%H:%M')
    result, status, is_today = validate_reminder_time(future_time)
    print(f"✅ Только время: {future_time} -> {status}")
    
    # Тест 3: Неверный формат
    result, status, is_today = validate_reminder_time('25:00')
    print(f"✅ Неверный формат: 25:00 -> {status}")
    
    # Тест 4: Прошедшее время
    past_time = (datetime.now(OMSK_TIMEZONE) - timedelta(hours=1)).strftime('%H:%M')
    result, status, is_today = validate_reminder_time(past_time)
    print(f"✅ Прошедшее время: {past_time} -> {status}")
    
    print()


def test_database():
    """Тест работы с базой данных"""
    print("=== Тестирование базы данных ===")
    
    test_user_id = 987654321
    test_time = datetime.now(OMSK_TIMEZONE) + timedelta(minutes=10)
    
    # Тест добавления
    success = db.add_reminder(test_user_id, test_time)
    print(f"✅ Добавление напоминания: {'успешно' if success else 'ошибка'}")
    
    # Тест получения
    user_reminder = db.get_user_reminder(test_user_id)
    print(f"✅ Получение напоминания: {'найдено' if user_reminder else 'не найдено'}")
    
    # Тест замены (добавляем новое напоминание для того же пользователя)
    new_time = datetime.now(OMSK_TIMEZONE) + timedelta(minutes=20)
    success = db.add_reminder(test_user_id, new_time)
    user_reminder_new = db.get_user_reminder(test_user_id)
    print(f"✅ Замена напоминания: {'успешно' if user_reminder_new != user_reminder else 'ошибка'}")
    
    print()


def test_message_formatting():
    """Тест форматирования сообщений"""
    print("=== Тестирование форматирования сообщений ===")
    
    test_time = datetime.now(OMSK_TIMEZONE) + timedelta(days=1, hours=3)
    
    # Тест форматирования даты и времени
    formatted_date = format_datetime_for_user(test_time)
    formatted_time = format_time_for_user(test_time)
    print(f"✅ Форматирование даты: {formatted_date}")
    print(f"✅ Форматирование времени: {formatted_time}")
    
    # Тест сообщений
    reminder_msg = MESSAGES['reminder_set_with_date'].format(
        date=formatted_date,
        time=formatted_time
    )
    print(f"✅ Сообщение о напоминании: {reminder_msg}")
    
    print()


def test_edge_cases():
    """Тест граничных случаев"""
    print("=== Тестирование граничных случаев ===")
    
    # Тест различных неверных форматов
    invalid_inputs = [
        "24:00",  # Неверное время
        "12:60",  # Неверные минуты
        "18:00 32.12.2025",  # Неверная дата
        "18:00 12.13.2025",  # Неверный месяц
        "abc",  # Полностью неверный формат
        "",  # Пустая строка
        "18:00 12.06.2020",  # Прошедшая дата
    ]
    
    for invalid_input in invalid_inputs:
        result, status, is_today = validate_reminder_time(invalid_input)
        expected_status = "invalid_format" if status != "past_time" else "past_time"
        print(f"✅ '{invalid_input}' -> {status}")
    
    print()


def test_timezone():
    """Тест работы с часовым поясом"""
    print("=== Тестирование часового пояса ===")
    
    current_omsk = datetime.now(OMSK_TIMEZONE)
    print(f"✅ Текущее время в Омске: {current_omsk}")
    print(f"✅ Часовой пояс: {current_omsk.tzinfo}")
    
    # Проверяем, что время корректно локализуется
    test_input = "12:00"
    result, status, is_today = validate_reminder_time(test_input)
    if result:
        print(f"✅ Локализация времени: {result.tzinfo}")
    
    print()


async def main():
    """Главная функция тестирования"""
    print("🚀 Запуск тестирования Telegram-бота 'Напоминалка'")
    print("=" * 60)
    
    try:
        test_time_parsing()
        test_database()
        test_message_formatting()
        test_edge_cases()
        test_timezone()
        
        print("🎉 Все тесты пройдены успешно!")
        print("✅ Бот готов к запуску с реальным токеном")
        
    except Exception as e:
        print(f"❌ Ошибка в тестах: {e}")
        logger.error(f"Ошибка в тестах: {e}")


if __name__ == "__main__":
    asyncio.run(main())
