"""
Точка входа для Telegram-бота "Напоминалка" версия 2.0
"""
import asyncio
import sys
import logging
from bot import main

if __name__ == "__main__":
    try:
        print("🚀 Запуск Telegram-бота 'Напоминалка' v2.0")
        print("✨ Новые возможности:")
        print("  - Множественные напоминания")
        print("  - Кнопки управления")
        print("  - Расширенные форматы дат")
        print("=" * 50)
        
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен пользователем")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Критическая ошибка при запуске: {e}")
        print(f"❌ Ошибка: {e}")
        sys.exit(1)
