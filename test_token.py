"""
Скрипт для проверки токена Telegram-бота
"""
import os
import re
from pathlib import Path

def load_env_file():
    """Загружает переменные из .env файла"""
    env_vars = {}
    env_file = Path('.env')
    
    if not env_file.exists():
        print("❌ Файл .env не найден!")
        return env_vars
    
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
        print("✅ Файл .env загружен успешно")
    except Exception as e:
        print(f"❌ Ошибка чтения .env файла: {e}")
    
    return env_vars

def validate_token_format(token):
    """Проверяет формат токена"""
    if not token:
        return False, "Токен пустой"
    
    # Базовая проверка формата: число:строка
    pattern = r'^\d{8,10}:[A-Za-z0-9_-]{35}$'
    if not re.match(pattern, token):
        return False, "Неверный формат токена"
    
    return True, "Формат токена корректный"

def test_token_with_aiogram(token):
    """Тестирует токен с помощью aiogram"""
    try:
        from aiogram.utils.token import validate_token
        validate_token(token)
        return True, "Токен прошел валидацию aiogram"
    except ImportError:
        return None, "aiogram не установлен"
    except Exception as e:
        return False, f"Ошибка валидации aiogram: {e}"

def main():
    print("🔍 Проверка токена Telegram-бота")
    print("=" * 40)
    
    # Загружаем .env файл
    env_vars = load_env_file()
    
    # Получаем токен
    token = env_vars.get('BOT_TOKEN', '').strip()
    
    if not token:
        print("❌ BOT_TOKEN не найден в .env файле")
        print("\n📋 Инструкция:")
        print("1. Откройте файл .env")
        print("2. Добавьте строку: BOT_TOKEN=ваш_токен_здесь")
        print("3. Получите токен от @BotFather в Telegram")
        return
    
    print(f"🔑 Найден токен: {token[:10]}...{token[-10:] if len(token) > 20 else token}")
    
    # Проверяем, не является ли токен заглушкой
    placeholder_tokens = [
        'YOUR_BOT_TOKEN_HERE',
        'your_bot_token_here',
        '1234567890:ABCdefGHIjklMNOpqrsTUVwxyz'
    ]
    
    if token in placeholder_tokens:
        print("❌ Это токен-заглушка!")
        print("📋 Получите настоящий токен от @BotFather:")
        print("   1. Найдите @BotFather в Telegram")
        print("   2. Отправьте /newbot")
        print("   3. Следуйте инструкциям")
        print("   4. Скопируйте полученный токен в .env файл")
        return
    
    # Проверяем формат токена
    is_valid_format, format_message = validate_token_format(token)
    print(f"📝 Формат: {'✅' if is_valid_format else '❌'} {format_message}")
    
    if not is_valid_format:
        print("\n💡 Правильный формат токена:")
        print("   1234567890:ABCdefGHIjklMNOpqrsTUVwxyz")
        print("   - Начинается с 8-10 цифр")
        print("   - Затем двоеточие :")
        print("   - Затем 35 символов (буквы, цифры, _, -)")
        return
    
    # Тестируем с aiogram
    aiogram_result, aiogram_message = test_token_with_aiogram(token)
    if aiogram_result is not None:
        print(f"🤖 Aiogram: {'✅' if aiogram_result else '❌'} {aiogram_message}")
        
        if aiogram_result:
            print("\n🎉 ТОКЕН КОРРЕКТНЫЙ!")
            print("✅ Можно запускать бота")
        else:
            print("\n❌ ТОКЕН НЕКОРРЕКТНЫЙ!")
            print("📋 Получите новый токен от @BotFather")
    else:
        print(f"⚠️ Aiogram: {aiogram_message}")
        print("💡 Установите aiogram для полной проверки: pip install aiogram")
    
    print("\n🚀 Для запуска бота используйте:")
    print("   Docker: docker-run.bat")
    print("   Обычно: run.bat")

if __name__ == "__main__":
    main()
