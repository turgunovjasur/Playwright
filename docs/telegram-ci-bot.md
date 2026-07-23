# Telegram CI Bot

Telegram bot GitHub Actions workflow `.github/workflows/daily-smoke.yml`ni
ishga tushiradi. Workflow avtomatik ravishda har soat `00` daqiqada ham yuradi.
CI va Telegram bot runlari `setup-report` targetini ishlatadi: avval User setup,
keyin Report testlari yuradi. A/B/C group testlari workflowga kiritilmaydi.
`smartup.online` va `app3.greenwhite.uz/xtrade` serverlarining ikkalasida ham
mavjud company ishlatiladi (`CREATE_COMPANY=0`).

## Bot Flow

Telegramda:

```text
/run
```

Bot server tanlatadi:

```text
[Online]
[Xtrade]
```

Bot GitHub Actions run boshlaydi. Workflow shu xabarning o'zini edit qilib
progress ko'rsatadi:

```text
Test boshlandi
Setup + Report
Status: requirements o'rnatilyapti
```

Keyin:

```text
Test boshlandi
Setup + Report
Status: testlar ishlayapti
Hozir: test_01_legal_person

Passed:
test_01_legal_person [PASSED]
test_02_filial [PASSED]
```

Testlar o'tgan sari `Passed` ro'yxatiga qo'shilib boradi. Failed bo'lsa shu
progress xabarda alohida block chiqadi:

```text
Failed:
Group: Setup
Runner test: test_setup_runner.py
Ichki test: 10 - Buy License
Step: Buy License -> Лицензии sahifasini ochish
Error turi: TimeoutError
```

Bu progress xabari vaqtinchalik. Workflow final xabarni yuborgandan keyin
progress xabarini o'chiradi.

Test jarayonda bo'lsa, yangi `/run` boshlanmaydi. Bot mavjud runni qisqa
ko'rsatadi:

```text
Test jarayonda: 3 daqiqa. Run: https://github.com/turgunovjasur/Playwright/actions/runs/...
```

Workflow tugagach `.github/workflows/daily-smoke.yml` yakuniy test summary
xabarini Telegramga yuboradi. Failed bo'lsa final xabarda `Failed` blocki
chiqadi: group, runner test, ichki test, step, kod joyi, error turi, sabab va
ta'sir.

Gemini AI default holatda off. Workflow manual run qilinganda `ai_summary=true`
tanlansa yoki runner `--ai-summary` bilan yursa, Telegram xabarda qo'shimcha
`AI xulosa` chiqadi. AI faqat 1-2 gaplik umumiy xulosa yozadi; failed step,
kod joyi va error turini tizim o'zi chiqaradi.

Failed bo'lsa oxirgi screenshot ham yuboriladi, screenshot topilmasa artifact
linki beriladi.

Final xabarda test yaratgan user login ham chiqadi:

```text
User login: user-pw4827@autotest
```

Bu yerda `4827` qiymati `test-results/data/data_store.json` ichidagi `code`
dan olinadi. Password Telegramga yuborilmaydi.

## Commands

```text
/run
/servers
/help
```

Company code/password botdan so'ralmaydi. Ular tanlangan serverga qarab GitHub
Actions secrets orqali olinadi:

```text
smartup.online -> SMARTUP_COMPANY_CODE / SMARTUP_COMPANY_PASSWORD
app3.greenwhite.uz/xtrade -> APP3_COMPANY_CODE / APP3_COMPANY_PASSWORD
```

Botda smoke/regression scope tanlovi yo'q. `/run`dan keyin faqat server
tanlanadi; ikkala server ham existing-company rejimida ishlaydi.

AI xulosa uchun GitHub repository secrets ichida quyidagisi bo'lishi kerak:

```text
GEMINI_API_KEY
```

Bu key bot ishlayotgan Windows serverda emas, GitHub Actions secrets ichida
turadi. Key bo'lmasa test baribir ishlaydi va `System summary` chiqadi.
To'liq tizim xulosasi `daily-smoke-test-results` artifact ichida va Allure
reportda `System Test Summary` sifatida saqlanadi. `AI Test Summary` faqat AI
yoqilgan va Gemini javob bergan runlarda saqlanadi.

## Required Environment Variables

Windows serverda bot uchun kerak:

```text
TELEGRAM_BOT_TOKEN=<telegram bot token>
TELEGRAM_CHAT_ID=<allowed chat id>
TELEGRAM_RUN_PASSWORD=<run password>
GITHUB_PAT=<github personal access token>
```

Optional:

```text
GITHUB_REPOSITORY=turgunovjasur/Playwright
GITHUB_WORKFLOW_FILE=daily-smoke.yml
GITHUB_REF=main
ALLOWED_SERVER_URLS=https://smartup.online,https://app3.greenwhite.uz/xtrade
```

`ALLOWED_SERVER_URLS` faqat shu ikki serverga ruxsat beradi:

```text
https://smartup.online
https://app3.greenwhite.uz/xtrade
```

## GitHub Token Permission

Fine-grained GitHub personal access token yarating.

Repository:

```text
turgunovjasur/Playwright
```

Permission:

```text
Actions: Read and write
```

Tokenni repository fayllariga, Telegramga yoki loglarga yozmang.

## Windows Local Server Run

Repositoryni clone qiling, keyin:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

CMD ishlatsangiz:

```cmd
set TELEGRAM_BOT_TOKEN=telegram_bot_token
set TELEGRAM_CHAT_ID=telegram_chat_id
set GITHUB_PAT=github_pat
set ALLOWED_SERVER_URLS=https://smartup.online,https://app3.greenwhite.uz/xtrade
```

Botni ishga tushirish:

```cmd
run_telegram_ci_bot.bat
```

CMD oynasi ochiq turishi kerak. Oyna yopilsa bot ham to'xtaydi.
