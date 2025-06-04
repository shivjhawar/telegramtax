import os
import requests
from bs4 import BeautifulSoup
import feedparser
from urllib.parse import quote
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

def fetch_taxindiaonline():
    url = "https://taxindiaonline.com/RC2/TaxNews.asp"
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')

    news_items = []
    for a_tag in soup.select("table tr td a")[:5]:
        title = a_tag.text.strip()
        href = a_tag.get('href')
        if href and title:
            link = "https://taxindiaonline.com/RC2/" + href
            news_items.append(f"{title}\n{link}")
    return news_items

def fetch_rss_feed(feed_url, max_items=5):
    news_items = []
    feed = feedparser.parse(feed_url)
    for entry in feed.entries[:max_items]:
        title = entry.get("title", "").strip()
        link = entry.get("link", "").strip()
        if title and link:
            news_items.append(f"{title}\n{link}")
    return news_items

def fetch_google_news(query="tax india", max_items=5):
    feed_url = f"https://news.google.com/rss/search?q={quote(query)}&hl=en-IN&gl=IN&ceid=IN:en"
    return fetch_rss_feed(feed_url, max_items)

def fetch_pib_news(max_items=5):
    feed_url = "https://pib.gov.in/PressReleseRSS.aspx"
    return fetch_rss_feed(feed_url, max_items)

def split_message(message, max_length=4000):
    return [message[i:i+max_length] for i in range(0, len(message), max_length)]

def tax(update, context):
    messages = []

    try:
        google_news = fetch_google_news()
        messages.append("📰 Google News - Tax India:\n" + "\n\n".join(google_news))
    except Exception as e:
        print("Google News error:", e)
        messages.append("Failed to fetch Google News.")

    try:
        pib_news = fetch_pib_news()
        messages.append("📰 PIB - Govt. News:\n" + "\n\n".join(pib_news))
    except Exception as e:
        print("PIB error:", e)
        messages.append("Failed to fetch PIB news.")

    try:
        taxindia_news = fetch_taxindiaonline()
        messages.append("📰 TaxIndiaOnline:\n" + "\n\n".join(taxindia_news))
    except Exception as e:
        print("TaxIndiaOnline error:", e)
        messages.append("Failed to fetch TaxIndiaOnline news.")

    try:
        et_news = fetch_rss_feed("https://economictimes.indiatimes.com/rss/tax/rssfeeds/1145409.cms")
        messages.append("📰 Economic Times - Tax:\n" + "\n\n".join(et_news))
    except Exception as e:
        print("ET error:", e)
        messages.append("Failed to fetch Economic Times news.")

    try:
        livemint_news = fetch_rss_feed("https://www.livemint.com/rss/news/policy.xml")
        messages.append("📰 LiveMint - Policy:\n" + "\n\n".join(livemint_news))
    except Exception as e:
        print("LiveMint error:", e)
        messages.append("Failed to fetch LiveMint news.")

    try:
        bs_news = fetch_rss_feed("https://www.business-standard.com/rss/economy-106.rss")
        messages.append("📰 Business Standard - Tax:\n" + "\n\n".join(bs_news))
    except Exception as e:
        print("BS error:", e)
        messages.append("Failed to fetch Business Standard news.")

    full_message = "\n\n---\n\n".join(messages)
    for chunk in split_message(full_message):
        update.message.reply_text(chunk, disable_web_page_preview=True)

def start(update, context):
    update.message.reply_text("Hi! Meesho Tax bot is here. Use /tax to get latest tax news.")

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("tax", tax))

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
