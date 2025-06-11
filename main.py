"""
Точка входа для Telegram-бота "Напоминалка"
"""
import asyncio
import sys
import logging
from bot import main

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nБот остановлен пользователем")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Критическая ошибка при запуске: {e}")
        sys.exit(1)
