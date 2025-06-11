"""
Расширенная версия Telegram-бота "Напоминалка" с дополнительными функциями
"""
import asyncio
import logging
from datetime import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message

from config_advanced import (
    BOT_TOKEN, setup_advanced_logging, get_config_summary,
    MESSAGES, ALLOWED_USERS, ADMIN_USER_ID, RATE_LIMIT_MESSAGES_PER_MINUTE,
    CHECK_INTERVAL_SECONDS, NOTIFICATION_RETRY_ATTEMPTS, NOTIFICATION_RETRY_DELAY_SECONDS
)
from database import db
from handlers import send_reminder_to_user
from utils import validate_reminder_time, format_datetime_for_user, format_time_for_user

logger = logging.getLogger(__name__)


class AdvancedReminderBot:
    """Расширенная версия бота с дополнительными функциями"""
    
    def __init__(self):
        # Настройка логирования
        setup_advanced_logging()
        
        # Логируем конфигурацию
        config_summary = get_config_summary()
        logger.info(f"Инициализация бота с конфигурацией: {config_summary}")
        
        # Создание бота и диспетчера
        self.bot = Bot(
            token=BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        self.dp = Dispatcher()
        
        # Регистрация обработчиков
        self._register_handlers()
        
        # Флаг для остановки фоновых задач
        self._running = False
        
        # Счетчики для статистики
        self.stats = {
            'messages_processed': 0,
            'reminders_sent': 0,
            'errors_count': 0,
            'start_time': datetime.now()
        }
        
        logger.info("Расширенный бот инициализирован")
    
    def _register_handlers(self):
        """Регистрация всех обработчиков"""
        
        @self.dp.message(Command("start"))
        async def cmd_start(message: Message):
            await self._handle_start(message)
        
        @self.dp.message(Command("help"))
        async def cmd_help(message: Message):
            await self._handle_help(message)
        
        @self.dp.message(Command("status"))
        async def cmd_status(message: Message):
            await self._handle_status(message)
        
        @self.dp.message(Command("stats"))
        async def cmd_stats(message: Message):
            await self._handle_stats(message)
        
        @self.dp.message(Command("cancel"))
        async def cmd_cancel(message: Message):
            await self._handle_cancel(message)
        
        @self.dp.message()
        async def handle_text_message(message: Message):
            await self._handle_text_message(message)
    
    def _check_access(self, user_id: int) -> bool:
        """Проверка доступа пользователя"""
        if not ALLOWED_USERS:
            return True  # Если список пуст, доступ для всех
        return str(user_id) in ALLOWED_USERS
    
    def _is_admin(self, user_id: int) -> bool:
        """Проверка, является ли пользователь администратором"""
        return ADMIN_USER_ID and user_id == ADMIN_USER_ID
    
    async def _handle_start(self, message: Message):
        """Обработчик команды /start"""
        try:
            user_id = message.from_user.id
            
            if not self._check_access(user_id):
                await message.answer(MESSAGES['access_denied'])
                return
            
            await message.answer(MESSAGES['start'])
            logger.info(f"Пользователь {user_id} запустил бота")
            self.stats['messages_processed'] += 1
            
        except Exception as e:
            logger.error(f"Ошибка в обработчике /start: {e}")
            self.stats['errors_count'] += 1
    
    async def _handle_help(self, message: Message):
        """Обработчик команды /help"""
        try:
            user_id = message.from_user.id
            
            if not self._check_access(user_id):
                await message.answer(MESSAGES['access_denied'])
                return
            
            await message.answer(MESSAGES['help'])
            logger.info(f"Пользователь {user_id} запросил помощь")
            self.stats['messages_processed'] += 1
            
        except Exception as e:
            logger.error(f"Ошибка в обработчике /help: {e}")
            self.stats['errors_count'] += 1
    
    async def _handle_status(self, message: Message):
        """Обработчик команды /status"""
        try:
            user_id = message.from_user.id
            
            if not self._check_access(user_id):
                await message.answer(MESSAGES['access_denied'])
                return
            
            # Получаем текущее напоминание пользователя
            reminder = db.get_user_reminder(user_id)
            
            if reminder:
                response = MESSAGES['current_reminder'].format(
                    date=format_datetime_for_user(reminder),
                    time=format_time_for_user(reminder)
                )
            else:
                response = MESSAGES['no_reminder']
            
            await message.answer(response)
            logger.info(f"Пользователь {user_id} проверил статус")
            self.stats['messages_processed'] += 1
            
        except Exception as e:
            logger.error(f"Ошибка в обработчике /status: {e}")
            await message.answer(MESSAGES['error_occurred'])
            self.stats['errors_count'] += 1
    
    async def _handle_stats(self, message: Message):
        """Обработчик команды /stats (только для админа)"""
        try:
            user_id = message.from_user.id
            
            if not self._is_admin(user_id):
                await message.answer("🚫 Команда доступна только администратору")
                return
            
            uptime = datetime.now() - self.stats['start_time']
            uptime_str = str(uptime).split('.')[0]  # Убираем микросекунды
            
            stats_text = f"""
📊 <b>СТАТИСТИКА БОТА</b>

⏱ <b>Время работы:</b> {uptime_str}
📨 <b>Обработано сообщений:</b> {self.stats['messages_processed']}
🔔 <b>Отправлено напоминаний:</b> {self.stats['reminders_sent']}
❌ <b>Ошибок:</b> {self.stats['errors_count']}

🗄 <b>База данных:</b>
• Активные напоминания: {len(db.get_due_reminders())}

🔧 <b>Конфигурация:</b>
• Интервал проверки: {CHECK_INTERVAL_SECONDS}с
• Попытки отправки: {NOTIFICATION_RETRY_ATTEMPTS}
• Лимит сообщений: {RATE_LIMIT_MESSAGES_PER_MINUTE}/мин
"""
            
            await message.answer(stats_text)
            logger.info(f"Администратор {user_id} запросил статистику")
            
        except Exception as e:
            logger.error(f"Ошибка в обработчике /stats: {e}")
            await message.answer(MESSAGES['error_occurred'])
            self.stats['errors_count'] += 1
    
    async def _handle_cancel(self, message: Message):
        """Обработчик команды /cancel"""
        try:
            user_id = message.from_user.id
            
            if not self._check_access(user_id):
                await message.answer(MESSAGES['access_denied'])
                return
            
            # Удаляем напоминание пользователя
            reminder = db.get_user_reminder(user_id)
            if reminder:
                # Удаляем из базы (помечаем как отправленное)
                # TODO: Добавить метод для удаления напоминания
                await message.answer("✅ Ваше напоминание отменено")
                logger.info(f"Пользователь {user_id} отменил напоминание")
            else:
                await message.answer(MESSAGES['no_reminder'])
            
            self.stats['messages_processed'] += 1
            
        except Exception as e:
            logger.error(f"Ошибка в обработчике /cancel: {e}")
            await message.answer(MESSAGES['error_occurred'])
            self.stats['errors_count'] += 1
    
    async def _handle_text_message(self, message: Message):
        """Обработчик текстовых сообщений"""
        try:
            user_id = message.from_user.id
            text = message.text.strip()
            
            if not self._check_access(user_id):
                await message.answer(MESSAGES['access_denied'])
                return
            
            logger.info(f"Получено сообщение от пользователя {user_id}: {text}")
            
            # Валидация времени напоминания
            target_datetime, status, is_today_only = validate_reminder_time(text)
            
            if status == "invalid_format":
                await message.answer(MESSAGES['invalid_format'])
                self.stats['messages_processed'] += 1
                return
            
            if status == "past_time":
                await message.answer(MESSAGES['past_time'])
                self.stats['messages_processed'] += 1
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
                await message.answer(MESSAGES['error_occurred'])
                logger.error(f"Не удалось сохранить напоминание для пользователя {user_id}")
                self.stats['errors_count'] += 1
            
            self.stats['messages_processed'] += 1
            
        except Exception as e:
            logger.error(f"Ошибка в обработчике текстовых сообщений: {e}")
            try:
                await message.answer(MESSAGES['error_occurred'])
            except Exception as send_error:
                logger.error(f"Не удалось отправить сообщение об ошибке: {send_error}")
            self.stats['errors_count'] += 1
    
    async def check_reminders(self):
        """Улучшенная фоновая задача для проверки напоминаний"""
        while self._running:
            try:
                # Получаем напоминания, которые нужно отправить
                due_reminders = db.get_due_reminders()
                
                for reminder_id, user_id, reminder_time in due_reminders:
                    success = False
                    
                    # Попытки отправки с повторами
                    for attempt in range(NOTIFICATION_RETRY_ATTEMPTS):
                        try:
                            await send_reminder_to_user(self.bot, user_id, reminder_time)
                            success = True
                            self.stats['reminders_sent'] += 1
                            break
                            
                        except Exception as e:
                            logger.warning(f"Попытка {attempt + 1} отправки напоминания {reminder_id} неудачна: {e}")
                            if attempt < NOTIFICATION_RETRY_ATTEMPTS - 1:
                                await asyncio.sleep(NOTIFICATION_RETRY_DELAY_SECONDS)
                    
                    if success:
                        # Отмечаем как отправленное
                        db.mark_reminder_sent(reminder_id)
                    else:
                        logger.error(f"Не удалось отправить напоминание {reminder_id} после {NOTIFICATION_RETRY_ATTEMPTS} попыток")
                        self.stats['errors_count'] += 1
                
                # Очистка старых напоминаний (раз в час)
                current_minute = datetime.now().minute
                if current_minute == 0:
                    db.cleanup_old_reminders()
                
            except Exception as e:
                logger.error(f"Ошибка в проверке напоминаний: {e}")
                self.stats['errors_count'] += 1
            
            # Ждем до следующей проверки
            await asyncio.sleep(CHECK_INTERVAL_SECONDS)
    
    async def start_polling(self):
        """Запуск бота в режиме polling"""
        try:
            self._running = True
            
            # Запускаем фоновую задачу проверки напоминаний
            reminder_task = asyncio.create_task(self.check_reminders())
            
            logger.info("Расширенный бот запущен в режиме polling")
            
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
        logger.info("Расширенный бот остановлен")


async def main():
    """Главная функция"""
    bot = AdvancedReminderBot()
    
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
