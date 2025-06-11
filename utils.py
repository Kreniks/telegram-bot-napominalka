"""
Обновленные вспомогательные функции для парсинга времени и даты (версия 2.0)
Поддерживает расширенные форматы дат
"""
import re
import logging
from datetime import datetime, time, date
from typing import Optional, Tuple
from config import OMSK_TIMEZONE

logger = logging.getLogger(__name__)

# Регулярные выражения для парсинга (обновленные)
TIME_DATE_FULL_PATTERN = re.compile(r'^(\d{1,2}):(\d{2})\s+(\d{1,2})\.(\d{1,2})\.(\d{4})$')  # 18:00 12.06.2025
TIME_DATE_SHORT_PATTERN = re.compile(r'^(\d{1,2}):(\d{2})\s+(\d{1,2})\.(\d{1,2})\.(\d{2})$')  # 18:00 12.06.25
TIME_DATE_NO_YEAR_PATTERN = re.compile(r'^(\d{1,2}):(\d{2})\s+(\d{1,2})\.(\d{1,2})$')        # 18:00 12.06
TIME_ONLY_PATTERN = re.compile(r'^(\d{1,2}):(\d{2})$')                                        # 18:00


def parse_time_and_date_v2(text: str) -> Optional[Tuple[datetime, bool]]:
    """
    Расширенный парсинг времени и даты из текста пользователя
    
    Поддерживаемые форматы:
    - "18:00 12.06.2025" - полный формат
    - "18:00 12.06.25" - короткий год
    - "18:00 12.06" - без года (текущий год)
    - "18:00" - только время (сегодня)
    
    Args:
        text: Текст от пользователя
        
    Returns:
        Optional[Tuple[datetime, bool]]: (datetime объект в часовом поясе Омска, is_today_only)
        None если формат неверный
    """
    text = text.strip()
    current_year = datetime.now(OMSK_TIMEZONE).year
    
    # Попробуем полный формат "ЧЧ:ММ ДД.ММ.ГГГГ"
    match = TIME_DATE_FULL_PATTERN.match(text)
    if match:
        hour, minute, day, month, year = map(int, match.groups())
        return _create_datetime(hour, minute, day, month, year, False)
    
    # Попробуем короткий год "ЧЧ:ММ ДД.ММ.ГГ"
    match = TIME_DATE_SHORT_PATTERN.match(text)
    if match:
        hour, minute, day, month, year_short = map(int, match.groups())
        # Преобразуем двузначный год в четырехзначный
        if year_short <= 30:  # 00-30 считаем 2000-2030
            year = 2000 + year_short
        else:  # 31-99 считаем 1931-1999 (но это вряд ли будет использоваться для напоминаний)
            year = 1900 + year_short
        return _create_datetime(hour, minute, day, month, year, False)
    
    # Попробуем без года "ЧЧ:ММ ДД.ММ"
    match = TIME_DATE_NO_YEAR_PATTERN.match(text)
    if match:
        hour, minute, day, month = map(int, match.groups())
        year = current_year
        
        # Если дата уже прошла в этом году, используем следующий год
        try:
            target_date = date(year, month, day)
            current_date = datetime.now(OMSK_TIMEZONE).date()
            
            if target_date < current_date:
                year += 1
                logger.debug(f"Дата {day}.{month} уже прошла в {current_year}, используем {year}")
        except ValueError:
            pass  # Обработаем ошибку в _create_datetime
        
        return _create_datetime(hour, minute, day, month, year, False)
    
    # Попробуем формат "ЧЧ:ММ" (только время, текущая дата)
    match = TIME_ONLY_PATTERN.match(text)
    if match:
        hour, minute = map(int, match.groups())
        
        # Используем текущую дату в часовом поясе Омска
        current_datetime = datetime.now(OMSK_TIMEZONE)
        current_date = current_datetime.date()
        
        return _create_datetime(hour, minute, current_date.day, current_date.month, current_date.year, True)
    
    logger.debug(f"Не удалось распознать формат: {text}")
    return None


def _create_datetime(hour: int, minute: int, day: int, month: int, year: int, is_today_only: bool) -> Optional[Tuple[datetime, bool]]:
    """
    Создать datetime объект с валидацией
    
    Args:
        hour, minute, day, month, year: Компоненты даты и времени
        is_today_only: Флаг "только время"
        
    Returns:
        Optional[Tuple[datetime, bool]]: (datetime, is_today_only) или None при ошибке
    """
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
        
        logger.debug(f"Создан datetime: {target_datetime} (is_today_only: {is_today_only})")
        return target_datetime, is_today_only
        
    except Exception as e:
        logger.error(f"Ошибка создания datetime: {e}")
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


def format_datetime_short(dt: datetime) -> str:
    """
    Короткое форматирование даты и времени
    
    Args:
        dt: datetime объект
        
    Returns:
        str: Короткая строка "ДД.ММ в ЧЧ:ММ"
    """
    current_year = datetime.now(OMSK_TIMEZONE).year
    if dt.year == current_year:
        return dt.strftime("%d.%m в %H:%M")
    else:
        return dt.strftime("%d.%m.%Y в %H:%M")


def get_current_omsk_time() -> datetime:
    """
    Получить текущее время в часовом поясе Омска
    
    Returns:
        datetime: Текущее время в Омске
    """
    return datetime.now(OMSK_TIMEZONE)


def validate_reminder_time_v2(text: str) -> Tuple[Optional[datetime], str, bool]:
    """
    Полная валидация времени напоминания (версия 2.0)
    
    Args:
        text: Текст от пользователя
        
    Returns:
        Tuple[Optional[datetime], str, bool]: (datetime или None, сообщение об ошибке, is_today_only)
    """
    # Парсинг времени
    parsed_result = parse_time_and_date_v2(text)
    if not parsed_result:
        return None, "invalid_format", False
    
    target_datetime, is_today_only = parsed_result
    
    # Проверка, что время в будущем
    if not is_future_time(target_datetime):
        return None, "past_time", is_today_only
    
    return target_datetime, "success", is_today_only


def get_time_until_reminder(reminder_time: datetime) -> str:
    """
    Получить строку "через сколько времени" до напоминания
    
    Args:
        reminder_time: Время напоминания
        
    Returns:
        str: Строка типа "через 2 часа 30 минут"
    """
    current_time = datetime.now(OMSK_TIMEZONE)
    if reminder_time <= current_time:
        return "уже прошло"
    
    delta = reminder_time - current_time
    
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    
    parts = []
    if days > 0:
        parts.append(f"{days} дн.")
    if hours > 0:
        parts.append(f"{hours} ч.")
    if minutes > 0:
        parts.append(f"{minutes} мин.")
    
    if not parts:
        return "менее минуты"
    
    return "через " + " ".join(parts)
