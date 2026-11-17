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

## Kunlik scheduler

Production scheduling authoritysi GitHub cron emas, shu
`playwright-ci-bot` containeridir. Bot har kuni `Asia/Tashkent` vaqti bilan
`02:00`da `daily-smoke.yml` workflowiga `suite=api-regression`, `server=smartup` dispatch
yuboradi.

Botdagi `/run` kabi, avval API setup bajariladi. U muvaffaqiyatli tugagach
Order regression boshlanadi. Active workflow mavjud bo‘lsa joriy slot skip qilinadi.
Container `02:00` vaqtida ishlamagan bo‘lsa, o‘tkazib yuborilgan slot keyin
qoplanmaydi.

Scheduler faqat server `.env`ida yoqiladi:

```dotenv
HOURLY_SCHEDULE_ENABLED=1
```

`HOURLY_SCHEDULE_ENABLED` nomi mavjud server sozlamalariga moslik uchun
saqlangan; u endi kunlik jadvalni yoqadi. JSON'dagi `schedule.hour=2` va
`schedule.minute=0` ishga tushish vaqtini belgilaydi.

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
recreate qilinadi. GitHub `schedule` triggeri qayta tiklanmaguncha scheduled run
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

## API setup va Order regression hisobotlari

Botda `/run` → Online yoki Xtrade → run paroli. Bitta CI jobda
`scripts/run_tests.py api-setup` tasdiqlagan baseline ustida
`tests/regression/run.py` ishlaydi. Tayyor Allure Telegram tugmasida ochiladi.
Brauzer uchun foydalanuvchi `qa`; viewer paroli deploy paytida botning run
paroliga moslanadi. Run paroli o‘zgarsa viewer hashini ham yangilang.

`reports` Compose servisi `report-storage/` ichidagi run-attempt HTML fayllarini
o'qishga beradi. CI alohida `ci` hisobida HTTPS PUT bilan joylaydi.
Publisher asl fayl yoniga `.html.view` yaratadi. Telegram havolasi Allure
oynasini ochadi. Test kartasi, rasm va trace uchun brauzer asl fayldan
kerakli baytlarni HTTP Range orqali oladi. Asl fayl, hisobot oynasi va
biriktirmalar bir xil viewer paroli bilan himoyalangan. Publisher eski
hisobotni o'chirganda uning `.view` faylini ham o'chiradi.
GitHub Actions sozlamalari:

- `ALLURE_REPORT_BASE_URL` repository variable — HTTPS manzili va
  `/playwright-reports` prefiksi.
- `ALLURE_UPLOAD_PASSWORD` repository secret — faqat CI publish paroli.
- `ALLURE_ARTIFACT_KEY` repository secret — zaxira HTML faylini shifrlash
  va ochish uchun alohida tasodifiy kalit. Kalit almashtirilsa, avvalgi
  kalit bilan shifrlangan artefaktlarni ochish uchun o‘sha kalit kerak.

Hetzner tayyor HTML faylini qabul qilmasa, CI asl run ichida
`allure-html-<run_id>-<attempt>` nomli shifrlangan artefaktni 7 kun saqlaydi.
Qayta yuklash uchun GitHub Actions → **Republish Allure report** →
**Run workflow** ni tanlang. Asl test runining ID va urinish raqamini kiriting
(birinchi urinish — `1`). Tayyor hisobot asl manziliga joylanadi va havolasi
yangi workflow’ning Summary sahifasida chiqadi. Hetzner’ning hajm, disk
zaxirasi va eng yangi uchta hisobotni saqlash qoidalari bunda ham amal qiladi.

Hostda `report-auth/viewers` va `report-auth/publisher` Nginx htpasswd
fayllari bo‘lishi kerak. Ularni Git tashqarisida saqlang.
`report-storage` konteynerdagi UID 101 uchun yoziladigan katalog.
`telegram_bot/deploy/.env` ichidagi `ALLURE_BIND_ADDRESS` Docker ichki gateway
manzilini tanlaydi. Mavjud TLS proxy `/playwright-reports/` prefiksini olib
tashlab shu manzildagi 18086-portga uzatadi va upstreamga cookie yubormaydi.
`report-publisher` CI yuborgan HTML faylini qabul qiladi. Eng katta fayl hajmi
4 GiB. Yuklash uchun joy oldindan ajratiladi va umumiy diskda kamida 5 GB
(5 000 000 000 bayt) bo‘sh joy saqlanadi. Joy yetishmasa uploader eskirgan
hisobotlarni o‘chiradi yoki HTTP 507 qaytaradi. Tugallanmagan upload e’lon qilinmaydi.
Run raqami va urinish raqami bo‘yicha eng yangi uchta HTML qoladi. Publisher
saqlash qoidasini ishga tushganda, muvaffaqiyatli uploaddan keyin va bo‘sh
turganda har daqiqada tekshiradi. Eski yetti kunlik cron qoidasi o‘rnini shu
servis egallaydi.
