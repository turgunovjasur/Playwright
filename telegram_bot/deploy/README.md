# Playwright CI bot deployment

`@smartup_ci_bot` Hetzner serverda boshqa servislar bilan bir hostda, lekin
alohida Docker Compose project sifatida ishlaydi.

## Fayllarning yangi joylashuvi

Bot kodi va konfiguratsiyasi `telegram_bot/`da, deploy fayllari esa
`telegram_bot/deploy/`da. Repo yangilangach Compose buyruqlarida yangi
`telegram_bot/deploy/docker-compose.yml` yo'lini ishlating va image'ni qayta
build qiling. Compose project nomi `playwright-ci-bot`, servis nomi `bot` va
repo ildizidagi `.env` manzili saqlangan. Windows launcher ham
`telegram_bot/run_telegram_ci_bot.bat`ga ko'chdi; tashqi Task Scheduler yoki
service sozlamasida eski script yo'li bo'lsa uni yangilash kerak.

## Server topologiyasi

Serverda uchta mustaqil loyiha mavjud:

| Loyiha | Server katalogi | Compose project | Playwright deployining vakolati |
| --- | --- | --- | --- |
| Playwright CI bot (`@smartup_ci_bot`) | `/opt/playwright-ci-bot` | `playwright-ci-bot` | Deploy, restart va log tekshiruvi mumkin |
| QA-Assistant (`@qa_assistant_leads_bot`) | `/opt/qa-assistant` | `qa-assistant` | Tegilmaydi |
| Namoz_vaqti (`@UzNamozTaqvimiBot`) | `/opt/namoz-vaqti` | `namoz-vaqti` | Tegilmaydi |

Playwright botning container nomi Compose tomonidan
`playwright-ci-bot-bot-1` ko‘rinishida yaratiladi. U o‘zining
`playwright-ci-bot_default` networkida ishlaydi. Servis host port ochmaydi,
database yoki boshqa project volume/networklariga ulanmaydi.

## Izolyatsiya qoidalari

- Barcha Playwright deploy buyruqlari faqat `/opt/playwright-ci-bot` ichida va
  explicit `-p playwright-ci-bot` bilan bajariladi.
- `/opt/qa-assistant` va `/opt/namoz-vaqti` ichida Playwright deploy buyrug‘i
  bajarilmaydi.
- QA-Assistant va Namoz_vaqti `.env` fayllari, credentiallari, containerlari,
  networklari va volumelaridan foydalanilmaydi hamda ular o‘zgartirilmaydi.
- Playwright credentiallari faqat `/opt/playwright-ci-bot/.env`da saqlanadi;
  fayl permissioni `0600` bo‘lishi kerak.
- Playwright botni deploy, restart yoki rollback qilish boshqa Compose
  projectlarni restart qilishni talab qilmaydi.

## Har soatlik scheduler

Production hourly scheduling authoritysi GitHub cron emas, shu
`playwright-ci-bot` containeridir. Bot har soat `Asia/Tashkent` vaqti bilan
`HH:17`da `daily-smoke.yml` workflowiga `suite=all`, `server=smartup` dispatch
yuboradi.

`all` bitta workflow run ichida Smoke va Reportni parallel boshlaydi; Forms
Smoke tugagach ishlaydi. Active workflow mavjud bo‘lsa joriy slot skip qilinadi.
Container `HH:17` vaqtida ishlamagan bo‘lsa, o‘tkazib yuborilgan slot keyin
qoplanmaydi.

Scheduler faqat server `.env`ida yoqiladi:

```dotenv
HOURLY_SCHEDULE_ENABLED=1
```

GitHub repository/workflow/ref, ruxsat etilgan serverlar va jadval tafsilotlari
bot yonidagi `telegram_bot/telegram_ci_config.json`da saqlanadi. Bot, `stop_ci_runs.py`
va GitHub workflow server manzillarini shu fayldan o'qiydi. JSON yo'li joriy
terminal katalogiga emas, loader fayli joylashuviga bog'langan.

`.env`da bot uchun faqat `TELEGRAM_BOT_TOKEN`, `TELEGRAM_RUN_PASSWORD`,
`GITHUB_TOKEN` va `HOURLY_SCHEDULE_ENABLED` kerak. Eski `GITHUB_REPOSITORY`,
`GITHUB_WORKFLOW_FILE`, `GITHUB_REF`, `ALLOWED_SERVER_URLS`,
`HOURLY_SCHEDULE_MINUTE`, `HOURLY_SCHEDULE_TIMEZONE`, `HOURLY_SCHEDULE_SERVER`
environment qiymatlari endi bot konfiguratsiyasiga ta'sir qilmaydi; ulardagi
custom qiymatlarni deploydan oldin JSON'ga ko'chiring.

JSON Git'da saqlanadi va Docker image'ga kiradi. JSON o'zgarganda serverda pull
va `docker compose -f telegram_bot/deploy/docker-compose.yml -p playwright-ci-bot up -d --build`
kerak; faqat `restart` yangi image yaratmaydi. CI joblari o'z checkoutidagi
JSON'ni ishlatadi. JSON'ga token, API key va parol yozilmaydi.

Rollbackda `HOURLY_SCHEDULE_ENABLED=0` qilinib faqat Playwright containeri
recreate qilinadi. GitHub `schedule` triggeri qayta tiklanmaguncha hourly run
bo‘lmaydi; server scheduler va GitHub cron bir vaqtda yoqilmaydi.

## Operator buyruqlari

Quyidagi buyruqlar serverdagi `/opt/playwright-ci-bot` katalogidan bajariladi:

```bash
docker compose \
  -f telegram_bot/deploy/docker-compose.yml \
  -p playwright-ci-bot ps

docker compose \
  -f telegram_bot/deploy/docker-compose.yml \
  -p playwright-ci-bot logs --tail 100 bot

docker compose \
  -f telegram_bot/deploy/docker-compose.yml \
  -p playwright-ci-bot up -d --build

docker compose \
  -f telegram_bot/deploy/docker-compose.yml \
  -p playwright-ci-bot restart bot
```

`docker compose down` ishlatilsa ham `-p playwright-ci-bot` va shu projectning
Compose fayli explicit ko‘rsatilishi shart. Server bo‘yicha umumiy `docker
compose down`, container cleanup yoki volume/network prune bajarilmaydi.

## Runtime chegaralari

Bot faqat Telegram va GitHub API’lariga outbound HTTPS so‘rovlari yuboradi.
Compose konfiguratsiyasi containerga `0.25 CPU`, `128 MB` RAM, read-only root
filesystem, `no-new-privileges`, dropped Linux capabilities va log rotation
chegaralarini beradi.
