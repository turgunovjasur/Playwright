---
name: maintain-test-infra
description: Use when Smartup runner targetlari, smoke config, Telegram CI, GitHub Actions, Allure lifecycle, progress yoki system/AI summary infrasi bilan ishlash kerak bo'lsa.
---

# Test Infrani Saqlash

## Skill Chegarasi

Bu skill runner, collection, CI, Allure lifecycle va reporting subsystemini
egallaydi. Bitta testning kuzatilgan failure root cause'i — `debug-test`;
testni ishga tushirish va run summary — `run-smoke`; test artifactini yozish —
`write-test`. Owner skillga havola ruxsat scope'ini kengaytirmaydi.

## Vazifa turini aniqlash

- Runner target/config/collection → `scripts/run_tests.py`,
  `tests/smoke/smoke_config.py` va
  `skills/smartup-guide/references/smoke-runner.md`ni o'qi.
- Telegram bot yoki GitHub Actions → [references/telegram-ci.md](references/telegram-ci.md)ni o'qi.
- Allure, failure artifact yoki terminal progress → [references/reporting.md](references/reporting.md)ni o'qi.
- System/Gemini summary → [references/summaries.md](references/summaries.md)ni o'qi.
- Har qanday infra kod o'zgarishi →
  [unit test qoidasini](../write-test/references/project-rules.md#unit-test-qoshmaslik-va-run-qilmaslik)
  va `skills/run-smoke/SKILL.md`dagi user-reported execution qoidasini o'qi;
  reference'dagi verification commandlarini ruxsat deb qabul qilma.

## Ish tartibi

1. User so'ragan infra komponentini va uning consumerlarini aniqlash.
2. Tegishli reference va amaldagi kodni o'qish; reference'ni koddan ustun qo'ymaslik.
3. Secret, production dispatch yoki doimiy server processiga tegmasdan read-only
   diagnostika bilan sababni isbotlash.
4. O'zgartirish so'ralgan bo'lsa eng kichik kesimda kod + reference'ni birga
   yangilash. Unit-test scope'i uchun `write-test`dagi canonical qoidaga amal qil.
5. Default verificationni syntax/config parse, linter, read-only inspection va
   `git diff --check` bilan chekla. `pytest`, test collection yoki boshqa test
   commandini faqat user aynan `run qil` deganda ishlat.
6. Production workflow dispatch, Telegram xabar yuborish yoki Windows process
   restarti kerak bo'lsa userning explicit so'rovi/authoritysi bo'lmasa bajarmaslik.

## Kontraktlar

- Credential/token/password qiymatini kod, skill, chat yoki logga yozma.
- Telegram va GitHub API response'larini userga chiqarishda tokenli URL yoki
  request payloadni redact qil.
- Runner CLI/help, target mapping va skill commandlari bir o'zgarishda sinxron bo'lsin.
- Telegram progress, terminal summary va Allure bir xil test identity
  (`group`, `runner`, `test`, `Allure title`, nested step)dan foydalansin.
- Implementatsiya va execution authoritysi uchun
  [project-guide](../project-guide/SKILL.md#governance)ga amal qil.
- Infra knowledge'ni current behavior va historical evidence sifatida ajrat;
  eski kontraktni joriy qoida sifatida qoldirma.
