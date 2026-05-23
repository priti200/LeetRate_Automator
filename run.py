from threading import Thread
from app.bot import run_bot, run_flask
from app.config import BOT_TOKEN

if __name__ == "__main__":
    if not BOT_TOKEN:
        print("ERROR: Set BOT_TOKEN environment variable")
        exit(1)

    Thread(target=run_flask, daemon=True).start()
    run_bot()
