# Basic Telegram News Digest for macOS (no AI)

Collects RSS headlines and publisher-provided descriptions from seven topic groups and sends them to your Telegram bot. No AI API, OpenAI API key, or paid news API required.

## A. Create a Telegram bot
1. In Telegram, open @BotFather.
2. Send `/newbot`, follow the prompts, and copy the token securely.
3. Open your new bot and tap Start, then send `/start`.

## B. Install and configure on your Mac
Open Terminal and run these commands after extracting the ZIP and moving into the project folder:

```bash
python3 --version
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
open -e .env
```

Put your bot token in `TELEGRAM_BOT_TOKEN` in `.env`, save the file, then run:

```bash
python get_chat_id.py
```

Copy the printed chat ID into `TELEGRAM_CHAT_ID` in `.env`. Do not paste your bot token into chat or commit `.env` to Git.

## C. Send a test digest
```bash
chmod +x run_digest.sh
./run_digest.sh
```

Check Telegram. If it works, check `logs/digest.log` for execution details.

## D. Automate at 6 AM and 6 PM (Mac local time)
1. In Terminal, run `pwd` from the project directory and copy the full path.
2. Copy the template and replace both occurrences of `PROJECT_PATH` with that full path. Save it as `com.personal.telegramnews.plist` inside `~/Library/LaunchAgents/`.
3. Load it:

```bash
mkdir -p ~/Library/LaunchAgents
cp launchd/com.personal.telegramnews.plist.template ~/Library/LaunchAgents/com.personal.telegramnews.plist
# Replace PROJECT_PATH in that copied file with the full project path, e.g. /Users/your-user/telegram_news_digest_mac_basic
open -e ~/Library/LaunchAgents/com.personal.telegramnews.plist
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.personal.telegramnews.plist
launchctl enable gui/$(id -u)/com.personal.telegramnews
```

To test the scheduled job immediately:
```bash
launchctl kickstart -k gui/$(id -u)/com.personal.telegramnews
```

To stop automation:
```bash
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.personal.telegramnews.plist
```

`StartCalendarInterval` uses your Mac's local timezone. If the Mac is asleep at a scheduled time, launchd generally runs the job after wake; it cannot run while the Mac is shut down. Keep the Mac connected to the internet.

## Notes
- Feeds can change, fail, or have limited coverage; edit `feeds.py`.
- This script includes headlines, short RSS descriptions, source labels, and links. It does not fetch/repost full articles.
- This starter deduplicates within a single digest, not across morning/evening runs.
- Some publisher RSS feeds have terms restricting redistribution. This is for personal use; check each source's terms.
