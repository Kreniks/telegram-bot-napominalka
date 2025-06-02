"""
Telegram-бот "Напоминалка"
Основной файл для запуска бота
"""
import asyncio
import logging
from datetime import datetime, time
from typing import Dict, Set

from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN, MESSAGES, CHECK_INTERVAL
from utils.time_utils import validate_time_format, parse_time_string
from utils.reminder_manager import ReminderManager

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Создаем роутер для обработчиков
router = Router()

# Менеджер напоминаний
reminder_manager = ReminderManager()


@router.message(CommandStart())
async def start_handler(message: Message) -> None:
    """Обработчик команды /start"""
    await message.answer(MESSAGES['start'])
    logger.info(f"Пользователь {message.from_user.id} запустил бота")


@router.message(Command("help"))
async def help_handler(message: Message) -> None:
    """Обработчик команды /help"""
    await message.answer(MESSAGES['help'])
    logger.info(f"Пользователь {message.from_user.id} запросил помощь")


@router.message(Command("cancel"))
async def cancel_handler(message: Message) -> None:
    """Обработчик команды /cancel"""
    user_id = message.from_user.id
    
    if reminder_manager.has_reminder(user_id):
        reminder_manager.remove_reminder(user_id)
        await message.answer(MESSAGES['cancelled'])
        logger.info(f"Пользователь {user_id} отменил напоминание")
    else:
        await message.answer(MESSAGES['no_reminders'])
        logger.info(f"Пользователь {user_id} попытался отменить несуществующее напоминание")


@router.message()
async def time_handler(message: Message) -> None:
    """Обработчик ввода времени"""
    user_id = message.from_user.id
    text = message.text.strip()
    
    # Проверяем формат времени
    if not validate_time_format(text):
        await message.answer(MESSAGES['time_error'])
        logger.info(f"Пользователь {user_id} ввел некорректное время: {text}")
        return
    
    try:
        # Парсим время
        reminder_time = parse_time_string(text)
        
        # Сохраняем напоминание
        reminder_manager.set_reminder(user_id, reminder_time, message.chat.id)
        
        # Отправляем подтверждение
        await message.answer(MESSAGES['time_set'].format(time=text))
        logger.info(f"Пользователь {user_id} установил напоминание на {text}")
        
    except ValueError as e:
        await message.answer(MESSAGES['time_error'])
        logger.error(f"Ошибка парсинга времени для пользователя {user_id}: {e}")


async def check_reminders(bot: Bot) -> None:
    """Фоновая задача для проверки напоминаний"""
    while True:
        try:
            current_time = datetime.now().time()
            current_minute = current_time.replace(second=0, microsecond=0)
            
            # Получаем напоминания для текущей минуты
            reminders_to_send = reminder_manager.get_due_reminders(current_minute)
            
            for user_id, chat_id, reminder_time in reminders_to_send:
                try:
                    # Отправляем напоминание
                    time_str = reminder_time.strftime("%H:%M")
                    await bot.send_message(
                        chat_id=chat_id,
                        text=MESSAGES['reminder'].format(time=time_str)
                    )
                    
                    # Удаляем отправленное напоминание
                    reminder_manager.remove_reminder(user_id)
                    
                    logger.info(f"Отправлено напоминание пользователю {user_id} на {time_str}")
                    
                except Exception as e:
                    logger.error(f"Ошибка отправки напоминания пользователю {user_id}: {e}")
            
            # Ждем до следующей проверки
            await asyncio.sleep(CHECK_INTERVAL)
            
        except Exception as e:
            logger.error(f"Ошибка в check_reminders: {e}")
            await asyncio.sleep(CHECK_INTERVAL)


async def main() -> None:
    """Основная функция запуска бота"""
    # Создаем бота с настройками по умолчанию
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    # Создаем диспетчер
    dp = Dispatcher()
    
    # Подключаем роутер
    dp.include_router(router)
    
    # Запускаем фоновую задачу проверки напоминаний
    asyncio.create_task(check_reminders(bot))
    
    logger.info("Бот запущен")
    
    try:
        # Запускаем polling
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
