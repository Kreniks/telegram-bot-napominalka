"""
Основной модуль Telegram-бота "Напоминалка"
"""
import asyncio
import logging
from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN, setup_logging
from database import db
from handlers import router, send_reminder_to_user

logger = logging.getLogger(__name__)


class ReminderBot:
    """Класс для управления ботом напоминаний"""
    
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
        
        logger.info("Бот инициализирован")
    
    async def check_reminders(self):
        """Фоновая задача для проверки напоминаний"""
        while self._running:
            try:
                # Получаем напоминания, которые нужно отправить
                due_reminders = db.get_due_reminders()
                
                for reminder_id, user_id, reminder_time in due_reminders:
                    try:
                        # Отправляем напоминание
                        await send_reminder_to_user(self.bot, user_id, reminder_time)
                        
                        # Отмечаем как отправленное
                        db.mark_reminder_sent(reminder_id)
                        
                    except Exception as e:
                        logger.error(f"Ошибка отправки напоминания {reminder_id}: {e}")
                
                # Очистка старых напоминаний (раз в час)
                current_minute = datetime.now().minute
                if current_minute == 0:
                    db.cleanup_old_reminders()
                
            except Exception as e:
                logger.error(f"Ошибка в проверке напоминаний: {e}")
            
            # Ждем 60 секунд до следующей проверки
            await asyncio.sleep(60)
    
    async def start_polling(self):
        """Запуск бота в режиме polling"""
        try:
            self._running = True
            
            # Запускаем фоновую задачу проверки напоминаний
            reminder_task = asyncio.create_task(self.check_reminders())
            
            logger.info("Бот запущен в режиме polling")
            
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
        logger.info("Бот остановлен")


async def main():
    """Главная функция"""
    bot = ReminderBot()
    
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
