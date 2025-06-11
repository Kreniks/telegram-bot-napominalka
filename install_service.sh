#!/bin/bash

# Скрипт установки Telegram-бота "Напоминалка" как системного сервиса
# Для Ubuntu/Debian систем

set -e

echo "🚀 Установка Telegram-бота 'Напоминалка' как системного сервиса"
echo "================================================================"

# Проверяем права root
if [[ $EUID -ne 0 ]]; then
   echo "❌ Этот скрипт должен запускаться с правами root (sudo)"
   exit 1
fi

# Переменные
BOT_USER="botuser"
BOT_DIR="/opt/reminder-bot"
SERVICE_NAME="reminder-bot"

echo "📦 Обновление системы..."
apt update

echo "🐍 Установка Python и зависимостей..."
apt install -y python3 python3-pip python3-venv git

echo "👤 Создание пользователя для бота..."
if ! id "$BOT_USER" &>/dev/null; then
    useradd -r -s /bin/false -d "$BOT_DIR" "$BOT_USER"
    echo "✅ Пользователь $BOT_USER создан"
else
    echo "ℹ️ Пользователь $BOT_USER уже существует"
fi

echo "📁 Создание директории для бота..."
mkdir -p "$BOT_DIR"
cd "$BOT_DIR"

echo "📥 Клонирование репозитория..."
if [ -d ".git" ]; then
    echo "ℹ️ Репозиторий уже существует, обновляем..."
    git pull
else
    git clone https://github.com/Kreniks/telegram-bot-napominalka.git .
fi

echo "🔧 Настройка виртуального окружения..."
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

echo "🔐 Настройка переменных окружения..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "⚠️ ВНИМАНИЕ: Отредактируйте файл $BOT_DIR/.env и добавьте ваш BOT_TOKEN!"
    echo "Получите токен у @BotFather в Telegram"
fi

echo "🔒 Настройка прав доступа..."
chown -R "$BOT_USER:$BOT_USER" "$BOT_DIR"
chmod 600 "$BOT_DIR/.env"

echo "🔧 Установка systemd сервиса..."
cp reminder-bot.service /etc/systemd/system/
systemctl daemon-reload

echo "🚀 Включение автозапуска сервиса..."
systemctl enable "$SERVICE_NAME"

echo "✅ Установка завершена!"
echo ""
echo "📋 Следующие шаги:"
echo "1. Отредактируйте файл $BOT_DIR/.env и добавьте ваш BOT_TOKEN"
echo "2. Запустите сервис: sudo systemctl start $SERVICE_NAME"
echo "3. Проверьте статус: sudo systemctl status $SERVICE_NAME"
echo "4. Просмотр логов: sudo journalctl -u $SERVICE_NAME -f"
echo ""
echo "🔧 Полезные команды:"
echo "• Запуск: sudo systemctl start $SERVICE_NAME"
echo "• Остановка: sudo systemctl stop $SERVICE_NAME"
echo "• Перезапуск: sudo systemctl restart $SERVICE_NAME"
echo "• Статус: sudo systemctl status $SERVICE_NAME"
echo "• Логи: sudo journalctl -u $SERVICE_NAME -f"
echo "• Мониторинг: cd $BOT_DIR && python3 monitor.py"
