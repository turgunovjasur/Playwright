FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN addgroup --system bot && adduser --system --ingroup bot bot

COPY deploy/playwright-ci-bot/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY scripts/telegram_ci_bot.py scripts/stop_ci_runs.py ./scripts/

USER bot

CMD ["python", "scripts/telegram_ci_bot.py"]
