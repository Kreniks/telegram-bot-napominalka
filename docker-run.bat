@echo off
title Docker - Telegram Bot

echo.
echo ========================================
echo   Docker Telegram Bot Manager
echo ========================================
echo.

:: Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker not found!
    echo Please install Docker Desktop from https://docker.com
    pause
    exit /b 1
)

echo Docker found:
docker --version

:: Check if .env file exists
if not exist ".env" (
    echo.
    echo WARNING: .env file not found!
    echo Creating template .env file...
    echo BOT_TOKEN=your_bot_token_here > .env
    echo TIMEZONE=UTC >> .env
    echo LOGGING_LEVEL=INFO >> .env
    echo.
    echo ATTENTION: Configure your bot token in .env file!
    echo Then run this script again.
    pause
    exit /b 1
)

:: Check if token is configured
findstr /C:"your_bot_token_here" .env >nul
if not errorlevel 1 (
    echo.
    echo ERROR: Bot token not configured!
    echo Edit .env file and set your bot token from @BotFather
    pause
    exit /b 1
)

echo.
echo Building Docker image...
docker-compose build

if errorlevel 1 (
    echo ERROR: Failed to build Docker image
    pause
    exit /b 1
)

echo.
echo Starting bot in Docker container...
docker-compose up -d

if errorlevel 1 (
    echo ERROR: Failed to start container
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Bot started successfully!
echo ========================================
echo.
echo Container status:
docker-compose ps

echo.
echo Useful commands:
echo   docker-compose logs -f    - View logs
echo   docker-compose stop       - Stop bot
echo   docker-compose restart    - Restart bot
echo   docker-compose down       - Stop and remove container
echo.
pause
