"""
Менеджер напоминаний для хранения и управления напоминаниями пользователей
"""
from datetime import time
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class ReminderManager:
    """Класс для управления напоминаниями пользователей"""
    
    def __init__(self):
        """Инициализация менеджера напоминаний"""
        # Словарь для хранения напоминаний: {user_id: (reminder_time, chat_id)}
        self._reminders: Dict[int, Tuple[time, int]] = {}
    
    def set_reminder(self, user_id: int, reminder_time: time, chat_id: int) -> None:
        """
        Устанавливает напоминание для пользователя
        
        Args:
            user_id: ID пользователя
            reminder_time: Время напоминания
            chat_id: ID чата для отправки напоминания
        """
        self._reminders[user_id] = (reminder_time, chat_id)
        logger.info(f"Установлено напоминание для пользователя {user_id} на {reminder_time}")
    
    def remove_reminder(self, user_id: int) -> bool:
        """
        Удаляет напоминание пользователя
        
        Args:
            user_id: ID пользователя
            
        Returns:
            bool: True если напоминание было удалено, False если его не было
        """
        if user_id in self._reminders:
            del self._reminders[user_id]
            logger.info(f"Удалено напоминание для пользователя {user_id}")
            return True
        return False
    
    def has_reminder(self, user_id: int) -> bool:
        """
        Проверяет, есть ли у пользователя активное напоминание
        
        Args:
            user_id: ID пользователя
            
        Returns:
            bool: True если есть активное напоминание
        """
        return user_id in self._reminders
    
    def get_reminder(self, user_id: int) -> Optional[Tuple[time, int]]:
        """
        Получает напоминание пользователя
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Optional[Tuple[time, int]]: Кортеж (время, chat_id) или None
        """
        return self._reminders.get(user_id)
    
    def get_due_reminders(self, current_time: time) -> List[Tuple[int, int, time]]:
        """
        Получает список напоминаний, которые должны быть отправлены в текущее время
        
        Args:
            current_time: Текущее время для сравнения
            
        Returns:
            List[Tuple[int, int, time]]: Список кортежей (user_id, chat_id, reminder_time)
        """
        due_reminders = []
        
        for user_id, (reminder_time, chat_id) in self._reminders.items():
            # Сравниваем время с точностью до минуты
            if (reminder_time.hour == current_time.hour and 
                reminder_time.minute == current_time.minute):
                due_reminders.append((user_id, chat_id, reminder_time))
        
        return due_reminders
    
    def get_all_reminders(self) -> Dict[int, Tuple[time, int]]:
        """
        Получает все активные напоминания
        
        Returns:
            Dict[int, Tuple[time, int]]: Словарь всех напоминаний
        """
        return self._reminders.copy()
    
    def clear_all_reminders(self) -> int:
        """
        Очищает все напоминания
        
        Returns:
            int: Количество удаленных напоминаний
        """
        count = len(self._reminders)
        self._reminders.clear()
        logger.info(f"Очищены все напоминания ({count} шт.)")
        return count
    
    def get_reminders_count(self) -> int:
        """
        Получает количество активных напоминаний
        
        Returns:
            int: Количество активных напоминаний
        """
        return len(self._reminders)
