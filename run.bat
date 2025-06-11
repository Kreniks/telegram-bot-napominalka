@echo off
echo Запуск Telegram-бота "Напоминалка"
echo ================================

REM Проверяем наличие виртуального окружения
if not exist "venv\Scripts\activate.bat" (
    echo Ошибка: Виртуальное окружение не найдено!
    echo Создайте виртуальное окружение командой: python -m venv venv
    pause
    exit /b 1
)

REM Проверяем наличие файла .env
if not exist ".env" (
    echo Ошибка: Файл .env не найден!
    echo Создайте файл .env на основе .env.example и добавьте токен бота
    pause
    exit /b 1
)

REM Активируем виртуальное окружение и запускаем бота
call venv\Scripts\activate.bat
python main.py

pause
