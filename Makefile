# Makefile для управления Telegram-ботом "Напоминалка"

# Переменные
DOCKER_COMPOSE = docker-compose
DOCKER_COMPOSE_DEV = docker-compose -f docker-compose.dev.yml
DOCKER_COMPOSE_PROD = docker-compose --profile production
PROJECT_NAME = telegram-reminder-bot
BUILD_DATE = $(shell date -u +"%Y-%m-%dT%H:%M:%SZ")
VCS_REF = $(shell git rev-parse --short HEAD)
VERSION = 1.0.0

# Цвета для вывода
RED = \033[0;31m
GREEN = \033[0;32m
YELLOW = \033[0;33m
BLUE = \033[0;34m
NC = \033[0m # No Color

.PHONY: help build up down logs test clean dev prod status health backup

# Помощь
help:
	@echo "$(BLUE)Telegram-бот 'Напоминалка' - Docker Management$(NC)"
	@echo "=================================================="
	@echo ""
	@echo "$(GREEN)Основные команды:$(NC)"
	@echo "  make build     - Собрать Docker образы"
	@echo "  make up        - Запустить бота (обычная версия)"
	@echo "  make down      - Остановить бота"
	@echo "  make logs      - Показать логи"
	@echo "  make test      - Запустить тесты"
	@echo "  make clean     - Очистить контейнеры и образы"
	@echo ""
	@echo "$(GREEN)Разработка:$(NC)"
	@echo "  make dev       - Запустить в режиме разработки"
	@echo "  make dev-logs  - Логи разработки"
	@echo "  make dev-test  - Тесты в dev режиме"
	@echo "  make dev-down  - Остановить dev окружение"
	@echo ""
	@echo "$(GREEN)Production:$(NC)"
	@echo "  make prod      - Запустить production версию"
	@echo "  make prod-logs - Логи production"
	@echo "  make prod-down - Остановить production"
	@echo ""
	@echo "$(GREEN)Версия 2.0:$(NC)"
	@echo "  make v2        - Запустить бота v2.0"
	@echo "  make v2-logs   - Логи v2.0"
	@echo "  make v2-down   - Остановить v2.0"
	@echo "  make v2-test   - Тесты v2.0"
	@echo ""
	@echo "$(GREEN)Мониторинг:$(NC)"
	@echo "  make status    - Статус контейнеров"
	@echo "  make health    - Проверка здоровья"
	@echo "  make monitor   - Запустить мониторинг"
	@echo "  make backup    - Создать backup"
	@echo ""
	@echo "$(GREEN)Утилиты:$(NC)"
	@echo "  make shell     - Войти в контейнер"
	@echo "  make rebuild   - Пересобрать и перезапустить"

# Проверка .env файла
check-env:
	@if [ ! -f .env ]; then \
		echo "$(RED)❌ Файл .env не найден!$(NC)"; \
		echo "$(YELLOW)Создайте .env файл на основе .env.example$(NC)"; \
		exit 1; \
	fi
	@if ! grep -q "BOT_TOKEN=" .env || grep -q "BOT_TOKEN=your_bot_token_here" .env; then \
		echo "$(RED)❌ BOT_TOKEN не настроен в .env файле!$(NC)"; \
		echo "$(YELLOW)Получите токен у @BotFather и добавьте в .env$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)✅ Конфигурация .env проверена$(NC)"

# Сборка образов
build: check-env
	@echo "$(BLUE)🔨 Сборка Docker образов...$(NC)"
	$(DOCKER_COMPOSE) build \
		--build-arg BUILD_DATE="$(BUILD_DATE)" \
		--build-arg VCS_REF="$(VCS_REF)" \
		--build-arg VERSION="$(VERSION)"
	@echo "$(GREEN)✅ Образы собраны$(NC)"

# Сборка production образа
build-prod: check-env
	@echo "$(BLUE)🔨 Сборка Production образа...$(NC)"
	$(DOCKER_COMPOSE_PROD) build \
		--build-arg BUILD_DATE="$(BUILD_DATE)" \
		--build-arg VCS_REF="$(VCS_REF)" \
		--build-arg VERSION="$(VERSION)"
	@echo "$(GREEN)✅ Production образ собран$(NC)"

# Запуск обычной версии
up: check-env
	@echo "$(BLUE)🚀 Запуск бота...$(NC)"
	$(DOCKER_COMPOSE) up -d telegram-bot
	@echo "$(GREEN)✅ Бот запущен$(NC)"
	@echo "$(YELLOW)Проверьте статус: make status$(NC)"
	@echo "$(YELLOW)Логи: make logs$(NC)"

# Запуск в режиме разработки
dev: check-env
	@echo "$(BLUE)🛠️ Запуск в режиме разработки...$(NC)"
	$(DOCKER_COMPOSE_DEV) up -d
	@echo "$(GREEN)✅ Dev окружение запущено$(NC)"
	@echo "$(YELLOW)Web интерфейс: http://localhost$(NC)"
	@echo "$(YELLOW)Health check: http://localhost:8080/health$(NC)"
	@echo "$(YELLOW)Debugger port: 5678$(NC)"

# Запуск production версии
prod: check-env build-prod
	@echo "$(BLUE)🏭 Запуск Production версии...$(NC)"
	$(DOCKER_COMPOSE_PROD) up -d telegram-bot-production
	@echo "$(GREEN)✅ Production бот запущен$(NC)"

# Остановка
down:
	@echo "$(BLUE)🛑 Остановка бота...$(NC)"
	$(DOCKER_COMPOSE) down
	@echo "$(GREEN)✅ Бот остановлен$(NC)"

dev-down:
	@echo "$(BLUE)🛑 Остановка dev окружения...$(NC)"
	$(DOCKER_COMPOSE_DEV) down
	@echo "$(GREEN)✅ Dev окружение остановлено$(NC)"

prod-down:
	@echo "$(BLUE)🛑 Остановка production...$(NC)"
	$(DOCKER_COMPOSE_PROD) down
	@echo "$(GREEN)✅ Production остановлен$(NC)"

# Логи
logs:
	$(DOCKER_COMPOSE) logs -f telegram-bot

dev-logs:
	$(DOCKER_COMPOSE_DEV) logs -f

prod-logs:
	$(DOCKER_COMPOSE_PROD) logs -f telegram-bot-production

# Тестирование
test: check-env
	@echo "$(BLUE)🧪 Запуск тестов...$(NC)"
	$(DOCKER_COMPOSE) run --rm telegram-bot python test_bot.py
	@echo "$(GREEN)✅ Тесты завершены$(NC)"

dev-test:
	@echo "$(BLUE)🧪 Запуск тестов в dev режиме...$(NC)"
	$(DOCKER_COMPOSE_DEV) run --rm telegram-bot-test
	@echo "$(GREEN)✅ Dev тесты завершены$(NC)"

# Статус
status:
	@echo "$(BLUE)📊 Статус контейнеров:$(NC)"
	@docker ps --filter "name=$(PROJECT_NAME)" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Проверка здоровья
health:
	@echo "$(BLUE)🏥 Проверка здоровья...$(NC)"
	@curl -s http://localhost:8080/health | python -m json.tool || echo "$(RED)❌ Health check недоступен$(NC)"

# Мониторинг
monitor:
	@echo "$(BLUE)📊 Запуск мониторинга...$(NC)"
	$(DOCKER_COMPOSE) run --rm telegram-bot python monitor.py

# Backup
backup:
	@echo "$(BLUE)💾 Создание backup...$(NC)"
	@docker exec reminder-bot python -c "
from database import db
from datetime import datetime
import shutil
import os

backup_name = f'backup_{datetime.now().strftime(\"%Y%m%d_%H%M%S\")}.db'
backup_path = f'/app/backups/{backup_name}'
os.makedirs('/app/backups', exist_ok=True)
shutil.copy2('/app/data/reminders.db', backup_path)
print(f'✅ Backup создан: {backup_path}')
"

# Вход в контейнер
shell:
	@echo "$(BLUE)🐚 Вход в контейнер...$(NC)"
	docker exec -it reminder-bot /bin/bash

# Пересборка и перезапуск
rebuild: down build up
	@echo "$(GREEN)✅ Пересборка завершена$(NC)"

# Очистка
clean:
	@echo "$(BLUE)🧹 Очистка...$(NC)"
	$(DOCKER_COMPOSE) down -v --rmi all --remove-orphans
	$(DOCKER_COMPOSE_DEV) down -v --rmi all --remove-orphans
	docker system prune -f
	@echo "$(GREEN)✅ Очистка завершена$(NC)"

# Показать версию
version:
	@echo "$(BLUE)Telegram-бот 'Напоминалка'$(NC)"
	@echo "Версия: $(VERSION)"
	@echo "Build: $(BUILD_DATE)"
	@echo "Git: $(VCS_REF)"

# ============================================================================
# КОМАНДЫ ДЛЯ ВЕРСИИ 2.0
# ============================================================================

# Запуск версии 2.0
v2: check-env
	@echo "$(BLUE)🚀 Запуск бота v2.0...$(NC)"
	@echo "$(YELLOW)✨ Новые возможности:$(NC)"
	@echo "$(YELLOW)  - Множественные напоминания$(NC)"
	@echo "$(YELLOW)  - Кнопки управления$(NC)"
	@echo "$(YELLOW)  - Расширенные форматы дат$(NC)"
	docker-compose -f docker-compose.v2.yml up -d telegram-bot-v2
	@echo "$(GREEN)✅ Бот v2.0 запущен$(NC)"
	@echo "$(YELLOW)Проверьте статус: make v2-status$(NC)"
	@echo "$(YELLOW)Логи: make v2-logs$(NC)"

# Остановка версии 2.0
v2-down:
	@echo "$(BLUE)🛑 Остановка бота v2.0...$(NC)"
	docker-compose -f docker-compose.v2.yml down
	@echo "$(GREEN)✅ Бот v2.0 остановлен$(NC)"

# Логи версии 2.0
v2-logs:
	docker-compose -f docker-compose.v2.yml logs -f telegram-bot-v2

# Статус версии 2.0
v2-status:
	@echo "$(BLUE)📊 Статус бота v2.0:$(NC)"
	@docker ps --filter "name=reminder-bot-v2" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Тесты версии 2.0
v2-test: check-env
	@echo "$(BLUE)🧪 Запуск тестов v2.0...$(NC)"
	docker-compose -f docker-compose.v2.yml run --rm telegram-bot-v2 python test_bot_v2.py
	@echo "$(GREEN)✅ Тесты v2.0 завершены$(NC)"

# Пересборка и перезапуск v2.0
v2-rebuild: v2-down
	@echo "$(BLUE)🔨 Пересборка бота v2.0...$(NC)"
	docker-compose -f docker-compose.v2.yml build --no-cache telegram-bot-v2
	@echo "$(BLUE)🚀 Запуск обновленного бота v2.0...$(NC)"
	docker-compose -f docker-compose.v2.yml up -d telegram-bot-v2
	@echo "$(GREEN)✅ Бот v2.0 пересобран и запущен$(NC)"

# Вход в контейнер v2.0
v2-shell:
	@echo "$(BLUE)🐚 Вход в контейнер v2.0...$(NC)"
	docker exec -it reminder-bot-v2 /bin/bash

# Health check для v2.0
v2-health:
	@echo "$(BLUE)🏥 Проверка здоровья v2.0...$(NC)"
	@curl -s http://localhost:8080/health | python -m json.tool || echo "$(RED)❌ Health check недоступен$(NC)"

# Очистка v2.0
v2-clean:
	@echo "$(BLUE)🧹 Очистка v2.0...$(NC)"
	docker-compose -f docker-compose.v2.yml down -v --rmi all --remove-orphans
	@echo "$(GREEN)✅ Очистка v2.0 завершена$(NC)"
