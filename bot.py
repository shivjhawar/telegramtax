import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Hi! Meesho Tax bot is here.")

def tax(update: Update, context: CallbackContext):
    update.message.reply_text("Here is your latest tax update: GST filing deadline is 10th June.")

def main():
    token = os.getenv("BOT_TOKEN")
    if not token:
        print("Error: BOT_TOKEN not set")
        return

    updater = Updater(token, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("tax", tax))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
