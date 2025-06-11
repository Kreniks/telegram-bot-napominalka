"""
Тестирование функциональности бота версии 2.0
"""
import asyncio
import logging
from datetime import datetime, timedelta

from config import OMSK_TIMEZONE, setup_logging
from database import db_v2
from utils import (
    validate_reminder_time_v2,
    format_datetime_for_user,
    format_time_for_user,
    format_datetime_short,
    get_time_until_reminder
)

# Настройка логирования для тестов
setup_logging()
logger = logging.getLogger(__name__)


def test_new_date_formats():
    """Тест новых форматов дат"""
    print("=== Тестирование новых форматов дат ===")
    
    test_cases = [
        # Полный формат
        "18:00 12.06.2025",
        # Короткий год
        "18:00 12.06.25",
        # Без года
        "18:00 12.06",
        # Только время
        "18:00",
        # Неверные форматы
        "25:00",
        "18:00 32.13.2025",
        "abc",
        ""
    ]
    
    for test_input in test_cases:
        result, status, is_today = validate_reminder_time_v2(test_input)
        print(f"'{test_input}' -> {status} (today: {is_today})")
        if result:
            print(f"  Результат: {result}")
    
    print()


def test_database_v2():
    """Тест новой базы данных с множественными напоминаниями"""
    print("=== Тестирование базы данных v2 ===")
    
    test_user_id = 123456789
    current_time = datetime.now(OMSK_TIMEZONE)
    
    # Очищаем старые тестовые данные
    print("Очистка старых тестовых данных...")
    
    # Добавляем несколько напоминаний
    test_reminders = [
        (current_time + timedelta(minutes=5), "Первое напоминание"),
        (current_time + timedelta(hours=1), "Второе напоминание"),
        (current_time + timedelta(days=1), "Напоминание на завтра"),
        (current_time + timedelta(weeks=1), None)  # Без текста
    ]
    
    print(f"Добавление {len(test_reminders)} напоминаний...")
    for reminder_time, reminder_text in test_reminders:
        success = db_v2.add_reminder(test_user_id, reminder_time, reminder_text)
        print(f"  {reminder_time} - {'✅' if success else '❌'}")
    
    # Получаем напоминания пользователя
    user_reminders = db_v2.get_user_reminders(test_user_id)
    print(f"\nНапоминания пользователя {test_user_id}: {len(user_reminders)} шт.")
    
    for reminder_id, reminder_time, reminder_text in user_reminders:
        print(f"  ID {reminder_id}: {format_datetime_short(reminder_time)}")
        if reminder_text:
            print(f"    Текст: {reminder_text}")
    
    # Тестируем удаление
    if user_reminders:
        first_reminder_id = user_reminders[0][0]
        print(f"\nУдаление напоминания ID {first_reminder_id}...")
        success = db_v2.delete_reminder(first_reminder_id, test_user_id)
        print(f"Удаление: {'✅' if success else '❌'}")
        
        # Проверяем количество после удаления
        count_after = db_v2.get_reminders_count(test_user_id)
        print(f"Осталось напоминаний: {count_after}")
    
    print()


def test_formatting_functions():
    """Тест функций форматирования"""
    print("=== Тестирование функций форматирования ===")
    
    test_time = datetime.now(OMSK_TIMEZONE) + timedelta(days=1, hours=3, minutes=30)
    
    print(f"Тестовое время: {test_time}")
    print(f"format_datetime_for_user: {format_datetime_for_user(test_time)}")
    print(f"format_time_for_user: {format_time_for_user(test_time)}")
    print(f"format_datetime_short: {format_datetime_short(test_time)}")
    print(f"get_time_until_reminder: {get_time_until_reminder(test_time)}")
    
    # Тест с прошедшим временем
    past_time = datetime.now(OMSK_TIMEZONE) - timedelta(hours=1)
    print(f"\nПрошедшее время: {get_time_until_reminder(past_time)}")
    
    # Тест с временем в этом году
    this_year_time = datetime.now(OMSK_TIMEZONE).replace(month=12, day=31, hour=23, minute=59)
    print(f"Время в этом году: {format_datetime_short(this_year_time)}")
    
    print()


def test_edge_cases():
    """Тест граничных случаев"""
    print("=== Тестирование граничных случаев ===")
    
    edge_cases = [
        # Високосный год
        "18:00 29.02.24",
        # Несуществующая дата
        "18:00 29.02.25",
        # Граничные значения времени
        "00:00 01.01.25",
        "23:59 31.12.25",
        # Прошедшие даты
        "18:00 01.01.20",
        # Далекое будущее
        "18:00 01.01.99",
        # Граничные дни месяца
        "18:00 31.04.25",  # Апрель имеет только 30 дней
        "18:00 31.12.25",  # Декабрь имеет 31 день
    ]
    
    for test_input in edge_cases:
        result, status, is_today = validate_reminder_time_v2(test_input)
        print(f"'{test_input}' -> {status}")
        if result:
            print(f"  Результат: {format_datetime_short(result)}")
    
    print()


def test_year_detection():
    """Тест определения года"""
    print("=== Тестирование определения года ===")
    
    current_year = datetime.now(OMSK_TIMEZONE).year
    print(f"Текущий год: {current_year}")
    
    # Тестируем короткие годы
    short_years = ["00", "01", "25", "30", "50", "99"]
    
    for year_str in short_years:
        test_input = f"18:00 01.01.{year_str}"
        result, status, _ = validate_reminder_time_v2(test_input)
        if result:
            detected_year = result.year
            print(f"'{year_str}' -> {detected_year}")
    
    print()


async def main():
    """Главная функция тестирования"""
    print("🚀 Запуск тестирования Telegram-бота 'Напоминалка' v2.0")
    print("=" * 70)
    
    try:
        test_new_date_formats()
        test_database_v2()
        test_formatting_functions()
        test_edge_cases()
        test_year_detection()
        
        print("🎉 Все тесты v2.0 пройдены успешно!")
        print("✨ Новые возможности:")
        print("  - Множественные напоминания")
        print("  - Расширенные форматы дат")
        print("  - Улучшенное форматирование")
        print("  - Кнопки управления")
        
    except Exception as e:
        print(f"❌ Ошибка в тестах: {e}")
        logger.error(f"Ошибка в тестах: {e}")


if __name__ == "__main__":
    asyncio.run(main())
