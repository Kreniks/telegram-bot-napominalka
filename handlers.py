"""
Обновленные обработчики сообщений для Telegram-бота "Напоминалка" (версия 2.0)
Поддержка множественных напоминаний и кнопок
"""
import logging
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import MESSAGES
from database import db_v2
from utils import (
    validate_reminder_time_v2,
    format_datetime_for_user,
    format_time_for_user,
    format_datetime_short,
    get_time_until_reminder
)

logger = logging.getLogger(__name__)

# Создаем роутер для обработчиков
router = Router()


def get_main_keyboard() -> InlineKeyboardMarkup:
    """Создать основную клавиатуру с кнопками"""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="📋 Мои напоминания",
        callback_data="show_reminders"
    ))
    builder.add(InlineKeyboardButton(
        text="ℹ️ Помощь",
        callback_data="help"
    ))
    builder.adjust(1)  # По одной кнопке в ряд
    return builder.as_markup()


def get_reminders_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Создать клавиатуру со списком напоминаний"""
    builder = InlineKeyboardBuilder()
    
    reminders = db_v2.get_user_reminders(user_id)
    
    if not reminders:
        builder.add(InlineKeyboardButton(
            text="➕ Добавить напоминание",
            callback_data="add_reminder_help"
        ))
    else:
        # Добавляем кнопки для каждого напоминания
        for reminder_id, reminder_time, reminder_text in reminders:
            time_str = format_datetime_short(reminder_time)
            text_preview = reminder_text[:20] + "..." if reminder_text and len(reminder_text) > 20 else reminder_text
            
            button_text = f"🕐 {time_str}"
            if text_preview:
                button_text += f" - {text_preview}"
            
            builder.add(InlineKeyboardButton(
                text=button_text,
                callback_data=f"reminder_{reminder_id}"
            ))
        
        # Кнопка добавления нового напоминания
        builder.add(InlineKeyboardButton(
            text="➕ Добавить еще",
            callback_data="add_reminder_help"
        ))
    
    # Кнопка возврата в главное меню
    builder.add(InlineKeyboardButton(
        text="🔙 Назад",
        callback_data="main_menu"
    ))
    
    builder.adjust(1)  # По одной кнопке в ряд
    return builder.as_markup()


def get_reminder_detail_keyboard(reminder_id: int) -> InlineKeyboardMarkup:
    """Создать клавиатуру для детального просмотра напоминания"""
    builder = InlineKeyboardBuilder()
    
    builder.add(InlineKeyboardButton(
        text="🗑️ Удалить",
        callback_data=f"delete_{reminder_id}"
    ))
    builder.add(InlineKeyboardButton(
        text="🔙 К списку",
        callback_data="show_reminders"
    ))
    
    builder.adjust(1)
    return builder.as_markup()


def get_delete_confirmation_keyboard(reminder_id: int) -> InlineKeyboardMarkup:
    """Создать клавиатуру подтверждения удаления"""
    builder = InlineKeyboardBuilder()
    
    builder.add(InlineKeyboardButton(
        text="✅ Да, удалить",
        callback_data=f"confirm_delete_{reminder_id}"
    ))
    builder.add(InlineKeyboardButton(
        text="❌ Отмена",
        callback_data=f"reminder_{reminder_id}"
    ))
    
    builder.adjust(2)  # По две кнопки в ряд
    return builder.as_markup()


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    try:
        user_id = message.from_user.id
        
        # Обновленное приветственное сообщение
        welcome_text = (
            "🤖 Привет! Я бот-Напоминалка v2.0!\n\n"
            "✨ Новые возможности:\n"
            "• Множественные напоминания\n"
            "• Удобные кнопки управления\n"
            "• Расширенные форматы дат\n\n"
            "📝 Поддерживаемые форматы:\n"
            "• <code>18:00</code> - на сегодня\n"
            "• <code>18:00 12.06</code> - без года\n"
            "• <code>18:00 12.06.25</code> - короткий год\n"
            "• <code>18:00 12.06.2025</code> - полный формат\n\n"
            "🌍 Все время по Омску (+6 UTC)"
        )
        
        await message.answer(
            welcome_text,
            reply_markup=get_main_keyboard(),
            parse_mode="HTML"
        )
        logger.info(f"Пользователь {user_id} запустил бота v2.0")
        
    except Exception as e:
        logger.error(f"Ошибка в обработчике /start: {e}")


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help"""
    try:
        await show_help(message.from_user.id, message.answer)
        logger.info(f"Пользователь {message.from_user.id} запросил помощь")
    except Exception as e:
        logger.error(f"Ошибка в обработчике /help: {e}")


@router.message(Command("list", "reminders"))
async def cmd_list_reminders(message: Message):
    """Обработчик команды /list или /reminders"""
    try:
        await show_reminders_list(message.from_user.id, message.answer)
        logger.info(f"Пользователь {message.from_user.id} запросил список напоминаний")
    except Exception as e:
        logger.error(f"Ошибка в обработчике /list: {e}")


@router.callback_query(F.data == "main_menu")
async def callback_main_menu(callback: CallbackQuery):
    """Обработчик кнопки главного меню"""
    try:
        await callback.message.answer(
            "🏠 Главное меню\n\nВыберите действие:",
            reply_markup=get_main_keyboard()
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка в callback main_menu: {e}")
        await callback.answer("Произошла ошибка")


@router.callback_query(F.data == "show_reminders")
async def callback_show_reminders(callback: CallbackQuery):
    """Обработчик кнопки показа напоминаний"""
    try:
        await show_reminders_list_new_message(callback.from_user.id, callback.message.answer)
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка в callback show_reminders: {e}")
        await callback.answer("Произошла ошибка")


@router.callback_query(F.data == "help")
async def callback_help(callback: CallbackQuery):
    """Обработчик кнопки помощи"""
    try:
        await show_help_new_message(callback.from_user.id, callback.message.answer)
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка в callback help: {e}")
        await callback.answer("Произошла ошибка")


@router.callback_query(F.data == "add_reminder_help")
async def callback_add_reminder_help(callback: CallbackQuery):
    """Обработчик кнопки помощи по добавлению напоминания"""
    try:
        help_text = (
            "➕ Как добавить напоминание:\n\n"
            "Просто напишите время и дату в любом из форматов:\n\n"
            "📝 Примеры:\n"
            "• <code>18:00</code> - сегодня в 18:00\n"
            "• <code>09:30 15.06</code> - 15 июня в 09:30\n"
            "• <code>14:00 25.12.25</code> - 25 декабря 2025 в 14:00\n"
            "• <code>20:30 01.01.2026</code> - 1 января 2026 в 20:30\n\n"
            "💡 Можно добавить неограниченное количество напоминаний!"
        )
        
        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(
            text="🔙 К напоминаниям",
            callback_data="show_reminders"
        ))
        
        await callback.message.edit_text(
            help_text,
            reply_markup=builder.as_markup(),
            parse_mode="HTML"
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка в callback add_reminder_help: {e}")
        await callback.answer("Произошла ошибка")


@router.callback_query(F.data.startswith("reminder_"))
async def callback_reminder_detail(callback: CallbackQuery):
    """Обработчик кнопки детального просмотра напоминания"""
    try:
        reminder_id = int(callback.data.split("_")[1])
        user_id = callback.from_user.id
        
        # Получаем информацию о напоминании
        reminders = db_v2.get_user_reminders(user_id)
        reminder_info = None
        
        for r_id, r_time, r_text in reminders:
            if r_id == reminder_id:
                reminder_info = (r_id, r_time, r_text)
                break
        
        if not reminder_info:
            await callback.answer("Напоминание не найдено")
            return
        
        _, reminder_time, reminder_text = reminder_info
        
        detail_text = (
            f"🕐 <b>Напоминание #{reminder_id}</b>\n\n"
            f"📅 Дата: {format_datetime_for_user(reminder_time)}\n"
            f"⏰ Время: {format_time_for_user(reminder_time)}\n"
            f"⏳ {get_time_until_reminder(reminder_time)}\n"
        )
        
        if reminder_text:
            detail_text += f"\n💬 Текст: {reminder_text}"
        
        await callback.message.edit_text(
            detail_text,
            reply_markup=get_reminder_detail_keyboard(reminder_id),
            parse_mode="HTML"
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка в callback reminder_detail: {e}")
        await callback.answer("Произошла ошибка")


@router.callback_query(F.data.startswith("delete_"))
async def callback_delete_reminder(callback: CallbackQuery):
    """Обработчик кнопки удаления напоминания"""
    try:
        reminder_id = int(callback.data.split("_")[1])
        
        await callback.message.edit_text(
            f"🗑️ Удалить напоминание #{reminder_id}?\n\nЭто действие нельзя отменить.",
            reply_markup=get_delete_confirmation_keyboard(reminder_id)
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка в callback delete_reminder: {e}")
        await callback.answer("Произошла ошибка")


@router.callback_query(F.data.startswith("confirm_delete_"))
async def callback_confirm_delete(callback: CallbackQuery):
    """Обработчик подтверждения удаления напоминания"""
    try:
        reminder_id = int(callback.data.split("_")[2])
        user_id = callback.from_user.id
        
        if db_v2.delete_reminder(reminder_id, user_id):
            await callback.message.edit_text(
                "✅ Напоминание удалено!",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                    InlineKeyboardButton(text="🔙 К списку", callback_data="show_reminders")
                ]])
            )
            logger.info(f"Пользователь {user_id} удалил напоминание {reminder_id}")
        else:
            await callback.answer("Не удалось удалить напоминание")
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка в callback confirm_delete: {e}")
        await callback.answer("Произошла ошибка")


@router.message()
async def handle_text_message(message: Message):
    """Обработчик текстовых сообщений"""
    try:
        user_id = message.from_user.id
        text = message.text.strip()
        
        logger.info(f"Получено сообщение от пользователя {user_id}: {text}")
        
        # Валидация времени напоминания
        target_datetime, status, is_today_only = validate_reminder_time_v2(text)
        
        if status == "invalid_format":
            await message.answer(
                "❌ Неверный формат!\n\n"
                "Поддерживаемые форматы:\n"
                "• <code>18:00</code> - на сегодня\n"
                "• <code>18:00 12.06</code> - без года\n"
                "• <code>18:00 12.06.25</code> - короткий год\n"
                "• <code>18:00 12.06.2025</code> - полный формат",
                parse_mode="HTML",
                reply_markup=get_main_keyboard()
            )
            return
        
        if status == "past_time":
            await message.answer(
                "⏰ Это время уже прошло!\n\nУкажите будущее время и дату.",
                reply_markup=get_main_keyboard()
            )
            return
        
        # Сохраняем напоминание в базу данных
        if db_v2.add_reminder(user_id, target_datetime):
            # Формируем ответ пользователю
            if is_today_only:
                response = f"✅ Напоминание добавлено на сегодня в {format_time_for_user(target_datetime)}!"
            else:
                response = f"✅ Напоминание добавлено на {format_datetime_for_user(target_datetime)} в {format_time_for_user(target_datetime)}!"
            
            # Показываем количество напоминаний
            count = db_v2.get_reminders_count(user_id)
            response += f"\n\n📊 У вас {count} активных напоминаний"
            
            await message.answer(response, reply_markup=get_main_keyboard())
            logger.info(f"Установлено напоминание для пользователя {user_id} на {target_datetime}")
        else:
            await message.answer(
                "❌ Произошла ошибка при сохранении напоминания. Попробуйте еще раз.",
                reply_markup=get_main_keyboard()
            )
            logger.error(f"Не удалось сохранить напоминание для пользователя {user_id}")
            
    except Exception as e:
        logger.error(f"Ошибка в обработчике текстовых сообщений: {e}")
        try:
            await message.answer(
                "❌ Произошла ошибка. Попробуйте еще раз.",
                reply_markup=get_main_keyboard()
            )
        except Exception as send_error:
            logger.error(f"Не удалось отправить сообщение об ошибке: {send_error}")


async def show_reminders_list(user_id: int, edit_func):
    """Показать список напоминаний пользователя"""
    reminders = db_v2.get_user_reminders(user_id)
    
    if not reminders:
        text = (
            "📋 У вас пока нет напоминаний\n\n"
            "Чтобы добавить напоминание, просто напишите время и дату.\n"
            "Например: <code>18:00 12.06</code>"
        )
    else:
        text = f"📋 Ваши напоминания ({len(reminders)}):\n\n"
        
        for i, (reminder_id, reminder_time, reminder_text) in enumerate(reminders, 1):
            time_str = format_datetime_short(reminder_time)
            until_str = get_time_until_reminder(reminder_time)
            
            text += f"{i}. 🕐 {time_str}\n"
            text += f"   ⏳ {until_str}\n"
            if reminder_text:
                text += f"   💬 {reminder_text}\n"
            text += "\n"
    
    await edit_func(
        text,
        reply_markup=get_reminders_keyboard(user_id),
        parse_mode="HTML"
    )


async def show_help(user_id: int, edit_func):
    """Показать справку"""
    help_text = (
        "ℹ️ <b>Справка по боту-напоминалке v2.0</b>\n\n"
        "📝 <b>Поддерживаемые форматы:</b>\n"
        "• <code>18:00</code> - напоминание на сегодня\n"
        "• <code>18:00 12.06</code> - 12 июня текущего года\n"
        "• <code>18:00 12.06.25</code> - 12 июня 2025 года\n"
        "• <code>18:00 12.06.2025</code> - полный формат\n\n"
        "✨ <b>Возможности:</b>\n"
        "• Неограниченное количество напоминаний\n"
        "• Удобное управление через кнопки\n"
        "• Автоматическое определение года\n"
        "• Все время по Омску (+6 UTC)\n\n"
        "🔧 <b>Команды:</b>\n"
        "• /start - главное меню\n"
        "• /list - список напоминаний\n"
        "• /help - эта справка"
    )
    
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="🔙 Главное меню",
        callback_data="main_menu"
    ))
    
    await edit_func(
        help_text,
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )


async def show_reminders_list_new_message(user_id: int, send_func):
    """Показать список напоминаний пользователя в новом сообщении"""
    reminders = db_v2.get_user_reminders(user_id)

    if not reminders:
        text = (
            "📋 У вас пока нет напоминаний\n\n"
            "Чтобы добавить напоминание, просто напишите время и дату.\n"
            "Например: <code>18:00 12.06</code>"
        )
    else:
        text = f"📋 Ваши напоминания ({len(reminders)}):\n\n"

        for i, (reminder_id, reminder_time, reminder_text) in enumerate(reminders, 1):
            time_str = format_datetime_short(reminder_time)
            until_str = get_time_until_reminder(reminder_time)

            text += f"{i}. 🕐 {time_str}\n"
            text += f"   ⏳ {until_str}\n"
            if reminder_text:
                text += f"   💬 {reminder_text}\n"
            text += "\n"

    await send_func(
        text,
        reply_markup=get_reminders_keyboard(user_id),
        parse_mode="HTML"
    )


async def show_help_new_message(user_id: int, send_func):
    """Показать справку в новом сообщении"""
    help_text = (
        "ℹ️ <b>Справка по боту-напоминалке v2.0</b>\n\n"
        "📝 <b>Поддерживаемые форматы:</b>\n"
        "• <code>18:00</code> - напоминание на сегодня\n"
        "• <code>18:00 12.06</code> - 12 июня текущего года\n"
        "• <code>18:00 12.06.25</code> - 12 июня 2025 года\n"
        "• <code>18:00 12.06.2025</code> - полный формат\n\n"
        "✨ <b>Возможности:</b>\n"
        "• Неограниченное количество напоминаний\n"
        "• Удобное управление через кнопки\n"
        "• Автоматическое определение года\n"
        "• Все время по Омску (+6 UTC)\n\n"
        "🔧 <b>Команды:</b>\n"
        "• /start - главное меню\n"
        "• /list - список напоминаний\n"
        "• /help - эта справка"
    )

    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="🔙 Главное меню",
        callback_data="main_menu"
    ))

    await send_func(
        help_text,
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )


async def send_reminder_to_user_v2(bot, user_id: int, reminder_datetime, reminder_text: str = None):
    """
    Отправить напоминание пользователю (версия 2.0)

    Args:
        bot: Экземпляр бота
        user_id: ID пользователя
        reminder_datetime: Время напоминания
        reminder_text: Дополнительный текст напоминания
    """
    try:
        base_text = f"🔔 <b>Напоминание!</b>\n📅 {format_datetime_for_user(reminder_datetime)} в {format_time_for_user(reminder_datetime)}"

        if reminder_text:
            base_text += f"\n\n💬 {reminder_text}"

        await bot.send_message(
            chat_id=user_id,
            text=base_text,
            parse_mode="HTML",
            reply_markup=get_main_keyboard()
        )
        logger.info(f"Отправлено напоминание пользователю {user_id}")

    except Exception as e:
        logger.error(f"Ошибка отправки напоминания пользователю {user_id}: {e}")
        raise
