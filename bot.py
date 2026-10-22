import html
import os
import re
import logging
from datetime import datetime
from email.utils import parsedate_to_datetime

import feedparser
import requests
from dotenv import load_dotenv
from feeds import FEEDS

load_dotenv()
TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
MAX_PER_CATEGORY = int(os.getenv("MAX_PER_CATEGORY", "4"))
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

def clean(text):
    text = re.sub(r"<[^>]+>", " ", text or "")
    return html.unescape(re.sub(r"\s+", " ", text)).strip()

def timestamp(entry):
    try:
        if entry.get("published"):
            return parsedate_to_datetime(entry.published).timestamp()
        if entry.get("updated_parsed"):
            return datetime(*entry.updated_parsed[:6]).timestamp()
    except Exception:
        pass
    return 0

def get_stories(category, sources):
    stories, seen = [], set()
    for source, url in sources:
        try:
            response = requests.get(url, headers={"User-Agent": "PersonalNewsDigest/1.0"}, timeout=20)
            response.raise_for_status()
            feed = feedparser.parse(response.content)
            for item in feed.entries:
                title, link = clean(item.get("title", "")), item.get("link", "")
                if not title or not link:
                    continue
                key = re.sub(r"\W+", "", title.lower())
                if key in seen:
                    continue
                seen.add(key)
                summary = clean(item.get("summary", item.get("description", "")))
                stories.append({"title": title, "link": link, "summary": summary, "source": source, "time": timestamp(item)})
        except Exception as exc:
            logging.warning("Feed failed (%s): %s", source, exc)
    stories.sort(key=lambda x: x["time"], reverse=True)
    return stories[:MAX_PER_CATEGORY]

def send_message(text):
    # Telegram allows up to 4096 characters per text message.
    chunks, current = [], ""
    for line in text.splitlines():
        candidate = current + "\n" + line if current else line
        if len(candidate) > 3800 and current:
            chunks.append(current)
            current = line
        else:
            current = candidate
    if current:
        chunks.append(current)
    for chunk in chunks:
        r = requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            json={"chat_id": CHAT_ID, "text": chunk, "disable_web_page_preview": True},
            timeout=20,
        )
        r.raise_for_status()
        if not r.json().get("ok"):
            raise RuntimeError(r.text)

def main():
    now = datetime.now().astimezone()
    parts = [f"🗞 PERSONAL NEWS DIGEST\n{now.strftime('%A, %d %B %Y · %I:%M %p %Z')}",
             "Headlines and publisher descriptions only — no AI summaries."]
    count = 0
    for category, sources in FEEDS.items():
        stories = get_stories(category, sources)
        parts.append(f"\n━━ {category.upper()} ━━")
        if not stories:
            parts.append("No stories fetched from configured feeds.")
            continue
        for story in stories:
            count += 1
            summary = story["summary"]
            if len(summary) > 260:
                summary = summary[:257].rsplit(" ", 1)[0] + "…"
            parts.append(f"\n• {story['title']}")
            if summary:
                parts.append(f"  {summary}")
            parts.append(f"  Source: {story['source']}\n  {story['link']}")
    parts.append(f"\nTotal stories: {count}")
    send_message("\n".join(parts))
    logging.info("Digest sent (%s stories)", count)

if __name__ == "__main__":
    main()
