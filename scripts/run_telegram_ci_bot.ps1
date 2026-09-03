Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $RepoRoot

if (-not $env:TELEGRAM_BOT_TOKEN) {
    throw "TELEGRAM_BOT_TOKEN environment variable is required."
}

# Botdan hamma foydalana oladi; CI run/stop faqat to'g'ri parol bilan ochiladi.
if (-not $env:TELEGRAM_RUN_PASSWORD) {
    throw "TELEGRAM_RUN_PASSWORD environment variable is required (CI run/stop paroli)."
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

if (-not $env:ALLOWED_SERVER_URLS) {
    $env:ALLOWED_SERVER_URLS = "https://smartup.online,https://app3.greenwhite.uz/xtrade"
}

$VenvPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"
if (Test-Path $VenvPython) {
    & $VenvPython "scripts\telegram_ci_bot.py"
}
else {
    & python "scripts\telegram_ci_bot.py"
}
