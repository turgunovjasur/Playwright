# Playwright Project Bootstrap

Bu repo uchun barcha doimiy AI ko'rsatmalari va loyiha bilimlarining yagona
ishonchli manbasi — repo root'idagi `skills/`.

Har qanday repo vazifasidan oldin:

1. `skills/project-guide/SKILL.md` ni o'qi va u yerdagi authority, routing,
   ownership va write-back qoidalariga amal qil.
2. Vazifaga mos skillni `skills/<name>/SKILL.md` dan o'qi; kerakli reference
   fayllarnigina och.
3. `.agents/skills/` va `.claude/skills/` faqat `skills/`ga symlink
   entry-pointlar; ularda alohida bilim saqlama.
4. Skill yoki knowledge-base o'zgarsa
   `./.venv/bin/python skills/scripts/validate_skills.py` ni ishlat.

`skills/project-guide/SKILL.md` ro'yxatda ko'rinmasa ham uni to'g'ridan-to'g'ri
o'qish majburiy.
