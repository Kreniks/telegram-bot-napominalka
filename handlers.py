"""
Обработчики сообщений для Telegram-бота "Напоминалка"
"""
import logging
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import Message

from config import MESSAGES
from database import db
from utils import validate_reminder_time, format_datetime_for_user, format_time_for_user

logger = logging.getLogger(__name__)

# Создаем роутер для обработчиков
router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    try:
        await message.answer(MESSAGES['start'])
        logger.info(f"Пользователь {message.from_user.id} запустил бота")
    except Exception as e:
        logger.error(f"Ошибка в обработчике /start: {e}")


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help"""
    try:
        await message.answer(MESSAGES['help'])
        logger.info(f"Пользователь {message.from_user.id} запросил помощь")
    except Exception as e:
        logger.error(f"Ошибка в обработчике /help: {e}")


@router.message()
async def handle_text_message(message: Message):
    """Обработчик текстовых сообщений"""
    try:
        user_id = message.from_user.id
        text = message.text.strip()
        
        logger.info(f"Получено сообщение от пользователя {user_id}: {text}")
        
        # Валидация времени напоминания
        target_datetime, status, is_today_only = validate_reminder_time(text)
        
        if status == "invalid_format":
            await message.answer(MESSAGES['invalid_format'])
            return
        
        if status == "past_time":
            await message.answer(MESSAGES['past_time'])
            return
        
        # Сохраняем напоминание в базу данных
        if db.add_reminder(user_id, target_datetime):
            # Формируем ответ пользователю
            if is_today_only:
                response = MESSAGES['reminder_set_today'].format(
                    time=format_time_for_user(target_datetime)
                )
            else:
                response = MESSAGES['reminder_set_with_date'].format(
                    date=format_datetime_for_user(target_datetime),
                    time=format_time_for_user(target_datetime)
                )
            
            await message.answer(response)
            logger.info(f"Установлено напоминание для пользователя {user_id} на {target_datetime}")
        else:
            await message.answer("Произошла ошибка при сохранении напоминания. Попробуйте еще раз.")
            logger.error(f"Не удалось сохранить напоминание для пользователя {user_id}")
            
    except Exception as e:
        logger.error(f"Ошибка в обработчике текстовых сообщений: {e}")
        try:
            await message.answer(MESSAGES['unknown_message'])
        except Exception as send_error:
            logger.error(f"Не удалось отправить сообщение об ошибке: {send_error}")


async def send_reminder_to_user(bot, user_id: int, reminder_datetime):
    """
    Отправить напоминание пользователю
    
    Args:
        bot: Экземпляр бота
        user_id: ID пользователя
        reminder_datetime: Время напоминания
    """
    try:
        reminder_text = MESSAGES['reminder_text'].format(
            date=format_datetime_for_user(reminder_datetime),
            time=format_time_for_user(reminder_datetime)
        )
        
        await bot.send_message(chat_id=user_id, text=reminder_text)
        logger.info(f"Отправлено напоминание пользователю {user_id}")
        
    except Exception as e:
        logger.error(f"Ошибка отправки напоминания пользователю {user_id}: {e}")
        raise
