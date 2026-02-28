# scripts

Utility scripts used with the local OpenClaw automations.

## Contents

- `scripts/tech_news.py` — pulls top technology stories (Hacker News + Algolia API) for daily briefings.
- `scripts/global_news.py` — aggregates top global headlines from Al Jazeera’s RSS feed.

These scripts are designed to run inside the OpenClaw workspace and power scheduled cron jobs (tech digest at 8:00 PM IST, global brief at 8:05 PM IST).

## Usage

From the workspace root:

```bash
./scripts/tech_news.py
./scripts/global_news.py
```

Both scripts format Markdown-friendly digests suitable for Telegram delivery.
