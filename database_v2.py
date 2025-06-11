"""
Обновленный модуль для работы с базой данных напоминаний (версия 2.0)
Поддерживает множественные напоминания на пользователя
"""
import sqlite3
import logging
from datetime import datetime
from typing import Optional, List, Tuple
from config import DB_PATH, OMSK_TIMEZONE

logger = logging.getLogger(__name__)


class ReminderDatabaseV2:
    """Класс для работы с базой данных напоминаний (версия 2.0)"""
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Инициализация базы данных с новой структурой"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Создаем новую таблицу с поддержкой множественных напоминаний
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS reminders_v2 (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        reminder_time TEXT NOT NULL,
                        reminder_text TEXT,
                        created_at TEXT NOT NULL,
                        is_sent BOOLEAN DEFAULT FALSE,
                        UNIQUE(user_id, reminder_time)
                    )
                ''')
                
                # Миграция данных из старой таблицы (если существует)
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='reminders'")
                if cursor.fetchone():
                    logger.info("Найдена старая таблица, выполняем миграцию...")
                    cursor.execute('''
                        INSERT OR IGNORE INTO reminders_v2 (user_id, reminder_time, created_at, is_sent)
                        SELECT user_id, reminder_time, created_at, is_sent FROM reminders
                    ''')
                    logger.info("Миграция данных завершена")
                
                conn.commit()
                logger.info("База данных v2 инициализирована")
        except Exception as e:
            logger.error(f"Ошибка инициализации базы данных: {e}")
            raise
    
    def add_reminder(self, user_id: int, reminder_time: datetime, reminder_text: str = None) -> bool:
        """
        Добавить напоминание для пользователя
        
        Args:
            user_id: ID пользователя Telegram
            reminder_time: Время напоминания в часовом поясе Омска
            reminder_text: Дополнительный текст напоминания (опционально)
            
        Returns:
            bool: True если успешно добавлено
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Добавляем новое напоминание (или заменяем существующее на то же время)
                cursor.execute('''
                    INSERT OR REPLACE INTO reminders_v2 (user_id, reminder_time, reminder_text, created_at)
                    VALUES (?, ?, ?, ?)
                ''', (
                    user_id,
                    reminder_time.isoformat(),
                    reminder_text,
                    datetime.now(OMSK_TIMEZONE).isoformat()
                ))
                
                conn.commit()
                logger.info(f"Добавлено напоминание для пользователя {user_id} на {reminder_time}")
                return True
                
        except Exception as e:
            logger.error(f"Ошибка добавления напоминания: {e}")
            return False
    
    def get_user_reminders(self, user_id: int) -> List[Tuple[int, datetime, str]]:
        """
        Получить все активные напоминания пользователя
        
        Args:
            user_id: ID пользователя
            
        Returns:
            List[Tuple[int, datetime, str]]: Список (id, reminder_time, reminder_text)
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, reminder_time, reminder_text
                    FROM reminders_v2
                    WHERE user_id = ? AND is_sent = FALSE
                    ORDER BY reminder_time
                ''', (user_id,))
                
                results = []
                for row in cursor.fetchall():
                    reminder_id, reminder_time_str, reminder_text = row
                    reminder_time = datetime.fromisoformat(reminder_time_str)
                    results.append((reminder_id, reminder_time, reminder_text or ""))
                
                return results
                
        except Exception as e:
            logger.error(f"Ошибка получения напоминаний пользователя: {e}")
            return []
    
    def get_due_reminders(self) -> List[Tuple[int, int, datetime, str]]:
        """
        Получить напоминания, которые нужно отправить
        
        Returns:
            List[Tuple[int, int, datetime, str]]: Список (id, user_id, reminder_time, reminder_text)
        """
        try:
            current_time = datetime.now(OMSK_TIMEZONE)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, user_id, reminder_time, reminder_text
                    FROM reminders_v2
                    WHERE is_sent = FALSE AND reminder_time <= ?
                ''', (current_time.isoformat(),))
                
                results = []
                for row in cursor.fetchall():
                    reminder_id, user_id, reminder_time_str, reminder_text = row
                    reminder_time = datetime.fromisoformat(reminder_time_str)
                    results.append((reminder_id, user_id, reminder_time, reminder_text or ""))
                
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
                    UPDATE reminders_v2 
                    SET is_sent = TRUE 
                    WHERE id = ?
                ''', (reminder_id,))
                conn.commit()
                
                logger.info(f"Напоминание {reminder_id} отмечено как отправленное")
                return True
                
        except Exception as e:
            logger.error(f"Ошибка обновления напоминания: {e}")
            return False
    
    def delete_reminder(self, reminder_id: int, user_id: int) -> bool:
        """
        Удалить конкретное напоминание пользователя
        
        Args:
            reminder_id: ID напоминания
            user_id: ID пользователя (для безопасности)
            
        Returns:
            bool: True если успешно удалено
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    DELETE FROM reminders_v2 
                    WHERE id = ? AND user_id = ?
                ''', (reminder_id, user_id))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                if deleted_count > 0:
                    logger.info(f"Удалено напоминание {reminder_id} пользователя {user_id}")
                    return True
                else:
                    logger.warning(f"Напоминание {reminder_id} не найдено для пользователя {user_id}")
                    return False
                
        except Exception as e:
            logger.error(f"Ошибка удаления напоминания: {e}")
            return False
    
    def get_reminders_count(self, user_id: int) -> int:
        """
        Получить количество активных напоминаний пользователя
        
        Args:
            user_id: ID пользователя
            
        Returns:
            int: Количество активных напоминаний
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT COUNT(*) FROM reminders_v2
                    WHERE user_id = ? AND is_sent = FALSE
                ''', (user_id,))
                
                return cursor.fetchone()[0]
                
        except Exception as e:
            logger.error(f"Ошибка подсчета напоминаний: {e}")
            return 0
    
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
                    DELETE FROM reminders_v2
                    WHERE is_sent = TRUE AND created_at < ?
                ''', (cutoff_time.isoformat(),))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                if deleted_count > 0:
                    logger.info(f"Удалено {deleted_count} старых напоминаний")
                    
        except Exception as e:
            logger.error(f"Ошибка очистки старых напоминаний: {e}")


# Глобальный экземпляр базы данных v2
db_v2 = ReminderDatabaseV2()
