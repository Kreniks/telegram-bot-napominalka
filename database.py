"""
Модуль для работы с базой данных напоминаний
"""
import sqlite3
import logging
from datetime import datetime
from typing import Optional, List, Tuple
from config import DB_PATH, OMSK_TIMEZONE

logger = logging.getLogger(__name__)


class ReminderDatabase:
    """Класс для работы с базой данных напоминаний"""
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Инициализация базы данных"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS reminders (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        reminder_time TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        is_sent BOOLEAN DEFAULT FALSE
                    )
                ''')
                conn.commit()
                logger.info("База данных инициализирована")
        except Exception as e:
            logger.error(f"Ошибка инициализации базы данных: {e}")
            raise
    
    def add_reminder(self, user_id: int, reminder_time: datetime) -> bool:
        """
        Добавить напоминание для пользователя (заменяет старое)
        
        Args:
            user_id: ID пользователя Telegram
            reminder_time: Время напоминания в часовом поясе Омска
            
        Returns:
            bool: True если успешно добавлено
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Удаляем старые напоминания пользователя
                cursor.execute('DELETE FROM reminders WHERE user_id = ?', (user_id,))
                
                # Добавляем новое напоминание
                cursor.execute('''
                    INSERT INTO reminders (user_id, reminder_time, created_at)
                    VALUES (?, ?, ?)
                ''', (
                    user_id,
                    reminder_time.isoformat(),
                    datetime.now(OMSK_TIMEZONE).isoformat()
                ))
                
                conn.commit()
                logger.info(f"Добавлено напоминание для пользователя {user_id} на {reminder_time}")
                return True
                
        except Exception as e:
            logger.error(f"Ошибка добавления напоминания: {e}")
            return False
    
    def get_due_reminders(self) -> List[Tuple[int, int, datetime]]:
        """
        Получить напоминания, которые нужно отправить
        
        Returns:
            List[Tuple[int, int, datetime]]: Список (id, user_id, reminder_time)
        """
        try:
            current_time = datetime.now(OMSK_TIMEZONE)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, user_id, reminder_time
                    FROM reminders
                    WHERE is_sent = FALSE AND reminder_time <= ?
                ''', (current_time.isoformat(),))
                
                results = []
                for row in cursor.fetchall():
                    reminder_id, user_id, reminder_time_str = row
                    reminder_time = datetime.fromisoformat(reminder_time_str)
                    results.append((reminder_id, user_id, reminder_time))
                
                return results
                
        except Exception as e:
            logger.error(f"Ошибка получения напоминаний: {e}")
            return []
    
    def mark_reminder_sent(self, reminder_id: int) -> bool:
        """
        Отметить напоминание как отправленное
        
        Args:
            reminder_id: ID напоминания
            
        Returns:
            bool: True если успешно обновлено
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE reminders 
                    SET is_sent = TRUE 
                    WHERE id = ?
                ''', (reminder_id,))
                conn.commit()
                
                logger.info(f"Напоминание {reminder_id} отмечено как отправленное")
                return True
                
        except Exception as e:
            logger.error(f"Ошибка обновления напоминания: {e}")
            return False
    
    def get_user_reminder(self, user_id: int) -> Optional[datetime]:
        """
        Получить активное напоминание пользователя
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Optional[datetime]: Время напоминания или None
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT reminder_time
                    FROM reminders
                    WHERE user_id = ? AND is_sent = FALSE
                ''', (user_id,))
                
                result = cursor.fetchone()
                if result:
                    return datetime.fromisoformat(result[0])
                return None
                
        except Exception as e:
            logger.error(f"Ошибка получения напоминания пользователя: {e}")
            return None
    
    def cleanup_old_reminders(self, days_old: int = 7):
        """
        Очистка старых отправленных напоминаний
        
        Args:
            days_old: Количество дней для хранения старых напоминаний
        """
        try:
            cutoff_time = datetime.now(OMSK_TIMEZONE).replace(hour=0, minute=0, second=0, microsecond=0)
            cutoff_time = cutoff_time.replace(day=cutoff_time.day - days_old)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    DELETE FROM reminders
                    WHERE is_sent = TRUE AND created_at < ?
                ''', (cutoff_time.isoformat(),))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                if deleted_count > 0:
                    logger.info(f"Удалено {deleted_count} старых напоминаний")
                    
        except Exception as e:
            logger.error(f"Ошибка очистки старых напоминаний: {e}")


# Глобальный экземпляр базы данных
db = ReminderDatabase()
