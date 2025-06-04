import os
import requests
import feedparser
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    print("Error: BOT_TOKEN not set")
    exit(1)

bot = Bot(token=BOT_TOKEN)
dispatcher = Dispatcher(bot, None, workers=0)

def fetch_google_news(query, max_items=5):
    """Fetches news from Google News RSS based on a query."""
    url = f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
    feed = feedparser.parse(url)
    news_items = []
    for entry in feed.entries[:max_items]:
        title = entry.title
        link = entry.link
        news_items.append(f"📰 {title}\n{link}")
    return news_items

def split_message(message, max_length=4000):
    return [message[i:i+max_length] for i in range(0, len(message), max_length)]

def send_split_message(update, text):
    for chunk in split_message(text):
        update.message.reply_text(chunk)

# /tax command
def tax(update, context):
    queries = [
        ("Indian Tax News", "income tax India"),
        ("E-commerce Tax (India)", "ecommerce tax India Amazon Flipkart Meesho"),
        ("Global E-commerce Tax", "ecommerce tax international")
    ]

    messages = []
    for title, query in queries:
        try:
            results = fetch_google_news(query)
            messages.append(f"📌 {title}:\n\n" + "\n\n".join(results))
        except Exception:
            messages.append(f"❌ Failed to fetch {title}")

    send_split_message(update, "\n\n---\n\n".join(messages))

# /caselaws command
def caselaws(update, context):
    try:
        results = fetch_google_news("income tax case laws India")
        message = "📜 Recent Tax Case Laws:\n\n" + "\n\n".join(results)
    except Exception:
        message = "❌ Failed to fetch tax case laws."
    send_split_message(update, message)

# /ipo command
def ipo(update, context):
    try:
        results = fetch_google_news("latest IPO India")
        message = "🚀 Latest IPO News (India):\n\n" + "\n\n".join(results)
    except Exception:
        message = "❌ Failed to fetch IPO news."
    send_split_message(update, message)

def start(update, context):
    update.message.reply_text(
        "👋 Welcome to the Tax Bot!\n\n"
        "Commands:\n"
        "/tax – Latest tax & ecommerce news\n"
        "/caselaws – Recent tax case laws\n"
        "/ipo – Latest IPO news"
    )

# Register commands
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("tax", tax))
dispatcher.add_handler(CommandHandler("caselaws", caselaws))
dispatcher.add_handler(CommandHandler("ipo", ipo))

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK"

@app.route("/")
def index():
    return "Bot is running."

if __name__ == "__main__":
    # Replace this URL with your actual Render app URL before deploying
    WEBHOOK_URL = f"https://telegramtax.onrender.com/8107230560:AAFAkk7OgTTCuheki8z58dm1ei3hPY8e9hc"
    bot.set_webhook(url=WEBHOOK_URL)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
