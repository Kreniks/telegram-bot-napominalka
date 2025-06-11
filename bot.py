"""
Telegram-бот "Напоминалка" версия 2.0
Поддержка множественных напоминаний и расширенных форматов дат
"""
import asyncio
import logging
from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN, setup_logging
from database import db_v2
from handlers import router, send_reminder_to_user_v2

logger = logging.getLogger(__name__)


class ReminderBotV2:
    """Класс для управления ботом напоминаний версии 2.0"""
    
    def __init__(self):
        # Настройка логирования
        setup_logging()
        
        # Создание бота и диспетчера
        self.bot = Bot(
            token=BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        self.dp = Dispatcher()
        
        # Регистрация роутера
        self.dp.include_router(router)
        
        # Флаг для остановки фоновых задач
        self._running = False
        
        # Статистика
        self.stats = {
            'messages_processed': 0,
            'reminders_sent': 0,
            'reminders_added': 0,
            'reminders_deleted': 0,
            'errors_count': 0,
            'start_time': datetime.now()
        }
        
        logger.info("Бот v2.0 инициализирован")
    
    async def check_reminders(self):
        """Фоновая задача для проверки напоминаний"""
        while self._running:
            try:
                # Получаем напоминания, которые нужно отправить
                due_reminders = db_v2.get_due_reminders()
                
                for reminder_id, user_id, reminder_time, reminder_text in due_reminders:
                    try:
                        # Отправляем напоминание
                        await send_reminder_to_user_v2(self.bot, user_id, reminder_time, reminder_text)
                        
                        # Отмечаем как отправленное
                        db_v2.mark_reminder_sent(reminder_id)
                        
                        self.stats['reminders_sent'] += 1
                        
                    except Exception as e:
                        logger.error(f"Ошибка отправки напоминания {reminder_id}: {e}")
                        self.stats['errors_count'] += 1
                
                # Очистка старых напоминаний (раз в час)
                current_minute = datetime.now().minute
                if current_minute == 0:
                    db_v2.cleanup_old_reminders()
                
            except Exception as e:
                logger.error(f"Ошибка в проверке напоминаний: {e}")
                self.stats['errors_count'] += 1
            
            # Ждем 60 секунд до следующей проверки
            await asyncio.sleep(60)
    
    async def start_polling(self):
        """Запуск бота в режиме polling"""
        try:
            self._running = True
            
            # Запускаем фоновую задачу проверки напоминаний
            reminder_task = asyncio.create_task(self.check_reminders())
            
            logger.info("Бот v2.0 запущен в режиме polling")
            logger.info("Новые возможности:")
            logger.info("- Множественные напоминания")
            logger.info("- Кнопки управления")
            logger.info("- Расширенные форматы дат")
            
            # Запускаем polling
            await self.dp.start_polling(self.bot)
            
        except Exception as e:
            logger.error(f"Ошибка при запуске бота: {e}")
            raise
        finally:
            self._running = False
            if 'reminder_task' in locals():
                reminder_task.cancel()
                try:
                    await reminder_task
                except asyncio.CancelledError:
                    pass
    
    async def stop(self):
        """Остановка бота"""
        self._running = False
        await self.bot.session.close()
        logger.info("Бот v2.0 остановлен")
    
    def get_stats(self) -> dict:
        """Получить статистику работы бота"""
        uptime = datetime.now() - self.stats['start_time']
        
        return {
            **self.stats,
            'uptime_seconds': int(uptime.total_seconds()),
            'uptime_str': str(uptime).split('.')[0]
        }


async def main():
    """Главная функция"""
    bot = ReminderBotV2()
    
    try:
        await bot.start_polling()
    except KeyboardInterrupt:
        logger.info("Получен сигнал остановки")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
    finally:
        await bot.stop()


if __name__ == "__main__":
    asyncio.run(main())
