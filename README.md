# LeetCode Rating Tracker — Telegram Bot

Fully automated Telegram bot that fetches LeetCode contest ratings for students and posts a weekly leaderboard every Monday.

## Features
- 🤖 **Telegram Bot Interface**: Control everything from Telegram
- 📁 **CSV/XLSX Upload**: Send a file via chat to add students
- 🚀 **One-Command Fetch**: `/fetch` to pull ratings for all students
- 🏆 **Auto Leaderboard**: Formatted leaderboard with medals + CSV download
- 🕒 **Weekly Auto-Post**: Every Monday at 10:00 AM (configurable)
- 💾 **SQLite Storage**: Persistent student data and fetch history
- 📊 **Stats**: Average rating, top performer, success rate

## Setup

### 1. Create a Telegram Bot
1. Message `@BotFather` on Telegram
2. Send `/newbot`
3. Follow prompts to name your bot
4. Copy the **BOT_TOKEN**

### 2. Get Your Chat ID
1. Send any message to your bot
2. Visit: `https://api.telegram.org/bot<BOT_TOKEN>/getUpdates`
3. Find `"chat": {"id": -100xxxxxxx}` — that number is your **CHAT_ID**

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Environment Variables
```bash
export BOT_TOKEN="your_token_here"
export CHAT_ID="your_chat_id_here"
export SCHEDULE_DAY="monday"
export SCHEDULE_TIME="10:00"
```

### 5. Run the Bot
```bash
python bot.py
```

## Bot Commands

| Command | Description |
|---|---|
| `/start` | Welcome message + command list |
| `/upload` | Send a CSV/XLSX file to add students |
| `/fetch` | Manually fetch ratings for all active students |
| `/leaderboard` | View current leaderboard + download CSV |
| `/stats` | View fetch statistics |
| `/list` | View all registered students |
| `/add <handle>` | Add a single student by LeetCode username |
| `/remove <handle>` | Remove a student from tracking |
| `/schedule` | Show current auto-fetch schedule |
| `/help` | Show all commands |

## File Upload Format

Your CSV/XLSX file should have these columns (in order):
1. ID
2. Start time
3. Completion time
4. Email
5. **Name** (student name)
6. Last modified time
7. **Roll number**
8. Name (as it appears in AUMS)
9. Programme
10. **Leetcode handle/userid** (username or full URL)

## Deploy to Render (Free)

### 1. Push to GitHub
```bash
git add .
git commit -m "Telegram bot for LeetCode ratings"
git push
```

### 2. Deploy on Render
1. Go to https://render.com → New Web Service
2. Connect your GitHub repo
3. Settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python bot.py`
   - **Instance Type**: Free
4. Add Environment Variables:
   - `BOT_TOKEN` = your bot token
   - `CHAT_ID` = your chat ID
   - `SCHEDULE_DAY` = monday
   - `SCHEDULE_TIME` = 10:00

### 3. Keep It Alive (Important for Free Tier)
Render free tier spins down after 15 minutes of inactivity. Use **UptimeRobot** (free):
1. Go to https://uptimerobot.com
2. Create a monitor for your Render URL
3. Set interval to 5 minutes
4. This keeps the bot running 24/7

## Architecture

```
bot.py (Flask + Telegram Bot + APScheduler)
├── database.py   (SQLite: students + fetch_history)
├── fetcher.py    (LeetCode GraphQL API with retry/backoff)
├── parser.py     (CSV/XLSX file parser)
├── formatter.py  (Telegram message formatting)
└── config.py     (Environment variables)
```

## Database

SQLite (`leetcode_bot.db`) stores:
- **students**: name, roll_number, leetcode_username, active status
- **fetch_history**: rating, global_rank, contests, timestamp per fetch

## Troubleshooting

- **Bot not responding**: Check `BOT_TOKEN` is correct
- **Messages not sent to chat**: Verify `CHAT_ID` matches your group/channel
- **Rate limits (429)**: Bot handles this automatically with exponential backoff
- **Render spins down**: Set up UptimeRobot to ping every 5 minutes
