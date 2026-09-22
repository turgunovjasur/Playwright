@echo off
setlocal

cd /d "%~dp0.."

.venv\Scripts\python.exe telegram_bot\telegram_ci_bot.py

exit /b %ERRORLEVEL%
