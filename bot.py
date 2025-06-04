import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Hello! I'm your Tax Update Bot. Send /today to get today's tax updates."
    )

def today(update: Update, context: CallbackContext):
    # Placeholder message, we will add real scraping later
    update.message.reply_text("Today's tax updates will be here soon!")

def main():
    print("Bot is starting...")

    BOT_TOKEN = os.getenv("BOT_TOKEN")
    if not BOT_TOKEN:
        print("Error: BOT_TOKEN environment variable not set.")
        return

    updater = Updater(BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("today", today))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()