import os
import requests
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("TELEGRAM_BOT_TOKEN")
if not token or token == "put_your_bot_token_here":
    token = input("Paste your bot token (input is visible; don't share it): ").strip()

r = requests.get(f"https://api.telegram.org/bot{token}/getUpdates", timeout=20)
r.raise_for_status()
updates = r.json().get("result", [])
if not updates:
    print("No messages found. Open your bot in Telegram, press Start, send /start, then run this script again.")
else:
    seen = set()
    for update in updates:
        message = update.get("message") or update.get("channel_post") or {}
        chat = message.get("chat", {})
        if chat and chat.get("id") not in seen:
            seen.add(chat.get("id"))
            print(f"Chat ID: {chat.get('id')} | Name: {chat.get('first_name') or chat.get('title') or 'Telegram chat'}")
