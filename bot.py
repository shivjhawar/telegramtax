import os
import requests
from bs4 import BeautifulSoup
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

def fetch_taxindiaonline():
    url = "https://taxindiaonline.com/RC2/TaxNews.asp"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    news_items = []
    for a_tag in soup.select("table tr td a")[:5]:
        title = a_tag.text.strip()
        href = a_tag.get('href')
        if href:
            link = "https://taxindiaonline.com/RC2/" + href
            news_items.append(f"{title}\n{link}")
    return news_items

def fetch_rss_feed(feed_url, max_items=5):
    news_items = []
    feed = feedparser.parse(feed_url)
    for entry in feed.entries[:max_items]:
        title = entry.title
        link = entry.link
        news_items.append(f"{title}\n{link}")
    return news_items

def fetch_google_news(query, max_items=5):
    """Fetches Google News RSS for given query"""
    url = f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
    return fetch_rss_feed(url, max_items)

def fetch_taxguru_caselaws(max_items=5):
    """Scrape latest tax case laws from TaxGuru"""
    url = "https://taxguru.in/tag/income-tax-case-laws/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    case_laws = []
    articles = soup.select("article")[:max_items]
    for article in articles:
        title_tag = article.select_one("h2.entry-title a")
        if title_tag:
            title = title_tag.text.strip()
            link = title_tag['href']
            case_laws.append(f"{title}\n{link}")
    return case_laws

def split_message(message, max_length=4000):
    return [message[i:i+max_length] for i in range(0, len(message), max_length)]

def tax(update, context):
    messages = []

    # TaxIndiaOnline News
    try:
        taxindia_news = fetch_taxindiaonline()
        messages.append("📰 TaxIndiaOnline News:\n" + "\n\n".join(taxindia_news))
    except Exception:
        messages.append("Failed to fetch TaxIndiaOnline news.")

    # Economic Times - Tax RSS
    try:
        et_news = fetch_rss_feed("https://economictimes.indiatimes.com/rss/tax/rssfeeds/1145409.cms")
        messages.append("📰 Economic Times - Tax:\n" + "\n\n".join(et_news))
    except Exception:
        messages.append("Failed to fetch Economic Times news.")

    # LiveMint Policy RSS
    try:
        livemint_news = fetch_rss_feed("https://www.livemint.com/rss/news/policy.xml")
        messages.append("📰 LiveMint - Policy:\n" + "\n\n".join(livemint_news))
    except Exception:
        messages.append("Failed to fetch LiveMint news.")

    # Business Standard RSS
    try:
        bs_news = fetch_rss_feed("https://www.business-standard.com/rss/economy-106.rss")
        messages.append("📰 Business Standard - Tax:\n" + "\n\n".join(bs_news))
    except Exception:
        messages.append("Failed to fetch Business Standard news.")

    # E-commerce Tax News (India) via Google News
    try:
        ecommerce_news = fetch_google_news("ecommerce tax India Amazon Flipkart Meesho")
        messages.append("🛒 E-commerce Tax News (India):\n" + "\n\n".join(ecommerce_news))
    except Exception:
        messages.append("Failed to fetch E-commerce tax news.")

    # Global E-commerce Tax News
    try:
        global_ecommerce_news = fetch_google_news("ecommerce tax international")
        messages.append("🌎 Global E-commerce Tax News:\n" + "\n\n".join(global_ecommerce_news))
    except Exception:
        messages.append("Failed to fetch global E-commerce tax news.")

    full_message = "\n\n---\n\n".join(messages)
    for chunk in split_message(full_message):
        update.message.reply_text(chunk)

def caselaws(update, context):
    try:
        case_laws = fetch_taxguru_caselaws()
        if case_laws:
            message = "📜 Recent Tax Case Laws from TaxGuru:\n\n" + "\n\n".join(case_laws)
        else:
            message = "No recent tax case laws found."
    except Exception:
        message = "Failed to fetch tax case laws."

    for chunk in split_message(message):
        update.message.reply_text(chunk)

def ipo(update, context):
    try:
        ipo_news = fetch_rss_feed("https://economictimes.indiatimes.com/ipo/rssfeeds/29739109.cms")
        if ipo_news:
            message = "🚀 Latest IPO News (India):\n\n" + "\n\n".join(ipo_news)
        else:
            message = "No recent IPO news found."
    except Exception:
        message = "Failed to fetch IPO news."

    for chunk in split_message(message):
        update.message.reply_text(chunk)

def start(update, context):
    update.message.reply_text(
        "Hi! Meesho Tax bot is here.\n\n"
        "Use /tax to get latest tax and e-commerce tax news.\n"
        "Use /caselaws to get recent tax case laws.\n"
        "Use /ipo to get latest IPO news from India."
    )

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
