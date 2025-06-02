@echo off
title Docker Logs - Telegram Bot

echo.
echo ========================================
echo   Viewing Bot Logs
echo ========================================
echo.

echo Press Ctrl+C to stop viewing logs
echo.

docker-compose logs -f telegram-bot
