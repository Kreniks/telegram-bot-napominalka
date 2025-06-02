# 🤖 Как получить токен для Telegram-бота

## 🎯 Проблема решена!

Я запустил бота в Docker и нашел проблему: **токен в файле .env недействительный**.

Aiogram проверяет формат токена и выдает ошибку: `TokenValidationError: Token is invalid!`

---

## 📋 Пошаговая инструкция получения токена

### Шаг 1: Откройте Telegram
- Запустите приложение Telegram на телефоне или компьютере

### Шаг 2: Найдите @BotFather
- В поиске введите: `@BotFather`
- Выберите официального BotFather (с галочкой)

### Шаг 3: Создайте нового бота
1. Напишите команду: `/newbot`
2. BotFather спросит имя бота. Введите, например: `Мой Напоминатель`
3. BotFather спросит username бота. Введите, например: `my_reminder_12345_bot`
   - Username должен заканчиваться на `bot`
   - Username должен быть уникальным
   - Если занят, попробуйте добавить цифры

### Шаг 4: Получите токен
После создания бота BotFather пришлет сообщение с токеном:

```
Congratulations! You have just created a new bot. 
You will find it at t.me/my_reminder_12345_bot. 
You can now add a description...

Use this token to access the HTTP API:
1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

Keep your token secure and store it safely, it can be used by anyone to control your bot.
```

**СКОПИРУЙТЕ ЭТОТ ТОКЕН!** (строка с цифрами и буквами)

### Шаг 5: Настройте .env файл
1. Откройте файл `.env` в блокноте
2. Найдите строку: `BOT_TOKEN=YOUR_BOT_TOKEN_HERE`
3. Замените `YOUR_BOT_TOKEN_HERE` на ваш токен
4. Должно получиться: `BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`
5. Сохраните файл

---

## 🚀 Запуск после настройки токена

### Docker (рекомендуется):
```bash
docker-run.bat
```

### Обычный запуск:
```bash
run.bat
```

---

## ✅ Проверка работы

1. Найдите своего бота в Telegram по username
2. Напишите `/start`
3. Бот должен ответить приветствием
4. Введите время, например: `19:00`
5. Бот установит напоминание

---

## 🔍 Диагностика Docker

Я протестировал Docker контейнер:

### ✅ Что работает:
- Docker образ собирается успешно
- Контейнер запускается
- .env файл читается правильно
- Все зависимости установлены

### ❌ Что было не так:
- Токен в .env файле был недействительным
- Aiogram отклонил токен при валидации

### 🎯 Решение:
- Получить настоящий токен от @BotFather
- Заменить в .env файле
- Перезапустить контейнер

---

## 💡 Полезные команды Docker

```bash
# Просмотр логов
docker-compose logs -f telegram-bot

# Перезапуск после изменения .env
docker-compose restart

# Остановка
docker-compose down

# Полная пересборка
docker-compose build --no-cache
docker-compose up -d
```

---

## 🎉 Готово!

После получения настоящего токена от @BotFather бот будет работать идеально в Docker!

**Docker решает все проблемы с зависимостями и кодировкой - остается только получить токен! 🚀**
