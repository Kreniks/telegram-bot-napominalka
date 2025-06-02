"""
Утилиты для работы со временем
"""
import re
from datetime import time
from typing import Optional


def validate_time_format(time_str: str) -> bool:
    """
    Проверяет корректность формата времени ЧЧ:ММ
    
    Args:
        time_str: Строка времени для проверки
        
    Returns:
        bool: True если формат корректный, False иначе
    """
    # Паттерн для формата ЧЧ:ММ
    pattern = r'^([0-1]?[0-9]|2[0-3]):([0-5][0-9])$'
    
    if not re.match(pattern, time_str):
        return False
    
    try:
        # Дополнительная проверка через парсинг
        parse_time_string(time_str)
        return True
    except ValueError:
        return False


def parse_time_string(time_str: str) -> time:
    """
    Парсит строку времени в объект time
    
    Args:
        time_str: Строка времени в формате ЧЧ:ММ
        
    Returns:
        time: Объект времени
        
    Raises:
        ValueError: Если формат времени некорректный
    """
    try:
        # Разделяем по двоеточию
        parts = time_str.split(':')
        
        if len(parts) != 2:
            raise ValueError("Неверный формат времени")
        
        hours = int(parts[0])
        minutes = int(parts[1])
        
        # Проверяем диапазоны
        if not (0 <= hours <= 23):
            raise ValueError("Часы должны быть в диапазоне 0-23")
        
        if not (0 <= minutes <= 59):
            raise ValueError("Минуты должны быть в диапазоне 0-59")
        
        return time(hour=hours, minute=minutes)
        
    except (ValueError, IndexError) as e:
        raise ValueError(f"Ошибка парсинга времени '{time_str}': {e}")


def format_time(time_obj: time) -> str:
    """
    Форматирует объект времени в строку ЧЧ:ММ
    
    Args:
        time_obj: Объект времени
        
    Returns:
        str: Отформатированная строка времени
    """
    return time_obj.strftime("%H:%M")


def is_time_equal(time1: time, time2: time) -> bool:
    """
    Сравнивает два времени с точностью до минуты
    
    Args:
        time1: Первое время
        time2: Второе время
        
    Returns:
        bool: True если времена равны (с точностью до минуты)
    """
    return (time1.hour == time2.hour and 
            time1.minute == time2.minute)
