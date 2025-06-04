import os
import requests
from bs4 import BeautifulSoup
import feedparser
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

def fetch_taxindiaonline():
    url = "https://taxindiaonline.com/RC2/TaxNews.asp"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    news_items = []
    # Assuming news are in <a> tags inside a certain div or section
    # Adjust selector as per actual site structure
    for a_tag in soup.select("table tr td a")[:5]:  # get top 5 links
        title = a_tag.text.strip()
        link = "https://taxindiaonline.com/RC2/" + a_tag.get('href')
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

def tax(update: Update, context: CallbackContext):
    messages = []

    # TaxIndiaOnline
    try:
        taxindia_news = fetch_taxindiaonline()
        messages.append("📰 TaxIndiaOnline News:\n" + "\n\n".join(taxindia_news))
    except Exception as e:
        messages.append("Failed to fetch TaxIndiaOnline news.")

    # Economic Times Tax RSS
    try:
        et_news = fetch_rss_feed("https://economictimes.indiatimes.com/rss/tax/rssfeeds/1145409.cms")
        messages.append("📰 Economic Times - Tax:\n" + "\n\n".join(et_news))
    except Exception as e:
        messages.append("Failed to fetch Economic Times news.")

    # LiveMint Policy RSS
    try:
        livemint_news = fetch_rss_feed("https://www.livemint.com/rss/news/policy.xml")
        messages.append("📰 LiveMint - Policy:\n" + "\n\n".join(livemint_news))
    except Exception as e:
        messages.append("Failed to fetch LiveMint news.")

    # Business Standard Tax RSS
    try:
        bs_news = fetch_rss_feed("https://www.business-standard.com/rss/economy-106.rss")
        messages.append("📰 Business Standard - Tax:\n" + "\n\n".join(bs_news))
    except Exception as e:
        messages.append("Failed to fetch Business Standard news.")

    # Send all combined messages (split if too long)
    full_message = "\n\n---\n\n".join(messages)
    for chunk in split_message(full_message):
        update.message.reply_text(chunk)

def split_message(message, max_length=4000):
    # Telegram message max length is 4096, leave buffer for safety
    return [message[i:i+max_length] for i in range(0, len(message), max_length)]

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Hi! Meesho Tax bot is here. Use /tax to get latest tax news.")

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

if __name__ == "__main__":
    main()
