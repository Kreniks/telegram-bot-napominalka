# 🐳 Docker Guide для Telegram-бота "Напоминалка"

Полное руководство по запуску бота в Docker контейнерах.

## 📋 Содержание

- [Быстрый старт](#быстрый-старт)
- [Варианты запуска](#варианты-запуска)
- [Конфигурация](#конфигурация)
- [Мониторинг](#мониторинг)
- [Разработка](#разработка)
- [Production](#production)
- [Troubleshooting](#troubleshooting)

---

## 🚀 Быстрый старт

### 1. Подготовка
```bash
# Клонируйте репозиторий
git clone https://github.com/Kreniks/telegram-bot-napominalka.git
cd telegram-bot-napominalka

# Создайте .env файл
cp .env.example .env

# Получите токен у @BotFather и добавьте в .env
echo "BOT_TOKEN=your_bot_token_here" > .env
```

### 2. Запуск
```bash
# Простой запуск
make up

# Или через docker-compose
docker-compose up -d
```

### 3. Проверка
```bash
# Статус контейнеров
make status

# Логи
make logs

# Health check
make health
```

---

## 🔧 Варианты запуска

### 📦 Обычная версия
```bash
# Сборка и запуск
make build
make up

# Логи
make logs

# Остановка
make down
```

### 🛠️ Разработка
```bash
# Запуск dev окружения
make dev

# Доступные сервисы:
# - Бот с hot reload: http://localhost:8080
# - Web интерфейс: http://localhost
# - Debugger: порт 5678

# Тесты в dev режиме
make dev-test

# Остановка
make dev-down
```

### 🏭 Production
```bash
# Запуск production версии
make prod

# Логи production
make prod-logs

# Остановка
make prod-down
```

---

## ⚙️ Конфигурация

### Основные переменные окружения

```bash
# Обязательные
BOT_TOKEN=your_bot_token_here

# Основные настройки
LOG_LEVEL=INFO
CHECK_INTERVAL_SECONDS=60
HEALTH_CHECK_ENABLED=true
HEALTH_CHECK_PORT=8080

# Режимы запуска
RUN_MODE=normal          # normal, advanced, monitor, test
CREATE_BACKUP=false      # Создавать backup при запуске
LOG_TO_STDOUT=true       # Выводить логи в stdout
```

### Профили Docker Compose

#### Обычный запуск
```bash
docker-compose up -d telegram-bot
```

#### Production с supervisor
```bash
docker-compose --profile production up -d telegram-bot-production
```

#### Разработка
```bash
docker-compose -f docker-compose.dev.yml up -d
```

---

## 📊 Мониторинг

### Health Check
```bash
# Через make
make health

# Прямой запрос
curl http://localhost:8080/health
```

### Метрики
```bash
# Метрики бота
curl http://localhost:8080/metrics

# Мониторинг через контейнер
make monitor
```

### Логи
```bash
# Все логи
make logs

# Только ошибки
docker-compose logs telegram-bot | grep ERROR

# Последние 100 строк
docker-compose logs --tail=100 telegram-bot
```

### Backup
```bash
# Создать backup
make backup

# Автоматический backup (в production)
# Настраивается через CREATE_BACKUP=true
```

---

## 🛠️ Разработка

### Структура dev окружения

```yaml
services:
  telegram-bot-dev:    # Основной бот с hot reload
  telegram-bot-test:   # Контейнер для тестов
  telegram-bot-monitor: # Мониторинг
  nginx-dev:           # Прокси для web интерфейса
```

### Отладка
```bash
# Запуск с debugger
make dev

# Подключение к debugger (VS Code)
# Host: localhost
# Port: 5678
```

### Тестирование
```bash
# Все тесты
make test

# Тесты в dev режиме
make dev-test

# Конкретный тест
docker-compose run --rm telegram-bot python test_bot.py
```

### Вход в контейнер
```bash
# Shell в контейнере
make shell

# Или напрямую
docker exec -it reminder-bot /bin/bash
```

---

## 🏭 Production

### Особенности production версии

- **Supervisor** для управления процессами
- **Health check сервер** на порту 8080
- **Автоматические backup** базы данных
- **Ротация логов** с ограничением размера
- **Graceful shutdown** при остановке
- **Ограничения ресурсов** (CPU, память)

### Запуск в production

```bash
# Сборка production образа
make build-prod

# Запуск
make prod

# Проверка статуса
make status

# Логи
make prod-logs
```

### Настройки production

```bash
# В .env файле
RUN_MODE=advanced
CREATE_BACKUP=true
LOG_TO_STDOUT=true
LOG_MAX_SIZE_MB=50
LOG_BACKUP_COUNT=10
HEALTH_CHECK_ENABLED=true
```

---

## 🔍 Troubleshooting

### Проблемы с запуском

#### Ошибка "BOT_TOKEN не найден"
```bash
# Проверьте .env файл
cat .env | grep BOT_TOKEN

# Создайте .env если его нет
cp .env.example .env
```

#### Ошибка подключения к Telegram API
```bash
# Проверьте токен
make test

# Проверьте интернет соединение
docker exec reminder-bot curl -I https://api.telegram.org
```

#### Контейнер не запускается
```bash
# Проверьте логи
docker-compose logs telegram-bot

# Проверьте статус
docker ps -a

# Пересоберите образ
make rebuild
```

### Проблемы с базой данных

#### База данных заблокирована
```bash
# Остановите все контейнеры
make down

# Удалите volume
docker volume rm telegram-reminder-bot_bot_data

# Перезапустите
make up
```

#### Потеря данных
```bash
# Восстановите из backup
docker exec reminder-bot ls /app/backups/

# Скопируйте backup
docker cp reminder-bot:/app/backups/backup_20231211_120000.db ./
```

### Проблемы с производительностью

#### Высокое потребление памяти
```bash
# Проверьте статистику
docker stats reminder-bot

# Настройте ограничения в docker-compose.yml
deploy:
  resources:
    limits:
      memory: 256M
```

#### Медленная работа
```bash
# Увеличьте интервал проверки
CHECK_INTERVAL_SECONDS=120

# Уменьшите количество попыток
NOTIFICATION_RETRY_ATTEMPTS=2
```

---

## 📚 Полезные команды

### Docker
```bash
# Просмотр образов
docker images | grep reminder

# Очистка неиспользуемых образов
docker image prune

# Просмотр volumes
docker volume ls

# Backup volume
docker run --rm -v bot_data:/data -v $(pwd):/backup alpine tar czf /backup/backup.tar.gz /data
```

### Makefile команды
```bash
make help          # Справка по всем командам
make build         # Сборка образов
make up            # Запуск бота
make down          # Остановка
make logs          # Логи
make test          # Тесты
make clean         # Полная очистка
make dev           # Режим разработки
make prod          # Production режим
make status        # Статус контейнеров
make health        # Health check
make monitor       # Мониторинг
make backup        # Создать backup
make shell         # Войти в контейнер
make rebuild       # Пересобрать и перезапустить
```

---

## 🎯 Рекомендации

### Для разработки
- Используйте `make dev` для hot reload
- Включите `DEBUG_MODE=true`
- Используйте debugger на порту 5678

### Для production
- Используйте `make prod`
- Настройте автоматические backup
- Мониторьте health check endpoint
- Настройте ограничения ресурсов

### Для безопасности
- Не включайте .env в git
- Используйте Docker secrets в production
- Ограничьте доступ к health check endpoint
- Регулярно обновляйте базовые образы

---

**Готово! Ваш Telegram-бот готов к работе в Docker! 🚀**
