@echo off
title Docker Stop - Telegram Bot

echo.
echo ========================================
echo   Stopping Telegram Bot
echo ========================================
echo.

echo Stopping bot container...
docker-compose stop

echo.
echo Removing container...
docker-compose down

echo.
echo ========================================
echo   Bot stopped successfully!
echo ========================================
echo.
pause
