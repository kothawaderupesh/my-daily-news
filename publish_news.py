import html
import json
import logging
import os
import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

import feedparser
import requests
from feeds import FEEDS

MAX_PER_CATEGORY = int(os.getenv("MAX_PER_CATEGORY", "4"))
OUTPUT = Path("docs/news.json")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def clean(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", value or "")
    return html.unescape(re.sub(r"\s+", " ", value)).strip()


def published_at(entry) -> str:
    try:
        if entry.get("published"):
            return parsedate_to_datetime(entry.published).isoformat()
        if entry.get("updated_parsed"):
            from datetime import datetime
            return datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc).isoformat()
    except Exception:
        pass
    return ""


def get_stories(category, sources):
    stories = []
    seen = set()

    for source, url in sources:
        try:
            response = requests.get(
                url,
                headers={"User-Agent": "PersonalNewsDigest/1.0"},
                timeout=20,
            )
            response.raise_for_status()
            feed = feedparser.parse(response.content)

            for item in feed.entries:
                title = clean(item.get("title", ""))
                link = item.get("link", "")
                if not title or not link:
                    continue

                key = re.sub(r"\W+", "", title.lower())
                if key in seen:
                    continue
                seen.add(key)

                summary = clean(item.get("summary", item.get("description", "")))
                stories.append({
                    "title": title,
                    "summary": summary[:1200],
                    "source": source,
                    "link": link,
                    "published": published_at(item),
                })
        except Exception as exc:
            logging.warning("Feed failed (%s): %s", source, exc)

    stories.sort(key=lambda story: story["published"], reverse=True)
    return stories[:MAX_PER_CATEGORY]


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "timezone_note": "generated_at is UTC",
        "categories": [],
    }

    total = 0
    for category, sources in FEEDS.items():
        stories = get_stories(category, sources)
        total += len(stories)
        payload["categories"].append({
            "name": category,
            "stories": stories,
        })

    payload["total_stories"] = total
    OUTPUT.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    logging.info("Wrote %s stories to %s", total, OUTPUT)


if __name__ == "__main__":
    main()
