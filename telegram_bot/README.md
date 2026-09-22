# Telegram CI bot

Telegram bot, soatlik scheduler va CI xabarlariga tegishli kod shu papkada.

| Fayl | Vazifasi |
| --- | --- |
| `telegram_ci_bot.py` | Botning ishga tushirish va polling entry point'i |
| `telegram_progress.py` | CI progress CLI entry point'i |
| `telegram_api.py` | Barcha Telegram so'rovlari, javob/xato parsingi, tokenni yashirish va retry intervali |
| `bot_client.py` | Bot uchun Telegram metodlari, cooldown va bounded retry |
| `github_api.py` | GitHub Actions dispatch, status, artifact va cancel API |
| `handlers.py`, `runs.py` | Bot buyruqlari, parol tekshiruvi, manual run va monitoring |
| `scheduler.py` | Soatlik jadval va band runni tekshirish |
| `bot_messages.py`, `bot_delivery.py` | Bot dialoglari va vaqtinchalik xabarlarni boshqarish |
| `messages.py`, `progress_details.py` | CI progress/final xabarlari, Forms va failure tafsilotlari |
| `metrics.py`, `formatting.py` | Hisoblar, vaqt va matn formatlash |
| `bot_state.py`, `progress_state.py` | Botning xotiradagi holati va CI progress JSON holati |
| `progress_commands.py`, `progress_runner.py` | CI CLI amallari va test processidan eventlarni o'qish |
| `progress_delivery.py` | Progress throttle, final retry/fallback va delivery hisoboti |
| `summaries.py` | System va AI summary fayllaridan ma'lumot olish |
| `models.py`, `constants.py`, `paths.py`, `environment.py` | Umumiy turlar, konstantalar, yo'llar va environment helperlari |
| `telegram_ci_config.json` | GitHub, serverlar va jadvalning maxfiy bo'lmagan sozlamalari |
| `telegram_ci_settings.py` | JSON konfiguratsiyasini o'qish va tekshirish |
| `stop_ci_runs.py` | Faol GitHub Actions runlarini to'xtatish CLI'i |
| `screenshots.py` | CI xatosida umumiy Telegram API orqali screenshot yuborish |
| `run_telegram_ci_bot.bat` | Windows launcher |
| `deploy/` | Dockerfile, Compose, dependency va server deploy yo'riqnomasi |

Repo ildizidan botni ishga tushirish:

```bash
python -m telegram_bot.telegram_ci_bot
```

Windowsda `telegram_bot\run_telegram_ci_bot.bat` ishlatiladi. Bot credentiallari
environment orqali beriladi; botning o'zi `.env`ni avtomatik yuklamaydi.
Docker Compose repo ildizidagi `.env`ni container environmentiga yuklaydi.

JSON kod yonida saqlanadi. Token va parollar JSON'ga yozilmaydi; `.env` yoki
GitHub Secrets orqali beriladi. Test natijalari repo ildizidagi `test-results/`da
saqlanadi. GitHub workflow fayllari `.github/workflows/`dan shu kodni chaqiradi.

Server buyruqlari va yangi manzilga o'tish: [deploy/README.md](deploy/README.md).

Telegram transporti faqat Python standart kutubxonasiga tayanadi: CI dependency
o'rnatilishidan oldin ham progress yubora oladi. `requests` faqat GitHub client
va botning GitHub xatolarini boshqarish yo'lida kerak.

Umumiy API bir urinishni bajaradi. Bot cooldown/retry, jonli CI progress throttle
va final xabarning retry/fallback siyosatlari o'z modullarida qoladi; umumiy
transport o'zi qayta urinish qilmaydi. Run va stop paroli uchun ikkita mustaqil
`PendingStore` instansiyasi ishlatiladi, ularning holati aralashmaydi.
