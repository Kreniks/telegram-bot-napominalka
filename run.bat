@echo off
title Telegram Bot
echo Starting bot...
cd /d "%~dp0"
call venv\Scripts\activate.bat
python main.py
echo.
echo Bot stopped. Press any key to close...
pause > nul