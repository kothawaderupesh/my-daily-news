# iPhone Shortcuts news endpoint files

These files adapt the existing RSS project so GitHub Actions publishes a JSON news digest that your iPhone Shortcut can retrieve. Apple Intelligence summarizes the JSON on the iPhone; no separate AI API key is used.

## Add these files to your existing repository

Copy the contents of this folder into the root of your existing news project, preserving the directory structure. Keep your existing `feeds.py` and `requirements.txt`.

Files included:
- `publish_news.py` — fetches stories from your existing `feeds.py` and writes `docs/news.json`.
- `.github/workflows/news-digest.yml` — replaces the old Telegram-sending workflow with a scheduled JSON publisher.
- `docs/.nojekyll` — lets GitHub Pages serve the docs folder as-is.

## Important: public endpoint

GitHub Pages serves `docs/news.json` publicly. The file contains public RSS headlines, descriptions, sources, and links only. Do not put credentials, tokens, personal data, or secrets in `docs/`.

## Install

1. Back up your existing `.github/workflows/news-digest.yml`.
2. Copy the supplied files into your repository. The supplied workflow replaces the old Telegram workflow so it no longer sends Telegram messages.
3. Confirm `requirements.txt` includes `feedparser` and `requests` (your starter project already has them).
4. Commit and push the files.
5. In GitHub, go to **Settings → Pages**.
6. Under **Build and deployment**, choose **Deploy from a branch**.
7. Choose your default branch (usually `main`) and folder `/docs`, then Save.
8. Go to **Actions → Publish News for iPhone Shortcut → Run workflow** to run it once.

After Pages finishes deploying, your JSON endpoint should be:

`https://YOUR_GITHUB_USERNAME.github.io/YOUR_REPOSITORY_NAME/news.json`

Replace both placeholders. Open that address in Safari to confirm it displays JSON. GitHub Pages can take a few minutes to publish for the first time.

## iPhone Shortcut

In Shortcuts:
1. Add **Get Contents of URL** and enter your `.../news.json` URL.
2. Add **Use Model** (On-Device) and pass the URL action's result as the input.
3. In the model instructions, ask it to summarize the supplied JSON into the seven categories, include headline/summary/why-it-matters/source link, and not invent facts.
4. Add **Show Result** after **Use Model**.
5. Run manually first. Then create Time of Day automations for 6:00 AM and 6:00 PM.

The GitHub schedule refreshes the JSON at 6 AM and 6 PM IST, but GitHub scheduled jobs may start late. The iPhone automation should be scheduled a little after those times (for example, 6:10 AM and 6:10 PM) so the new JSON has time to publish.

## Troubleshooting

- If `news.json` is missing, check the GitHub Actions run logs and ensure Pages is configured for the default branch `/docs`.
- If GitHub Pages is unavailable for your repository plan or visibility, use another public static hosting endpoint; the JSON must be reachable by the iPhone without a sign-in.
- The RSS feeds can fail or change over time. Check the Actions log if a category has no stories.
