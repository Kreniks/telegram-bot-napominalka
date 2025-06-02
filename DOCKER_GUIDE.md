# 🐳 Docker Guide для Telegram-бота "Напоминалка"

## 🎯 Зачем Docker?

Docker решает все проблемы с:
- ❌ Установкой Python и зависимостей
- ❌ Конфликтами версий
- ❌ Проблемами с кодировкой
- ❌ Различиями между операционными системами

✅ **С Docker бот запустится одинаково везде!**

---

## 📋 Что нужно установить

### 1. Docker Desktop
Скачайте и установите с официального сайта:
🔗 **https://www.docker.com/products/docker-desktop/**

**Для Windows:**
- Скачайте Docker Desktop for Windows
- Запустите установщик
- Перезагрузите компьютер
- Запустите Docker Desktop

**Проверка установки:**
```bash
docker --version
```

---

## 🚀 Способы запуска

### Способ 1: Автоматический (рекомендуется)
```bash
# Просто двойной клик:
docker-run.bat
```

### Способ 2: Через командную строку
```bash
# Сборка образа
docker-compose build

# Запуск бота
docker-compose up -d

# Просмотр логов
docker-compose logs -f
```

### Способ 3: Обычный Docker (без compose)
```bash
# Сборка образа
docker build -t telegram-bot-napominalka .

# Запуск контейнера
docker run -d --name napominalka-bot --env-file .env telegram-bot-napominalka
```

---

## 🔧 Управление ботом

### 📊 Просмотр статуса
```bash
docker-compose ps
```

### 📝 Просмотр логов
```bash
# Автоматический способ:
docker-logs.bat

# Или вручную:
docker-compose logs -f telegram-bot
```

### 🔄 Перезапуск бота
```bash
docker-compose restart
```

### 🛑 Остановка бота
```bash
# Автоматический способ:
docker-stop.bat

# Или вручную:
docker-compose stop
docker-compose down
```

### 🗑️ Полная очистка
```bash
# Удалить контейнер и образ
docker-compose down
docker rmi telegram-bot-napominalka
```

---

## ⚙️ Конфигурация

### Переменные окружения (.env файл)
```env
BOT_TOKEN=your_bot_token_here
TIMEZONE=UTC
LOGGING_LEVEL=INFO
```

### Ресурсы контейнера
В `docker-compose.yml` настроены ограничения:
- **Память**: 256MB (максимум), 128MB (резерв)
- **CPU**: 0.5 ядра (максимум), 0.25 ядра (резерв)

---

## 📁 Структура Docker файлов

```
project/
├── Dockerfile              # Описание образа
├── docker-compose.yml      # Конфигурация сервисов
├── .dockerignore           # Исключения при сборке
├── docker-run.bat          # 🚀 Автозапуск
├── docker-logs.bat         # 📝 Просмотр логов
├── docker-stop.bat         # 🛑 Остановка
└── DOCKER_GUIDE.md         # 📚 Это руководство
```

---

## 🔍 Диагностика проблем

### Проблема: Docker не найден
**Решение:**
1. Установите Docker Desktop
2. Перезагрузите компьютер
3. Запустите Docker Desktop

### Проблема: Ошибка при сборке
**Решение:**
```bash
# Очистите кэш Docker
docker system prune -a

# Пересоберите образ
docker-compose build --no-cache
```

### Проблема: Контейнер не запускается
**Решение:**
```bash
# Проверьте логи
docker-compose logs telegram-bot

# Проверьте .env файл
# Убедитесь, что токен настроен правильно
```

### Проблема: Бот не отвечает
**Решение:**
```bash
# Проверьте статус
docker-compose ps

# Перезапустите
docker-compose restart

# Проверьте логи
docker-compose logs -f telegram-bot
```

---

## 🎯 Преимущества Docker версии

### ✅ **Изоляция**
- Бот работает в отдельном контейнере
- Не влияет на систему
- Легко удалить без следов

### ✅ **Портативность**
- Работает на Windows, Linux, macOS
- Одинаковое поведение везде
- Легко перенести на сервер

### ✅ **Безопасность**
- Бот работает не от root
- Ограничения ресурсов
- Изолированная сеть

### ✅ **Удобство**
- Автоматический перезапуск
- Ротация логов
- Мониторинг здоровья

---

## 🚀 Развертывание на сервере

### VPS/Dedicated сервер
```bash
# Клонируйте репозиторий
git clone https://github.com/Kreniks/telegram-bot-napominalka.git
cd telegram-bot-napominalka

# Настройте .env файл
nano .env

# Запустите бота
docker-compose up -d
```

### Cloud платформы
- **Heroku**: Используйте Dockerfile
- **DigitalOcean**: Docker Droplet
- **AWS**: ECS или EC2 с Docker
- **Google Cloud**: Cloud Run

---

## 📞 Поддержка

Если возникли проблемы:
1. Проверьте логи: `docker-logs.bat`
2. Перезапустите: `docker-compose restart`
3. Создайте issue в GitHub репозитории

---

**🐳 Docker делает запуск бота максимально простым!**
