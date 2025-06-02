@echo off
echo.
echo ========================================
echo   Pushing to GitHub Repository
echo ========================================
echo.

echo Adding remote origin...
git remote add origin https://github.com/Kreniks/telegram-bot-napominalka.git

echo.
echo Checking remote...
git remote -v

echo.
echo Pushing to GitHub...
git push -u origin master

echo.
echo ========================================
echo   Push completed!
echo ========================================
echo.
echo Repository URL: https://github.com/Kreniks/telegram-bot-napominalka
echo.
pause
