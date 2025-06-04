import os
import feedparser
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    print("❌ Error: BOT_TOKEN not set in environment variables.")
    exit(1)

bot = Bot(token=BOT_TOKEN)
dispatcher = Dispatcher(bot, None, workers=0)


# ------------- Utility Functions ------------------

def fetch_google_news_rss(query, max_items=5):
    """Fetch Google News RSS feed based on a search query."""
    query_encoded = query.replace(" ", "+")
    url = f"https://news.google.com/rss/search?q={query_encoded}&hl=en-IN&gl=IN&ceid=IN:en"
    feed = feedparser.parse(url)

    news_items = []
    for entry in feed.entries[:max_items]:
        title = entry.title
        link = entry.link
        if "google.com" in link:
            # Google redirects, fix actual link
            link = entry.link.split('url=')[-1] if 'url=' in entry.link else entry.link
        news_items.append(f"📰 {title}\n🔗 {link}")
    return news_items


def split_message(message, max_length=4096):
    """Splits long messages into chunks Telegram can handle."""
    return [message[i:i+max_length] for i in range(0, len(message), max_length)]


def send_news(update, context, topic_title, query):
    try:
        news_items = fetch_google_news_rss(query)
        if not news_items:
            update.message.reply_text(f"No news found for {topic_title}.")
        else:
            message = f"📢 {topic_title}:\n\n" + "\n\n".join(news_items)
            for chunk in split_message(message):
                update.message.reply_text(chunk)
    except Exception as e:
        update.message.reply_text(f"❌ Error fetching news for {topic_title}.\nDetails: {e}")


# ------------- Command Handlers ------------------

def start(update, context):
    update.message.reply_text(
        "👋 Welcome to the TaxBot!\n\n"
        "Use the following commands:\n"
        "🧾 /tax – Latest Indian & global tax news\n"
        "⚖️ /caselaws – Recent tax case laws\n"
        "📈 /ipo – Latest Indian IPO news"
    )

def tax(update, context):
    queries = [
        ("Indian Tax News", "income tax India"),
        ("E-commerce Tax (India)", "ecommerce gst amazon flipkart meesho"),
        ("Global Tax on E-commerce", "ecommerce tax international")
    ]
    for title, query in queries:
        send_news(update, context, title, query)

def caselaws(update, context):
    send_news(update, context, "Recent Tax Case Laws", "income tax case law India")

def ipo(update, context):
    send_news(update, context, "Latest IPO News in India", "latest IPO India")


# ------------- Register Handlers ------------------

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("tax", tax))
dispatcher.add_handler(CommandHandler("caselaws", caselaws))
dispatcher.add_handler(CommandHandler("ipo", ipo))


# ------------- Webhook + Index Routes ------------------

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
