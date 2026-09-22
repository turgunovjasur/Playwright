FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN addgroup --system bot && adduser --system --ingroup bot bot

COPY telegram_bot/deploy/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY telegram_bot/*.py telegram_bot/telegram_ci_config.json ./telegram_bot/

USER bot

CMD ["python", "telegram_bot/telegram_ci_bot.py"]
