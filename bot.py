import os
import logging
import asyncio
from flask import Flask
from threading import Thread
from dotenv import load_dotenv

load_dotenv()

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

from config import BOT_TOKEN, CHAT_ID, SCHEDULE_DAY, SCHEDULE_TIME, TEMP_DIR
from database import init_db, add_students_batch, get_active_students, get_all_students, deactivate_student, save_fetch_result, get_latest_results, get_stats, get_student_count, get_last_fetch_time, add_student
from fetcher import LeetCodeFetcher
from parser import parse_file
from formatter import format_leaderboard, format_stats, format_student_list, generate_csv_file

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)

fetch_in_progress = False

async def do_fetch(context: ContextTypes.DEFAULT_TYPE, chat_id: str, label: str = "Fetch"):
    global fetch_in_progress
    if fetch_in_progress:
        await context.bot.send_message(chat_id=chat_id, text="⏳ A fetch is already in progress.")
        return

    fetch_in_progress = True
    try:
        students = get_active_students()
        if not students:
            await context.bot.send_message(chat_id=chat_id, text="📭 No students registered.")
            return

        total = len(students)
        await context.bot.send_message(chat_id=chat_id, text=f"🚀 {label}: Fetching ratings for {total} students...")

        fetcher = LeetCodeFetcher()
        results = []

        for idx, student in enumerate(students):
            data = fetcher.fetch_single(student["leetcode_username"])
            data["student_id"] = student["id"]
            data["name"] = student["name"]
            data["roll_number"] = student["roll_number"]
            data["leetcode_username"] = student["leetcode_username"]
            results.append(data)
            save_fetch_result(student["id"], data["rating"], data["global_rank"], data["contests_attended"], data["top_pct"], data["success"])

            if (idx + 1) % 50 == 0 or idx + 1 == total:
                try:
                    await context.bot.send_message(chat_id=chat_id, text=f"⏳ {idx + 1}/{total} processed")
                except Exception:
                    pass

        leaderboard = format_leaderboard(results)
        await context.bot.send_message(chat_id=chat_id, text=leaderboard, parse_mode="Markdown")

        csv_path = os.path.join(TEMP_DIR, "leaderboard.csv")
        generate_csv_file(results, csv_path)
        with open(csv_path, "rb") as f:
            await context.bot.send_document(chat_id=chat_id, document=f, filename="leaderboard.csv")

        successful = sum(1 for r in results if r["success"])
        await context.bot.send_message(chat_id=chat_id, text=f"✅ {label} complete! {successful}/{total} fetched successfully.")
        logger.info(f"{label} complete: {successful}/{total}")
    finally:
        fetch_in_progress = False

async def weekly_fetch_job(context: ContextTypes.DEFAULT_TYPE):
    logger.info("Running scheduled weekly auto-fetch")
    if not CHAT_ID:
        logger.error("CHAT_ID not set")
        return
    await do_fetch(context, CHAT_ID, label="Weekly Auto-Fetch")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome = (
        "👋 *Welcome to LeetCode Rating Tracker!*\n\n"
        "*Commands:*\n"
        "/upload — Send a CSV/XLSX file to add students and fetch ratings\n"
        "/fetch — Show latest leaderboard and download CSV\n"
        "/stats — View fetch statistics\n"
        "/list — View all registered students\n"
        "/add <handle> — Add a single student\n"
        "/remove <handle> — Remove a student\n"
        "/schedule — Show auto-fetch schedule\n"
        "/help — Show this message"
    )
    await context.bot.send_message(chat_id=update.effective_chat.id, text=welcome, parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if str(chat_id) != str(CHAT_ID):
        await context.bot.send_message(chat_id=chat_id, text="⛔ Unauthorized.")
        return

    doc = update.message.document
    if not doc:
        await context.bot.send_message(chat_id=chat_id, text="📁 Please send a CSV or XLSX file.")
        return

    filename = doc.file_name
    if not filename.lower().endswith((".csv", ".xlsx")):
        await context.bot.send_message(chat_id=chat_id, text="⚠️ Only CSV and XLSX files are supported.")
        return

    await context.bot.send_message(chat_id=chat_id, text=f"📥 Downloading {filename}...")

    file = await context.bot.get_file(doc.file_id)
    filepath = os.path.join(TEMP_DIR, filename)
    await file.download_to_drive(filepath)

    await context.bot.send_message(chat_id=chat_id, text="🔍 Parsing file...")

    students, error = parse_file(filepath)
    if error:
        await context.bot.send_message(chat_id=chat_id, text=f"❌ {error}")
        return

    if not students:
        await context.bot.send_message(chat_id=chat_id, text="⚠️ No valid students found in file.")
        return

    new_count, dup_count = add_students_batch(students)

    msg = f"✅ *File Processed*\n\n"
    msg += f"📊 Total records: {len(students)}\n"
    msg += f"➕ New students added: {new_count}\n"
    msg += f"⏭️ Duplicates skipped: {dup_count}"

    total, active = get_student_count()
    msg += f"\n👥 Total registered: {total} ({active} active)"

    await context.bot.send_message(chat_id=chat_id, text=msg, parse_mode="Markdown")

    try:
        os.remove(filepath)
    except Exception:
        pass

    await context.bot.send_message(chat_id=chat_id, text="🔎 Now fetching ratings for all students...", parse_mode="Markdown")
    await do_fetch(context, chat_id, label="📥 File Upload Fetch")

async def fetch_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if str(chat_id) != str(CHAT_ID):
        await context.bot.send_message(chat_id=chat_id, text="⛔ Unauthorized.")
        return

    results = get_latest_results()
    if not results:
        await context.bot.send_message(chat_id=chat_id, text="📭 No data yet. Upload a file with /upload first.")
        return

    msg = format_leaderboard(results)
    await context.bot.send_message(chat_id=chat_id, text=msg, parse_mode="Markdown")

    csv_path = os.path.join(TEMP_DIR, "leaderboard.csv")
    generate_csv_file(results, csv_path)
    with open(csv_path, "rb") as f:
        await context.bot.send_document(chat_id=chat_id, document=f, filename="leaderboard.csv")

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if str(chat_id) != str(CHAT_ID):
        await context.bot.send_message(chat_id=chat_id, text="⛔ Unauthorized.")
        return

    stats = get_stats()
    last_fetch = get_last_fetch_time()
    total, active = get_student_count()

    if not stats or stats.get("total", 0) == 0:
        await context.bot.send_message(chat_id=chat_id, text="📭 No fetch data yet. Upload a file first with /upload.")
        return

    msg = f"👥 Students: {active} active / {total} total\n\n" + format_stats(stats, last_fetch)
    await context.bot.send_message(chat_id=chat_id, text=msg, parse_mode="Markdown")

async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if str(chat_id) != str(CHAT_ID):
        await context.bot.send_message(chat_id=chat_id, text="⛔ Unauthorized.")
        return

    students = get_all_students()
    msg = format_student_list(students)
    await context.bot.send_message(chat_id=chat_id, text=msg, parse_mode="Markdown")

async def add_single(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if str(chat_id) != str(CHAT_ID):
        await context.bot.send_message(chat_id=chat_id, text="⛔ Unauthorized.")
        return

    if not context.args:
        await context.bot.send_message(chat_id=chat_id, text="⚠️ Usage: /add <leetcode_username>")
        return

    username = context.args[0]
    success = add_student("", "", username)
    if success:
        await context.bot.send_message(chat_id=chat_id, text=f"✅ Added `{username}`", parse_mode="Markdown")
    else:
        await context.bot.send_message(chat_id=chat_id, text=f"⚠️ `{username}` already exists", parse_mode="Markdown")

async def remove_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if str(chat_id) != str(CHAT_ID):
        await context.bot.send_message(chat_id=chat_id, text="⛔ Unauthorized.")
        return

    if not context.args:
        await context.bot.send_message(chat_id=chat_id, text="⚠️ Usage: /remove <leetcode_username>")
        return

    username = context.args[0]
    deleted = deactivate_student(username)
    if deleted:
        await context.bot.send_message(chat_id=chat_id, text=f"✅ Removed `{username}`", parse_mode="Markdown")
    else:
        await context.bot.send_message(chat_id=chat_id, text=f"⚠️ `{username}` not found", parse_mode="Markdown")

async def schedule_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if str(chat_id) != str(CHAT_ID):
        await context.bot.send_message(chat_id=chat_id, text="⛔ Unauthorized.")
        return

    await context.bot.send_message(chat_id=chat_id, text=f"🕒 Weekly auto-fetch: Every {SCHEDULE_DAY.capitalize()} at {SCHEDULE_TIME}")

def setup_scheduler(application):
    time_parts = SCHEDULE_TIME.split(":")
    from datetime import time as dt_time
    schedule_time = dt_time(hour=int(time_parts[0]), minute=int(time_parts[1]))

    day_to_weekday = {
        "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
        "friday": 4, "saturday": 5, "sunday": 6,
    }

    weekday = day_to_weekday.get(SCHEDULE_DAY.lower(), 0)

    application.job_queue.run_daily(
        weekly_fetch_job,
        schedule_time,
        days=(weekday,),
        name="weekly_fetch",
    )
    logger.info(f"Scheduled auto-fetch: {SCHEDULE_DAY.capitalize()} at {SCHEDULE_TIME}")

def run_bot():
    init_db()

    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("fetch", fetch_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("list", list_command))
    application.add_handler(CommandHandler("add", add_single))
    application.add_handler(CommandHandler("remove", remove_command))
    application.add_handler(CommandHandler("schedule", schedule_command))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_file))

    async def error_handler(update, context):
        logger.error(f"Error: {context.error}")

    application.add_error_handler(error_handler)

    setup_scheduler(application)

    logger.info("Bot started...")
    application.run_polling(poll_interval=2.0)

@app.route("/")
def health():
    return "OK"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    if not BOT_TOKEN:
        print("ERROR: Set BOT_TOKEN environment variable")
        exit(1)

    Thread(target=run_flask, daemon=True).start()
    run_bot()
