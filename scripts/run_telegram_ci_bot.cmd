@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "REPO_ROOT=%%~fI"
cd /d "%REPO_ROOT%"

if not defined TELEGRAM_BOT_TOKEN (
    echo TELEGRAM_BOT_TOKEN environment variable is required.
    exit /b 1
)

if not defined TELEGRAM_RUN_PASSWORD (
    echo TELEGRAM_RUN_PASSWORD environment variable is required (test run password).
    exit /b 1
)

if not defined TELEGRAM_CHAT_ID (
    if not defined TELEGRAM_ALLOWED_CHAT_IDS (
        echo Warning: TELEGRAM_CHAT_ID is not set - auto-run messages will not be sent.
    )
)

if not defined GITHUB_TOKEN (
    if not defined GITHUB_PAT (
        echo GITHUB_TOKEN or GITHUB_PAT environment variable is required.
        exit /b 1
    )
)

if not defined GITHUB_REPOSITORY set "GITHUB_REPOSITORY=turgunovjasur/Playwright"
if not defined GITHUB_WORKFLOW_FILE set "GITHUB_WORKFLOW_FILE=daily-smoke.yml"
if not defined GITHUB_REF set "GITHUB_REF=main"
if not defined DEFAULT_SERVER_URL set "DEFAULT_SERVER_URL=https://smartup.online/"
if not defined ALLOWED_SERVER_URLS set "ALLOWED_SERVER_URLS=https://smartup.online,https://app3.greenwhite.uz/xtrade"

if not defined AUTO_RUN_ENABLED set "AUTO_RUN_ENABLED=true"
if not defined AUTO_RUN_INTERVAL_SECONDS set "AUTO_RUN_INTERVAL_SECONDS=3600"
if not defined AUTO_RUN_SERVER set "AUTO_RUN_SERVER=smartup"

set "VENV_PYTHON=%REPO_ROOT%\.venv\Scripts\python.exe"
if exist "%VENV_PYTHON%" (
    "%VENV_PYTHON%" "scripts\telegram_ci_bot.py"
) else (
    python "scripts\telegram_ci_bot.py"
)

exit /b %ERRORLEVEL%
