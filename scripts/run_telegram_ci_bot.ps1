Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $RepoRoot

if (-not $env:TELEGRAM_BOT_TOKEN) {
    throw "TELEGRAM_BOT_TOKEN environment variable is required."
}

# Botdan hamma foydalana oladi; testni run qilish faqat to'g'ri parol bilan ochiladi.
if (-not $env:TELEGRAM_RUN_PASSWORD) {
    throw "TELEGRAM_RUN_PASSWORD environment variable is required (test run paroli)."
}

# Avto-run xabarlari uchun maqsad chat (ixtiyoriy, lekin avto-run uchun kerak).
if (-not $env:TELEGRAM_CHAT_ID -and -not $env:TELEGRAM_ALLOWED_CHAT_IDS) {
    Write-Warning "TELEGRAM_CHAT_ID berilmagan - avto-run xabarlari yuborilmaydi."
}

if (-not $env:GITHUB_TOKEN -and -not $env:GITHUB_PAT) {
    throw "GITHUB_TOKEN or GITHUB_PAT environment variable is required."
}

if (-not $env:GITHUB_REPOSITORY) {
    $env:GITHUB_REPOSITORY = "turgunovjasur/Playwright"
}

if (-not $env:GITHUB_WORKFLOW_FILE) {
    $env:GITHUB_WORKFLOW_FILE = "daily-smoke.yml"
}

if (-not $env:GITHUB_REF) {
    $env:GITHUB_REF = "main"
}

if (-not $env:DEFAULT_SERVER_URL) {
    $env:DEFAULT_SERVER_URL = "https://smartup.online/"
}

if (-not $env:ALLOWED_SERVER_URLS) {
    $env:ALLOWED_SERVER_URLS = "https://smartup.online,https://app3.greenwhite.uz/xtrade"
}

# Soatlik avto-run. O'chirish uchun AUTO_RUN_ENABLED=false. Interval/parametrlarni o'zgartirsa boladi.
if (-not $env:AUTO_RUN_ENABLED) {
    $env:AUTO_RUN_ENABLED = "true"
}

if (-not $env:AUTO_RUN_INTERVAL_SECONDS) {
    $env:AUTO_RUN_INTERVAL_SECONDS = "3600"
}

if (-not $env:AUTO_RUN_SERVER) {
    $env:AUTO_RUN_SERVER = "smartup"
}

$VenvPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"
if (Test-Path $VenvPython) {
    & $VenvPython "scripts\telegram_ci_bot.py"
}
else {
    & python "scripts\telegram_ci_bot.py"
}
