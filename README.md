# LeetCode Rating Tracker — Telegram Bot

Automated Telegram bot that fetches LeetCode contest ratings for students and posts a weekly leaderboard.

## Quick Start

```bash
pip install -r requirements.txt
python run.py
```

Set `BOT_TOKEN` and `CHAT_ID` in `.env` first.

## Commands

| Command | Description |
|---|---|
| `/start` | Welcome + command list |
| `/upload` | Send CSV/XLSX to add students |
| `/fetch` | Latest leaderboard + CSV |
| `/stats` | Fetch statistics |
| `/list` | All registered students |
| `/add <handle>` | Add a student |
| `/remove <handle>` | Remove a student |
| `/schedule` | Auto-fetch schedule |

## Structure

```
run.py              # Entry point
app/
├── bot.py          # Telegram bot + Flask health check
├── config.py       # Environment variables
├── database.py     # SQLite layer
├── fetcher.py      # LeetCode GraphQL API
├── parser.py       # CSV/XLSX parser
└── formatter.py    # Leaderboard/stats formatting
```

## Deploy

On Render: connect repo, set `python run.py` as start command, add env vars.
