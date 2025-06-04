import os
from threading import Thread
from flask import Flask
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

app = Flask(__name__)

@app.route('/')
def index():
    return "Bot is running"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Hi! Tax bot is here.")

def main():
    token = os.getenv("BOT_TOKEN")
    if not token:
        print("Error: BOT_TOKEN not set")
        return

    updater = Updater(token, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))

    Thread(target=run_flask).start()  # Start Flask server in background

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
