"""
Мониторинг состояния Telegram-бота "Напоминалка"
"""
import asyncio
import logging
import sqlite3
from datetime import datetime, timedelta
from config import DB_PATH, OMSK_TIMEZONE, setup_logging

setup_logging()
logger = logging.getLogger(__name__)


class BotMonitor:
    """Класс для мониторинга состояния бота"""
    
    def __init__(self):
        self.db_path = DB_PATH
    
    def check_database_health(self) -> dict:
        """Проверка состояния базы данных"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Проверяем структуру таблицы
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='reminders'")
                table_exists = cursor.fetchone() is not None
                
                if not table_exists:
                    return {"status": "error", "message": "Таблица reminders не существует"}
                
                # Считаем активные напоминания
                cursor.execute("SELECT COUNT(*) FROM reminders WHERE is_sent = FALSE")
                active_reminders = cursor.fetchone()[0]
                
                # Считаем общее количество напоминаний
                cursor.execute("SELECT COUNT(*) FROM reminders")
                total_reminders = cursor.fetchone()[0]
                
                # Считаем отправленные напоминания за последние 24 часа
                yesterday = datetime.now(OMSK_TIMEZONE) - timedelta(days=1)
                cursor.execute("""
                    SELECT COUNT(*) FROM reminders 
                    WHERE is_sent = TRUE AND created_at > ?
                """, (yesterday.isoformat(),))
                recent_sent = cursor.fetchone()[0]
                
                return {
                    "status": "healthy",
                    "active_reminders": active_reminders,
                    "total_reminders": total_reminders,
                    "sent_last_24h": recent_sent,
                    "db_size_mb": self._get_db_size()
                }
                
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _get_db_size(self) -> float:
        """Получить размер базы данных в МБ"""
        try:
            import os
            size_bytes = os.path.getsize(self.db_path)
            return round(size_bytes / (1024 * 1024), 2)
        except:
            return 0.0
    
    def get_upcoming_reminders(self, hours: int = 24) -> list:
        """Получить предстоящие напоминания"""
        try:
            current_time = datetime.now(OMSK_TIMEZONE)
            future_time = current_time + timedelta(hours=hours)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT user_id, reminder_time, created_at
                    FROM reminders
                    WHERE is_sent = FALSE 
                    AND reminder_time BETWEEN ? AND ?
                    ORDER BY reminder_time
                """, (current_time.isoformat(), future_time.isoformat()))
                
                reminders = []
                for row in cursor.fetchall():
                    user_id, reminder_time_str, created_at = row
                    reminder_time = datetime.fromisoformat(reminder_time_str)
                    reminders.append({
                        "user_id": user_id,
                        "reminder_time": reminder_time.strftime("%d.%m.%Y %H:%M"),
                        "created_at": created_at,
                        "time_until": str(reminder_time - current_time).split('.')[0]
                    })
                
                return reminders
                
        except Exception as e:
            logger.error(f"Ошибка получения предстоящих напоминаний: {e}")
            return []
    
    def generate_report(self) -> str:
        """Генерация отчета о состоянии бота"""
        current_time = datetime.now(OMSK_TIMEZONE)
        
        # Проверяем здоровье БД
        db_health = self.check_database_health()
        
        # Получаем предстоящие напоминания
        upcoming = self.get_upcoming_reminders()
        
        report = f"""
📊 ОТЧЕТ О СОСТОЯНИИ БОТА "НАПОМИНАЛКА"
Время отчета: {current_time.strftime("%d.%m.%Y %H:%M:%S")} (Омск)

🗄️ СОСТОЯНИЕ БАЗЫ ДАННЫХ:
Статус: {db_health.get('status', 'unknown')}
"""
        
        if db_health['status'] == 'healthy':
            report += f"""Активные напоминания: {db_health['active_reminders']}
Всего напоминаний: {db_health['total_reminders']}
Отправлено за 24ч: {db_health['sent_last_24h']}
Размер БД: {db_health['db_size_mb']} МБ
"""
        else:
            report += f"Ошибка: {db_health.get('message', 'Неизвестная ошибка')}\n"
        
        report += f"\n⏰ ПРЕДСТОЯЩИЕ НАПОМИНАНИЯ (24ч):\n"
        
        if upcoming:
            for reminder in upcoming[:10]:  # Показываем только первые 10
                report += f"• Пользователь {reminder['user_id']}: {reminder['reminder_time']} (через {reminder['time_until']})\n"
            
            if len(upcoming) > 10:
                report += f"... и еще {len(upcoming) - 10} напоминаний\n"
        else:
            report += "Нет предстоящих напоминаний\n"
        
        return report
    
    def cleanup_old_data(self, days: int = 30):
        """Очистка старых данных"""
        try:
            cutoff_date = datetime.now(OMSK_TIMEZONE) - timedelta(days=days)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM reminders 
                    WHERE is_sent = TRUE AND created_at < ?
                """, (cutoff_date.isoformat(),))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                logger.info(f"Удалено {deleted_count} старых записей (старше {days} дней)")
                return deleted_count
                
        except Exception as e:
            logger.error(f"Ошибка очистки старых данных: {e}")
            return 0


async def main():
    """Главная функция мониторинга"""
    monitor = BotMonitor()
    
    print("🔍 Запуск мониторинга бота...")
    
    # Генерируем отчет
    report = monitor.generate_report()
    print(report)
    
    # Очищаем старые данные
    deleted = monitor.cleanup_old_data()
    if deleted > 0:
        print(f"🧹 Очищено {deleted} старых записей")
    
    print("✅ Мониторинг завершен")


if __name__ == "__main__":
    asyncio.run(main())
