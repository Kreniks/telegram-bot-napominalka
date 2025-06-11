# Многоэтапная сборка для оптимизации размера образа
FROM python:3.11-slim as builder

# Устанавливаем системные зависимости для сборки
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Создаем виртуальное окружение
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Копируем и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Финальный образ
FROM python:3.11-slim

# Метаданные образа
LABEL maintainer="telegram-bot-napominalka" \
      version="1.0" \
      description="Telegram Reminder Bot with Omsk timezone support"

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    tzdata \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Устанавливаем часовой пояс Омска
ENV TZ=Asia/Omsk
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Копируем виртуальное окружение из builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Создаем пользователя для безопасности
RUN groupadd -r botuser && useradd -r -g botuser -u 1000 botuser

# Создаем необходимые директории
RUN mkdir -p /app/data /app/logs /app/backups && \
    chown -R botuser:botuser /app

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем исходный код
COPY --chown=botuser:botuser . .

# Переключаемся на непривилегированного пользователя
USER botuser

# Переменные окружения
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DB_PATH=/app/data/reminders.db \
    LOG_FILE=/app/logs/bot.log

# Проверка здоровья контейнера
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sqlite3; sqlite3.connect('${DB_PATH}').execute('SELECT 1').fetchone()" || exit 1

# Том для данных
VOLUME ["/app/data", "/app/logs"]

# Порт для health check (если включен)
EXPOSE 8080

# Команда запуска (можно переопределить через переменную окружения)
CMD ["sh", "-c", "python ${BOT_SCRIPT:-main.py}"]
