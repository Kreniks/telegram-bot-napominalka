"""
Вспомогательные функции для парсинга времени и даты
"""
import re
import logging
from datetime import datetime, time, date
from typing import Optional, Tuple
from config import OMSK_TIMEZONE

logger = logging.getLogger(__name__)

# Регулярные выражения для парсинга
TIME_DATE_PATTERN = re.compile(r'^(\d{1,2}):(\d{2})\s+(\d{1,2})\.(\d{1,2})\.(\d{4})$')
TIME_ONLY_PATTERN = re.compile(r'^(\d{1,2}):(\d{2})$')


def parse_time_and_date(text: str) -> Optional[Tuple[datetime, bool]]:
    """
    Парсинг времени и даты из текста пользователя
    
    Args:
        text: Текст от пользователя (например, "18:00 12.06.2025" или "18:00")
        
    Returns:
        Optional[Tuple[datetime, bool]]: (datetime объект в часовом поясе Омска, is_today_only)
        None если формат неверный
    """
    text = text.strip()
    
    # Попробуем сначала формат "ЧЧ:ММ ДД.ММ.ГГГГ"
    match = TIME_DATE_PATTERN.match(text)
    if match:
        hour, minute, day, month, year = map(int, match.groups())
        
        # Валидация времени
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            logger.debug(f"Неверное время: {hour}:{minute}")
            return None
        
        # Валидация даты
        try:
            target_date = date(year, month, day)
        except ValueError:
            logger.debug(f"Неверная дата: {day}.{month}.{year}")
            return None
        
        # Создаем datetime объект
        try:
            target_time = time(hour, minute)
            target_datetime = datetime.combine(target_date, target_time)
            # Применяем часовой пояс Омска
            target_datetime = OMSK_TIMEZONE.localize(target_datetime)
            
            logger.debug(f"Распознано время с датой: {target_datetime}")
            return target_datetime, False
            
        except Exception as e:
            logger.error(f"Ошибка создания datetime: {e}")
            return None
    
    # Попробуем формат "ЧЧ:ММ" (только время, текущая дата)
    match = TIME_ONLY_PATTERN.match(text)
    if match:
        hour, minute = map(int, match.groups())
        
        # Валидация времени
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            logger.debug(f"Неверное время: {hour}:{minute}")
            return None
        
        # Используем текущую дату в часовом поясе Омска
        try:
            current_date = datetime.now(OMSK_TIMEZONE).date()
            target_time = time(hour, minute)
            target_datetime = datetime.combine(current_date, target_time)
            # Применяем часовой пояс Омска
            target_datetime = OMSK_TIMEZONE.localize(target_datetime)
            
            logger.debug(f"Распознано время на сегодня: {target_datetime}")
            return target_datetime, True
            
        except Exception as e:
            logger.error(f"Ошибка создания datetime для сегодня: {e}")
            return None
    
    logger.debug(f"Не удалось распознать формат: {text}")
    return None


def is_future_time(target_datetime: datetime) -> bool:
    """
    Проверка, что время в будущем
    
    Args:
        target_datetime: Время для проверки (с часовым поясом)
        
    Returns:
        bool: True если время в будущем
    """
    current_time = datetime.now(OMSK_TIMEZONE)
    return target_datetime > current_time


def format_datetime_for_user(dt: datetime) -> str:
    """
    Форматирование datetime для отображения пользователю
    
    Args:
        dt: datetime объект
        
    Returns:
        str: Отформатированная строка
    """
    return dt.strftime("%d.%m.%Y")


def format_time_for_user(dt: datetime) -> str:
    """
    Форматирование времени для отображения пользователю
    
    Args:
        dt: datetime объект
        
    Returns:
        str: Отформатированное время
    """
    return dt.strftime("%H:%M")


def get_current_omsk_time() -> datetime:
    """
    Получить текущее время в часовом поясе Омска
    
    Returns:
        datetime: Текущее время в Омске
    """
    return datetime.now(OMSK_TIMEZONE)


def validate_reminder_time(text: str) -> Tuple[Optional[datetime], str, bool]:
    """
    Полная валидация времени напоминания
    
    Args:
        text: Текст от пользователя
        
    Returns:
        Tuple[Optional[datetime], str, bool]: (datetime или None, сообщение об ошибке, is_today_only)
    """
    # Парсинг времени
    parsed_result = parse_time_and_date(text)
    if not parsed_result:
        return None, "invalid_format", False
    
    target_datetime, is_today_only = parsed_result
    
    # Проверка, что время в будущем
    if not is_future_time(target_datetime):
        return None, "past_time", is_today_only
    
    return target_datetime, "success", is_today_only
