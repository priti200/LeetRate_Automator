import os

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
CHAT_ID = os.environ.get("CHAT_ID", "")

SCHEDULE_DAY = os.environ.get("SCHEDULE_DAY", "monday")
SCHEDULE_TIME = os.environ.get("SCHEDULE_TIME", "10:00")

DATABASE_FILE = "leetcode_bot.db"
TEMP_DIR = "temp_uploads"

FETCH_DELAY = 2
FETCH_MAX_RETRIES = 3
FETCH_BACKOFF_BASE = 30
PROGRESS_INTERVAL = 10
LEADERBOARD_TOP = 10

os.makedirs(TEMP_DIR, exist_ok=True)
