---
name: maintain-test-infra
description: Smartup test execution infrasi — scripts/run_tests.py, smoke config/reporting, Telegram CI bot, GitHub Actions workflow, Allure server va system/AI summary'larni diagnostika qiladi va yangilaydi. Bot, CI progress, report lifecycle, runner target mapping yoki summary pipeline bilan ishlaganda foydalan.
---

# Test Infrani Saqlash

## Vazifa turini aniqlash

- Runner target/config/collection → `scripts/run_tests.py`,
  `tests/smoke/smoke_config.py` va
  `skills/smartup-guide/references/smoke-runner.md`ni o'qi.
- Telegram bot yoki GitHub Actions → [references/telegram-ci.md](references/telegram-ci.md)ni o'qi.
- Allure, failure artifact yoki terminal progress → [references/reporting.md](references/reporting.md)ni o'qi.
- System/Gemini summary → [references/summaries.md](references/summaries.md)ni o'qi.

## Ish tartibi

1. User so'ragan infra komponentini va uning consumerlarini aniqlash.
2. Tegishli reference va amaldagi kodni o'qish; reference'ni koddan ustun qo'ymaslik.
3. Secret, production dispatch yoki doimiy server processiga tegmasdan read-only
   diagnostika bilan sababni isbotlash.
4. O'zgartirish so'ralgan bo'lsa eng kichik kesimda kod + test + reference'ni
   birga yangilash.
5. Unit test, `--dry-run` yoki eng tor relevant command bilan tekshirish.
6. Production workflow dispatch, Telegram xabar yuborish yoki Windows process
   restarti kerak bo'lsa userning explicit so'rovi/authoritysi bo'lmasa bajarmaslik.

## Kontraktlar

- Credential/token/password qiymatini kod, skill, chat yoki logga yozma.
- Telegram va GitHub API response'larini userga chiqarishda tokenli URL yoki
  request payloadni redact qil.
- Runner CLI/help, target mapping va skill commandlari bir o'zgarishda sinxron bo'lsin.
- Telegram progress, terminal summary va Allure bir xil test identity
  (`group`, `runner`, `test`, `Allure title`, nested step)dan foydalansin.
- Infra knowledge'ni current behavior va historical evidence sifatida ajrat;
  eski kontraktni joriy qoida sifatida qoldirma.
