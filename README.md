# Channel Mirror Template

Bilingual static mirror template for Telegram channels.

This repository contains mirror infrastructure (sync scripts, translation workflow, build/deploy pipelines, and site shell).

## What is included

- `/en/...` and `/ru/...` routes
- daily RU source sync from Telegram API
- EN translation workflow with draft/review statuses and non-destructive updates
- SEO-friendly static pages (robots/sitemap/rss)
- deploy from GitHub Actions to Cloudflare Pages via Wrangler

## Stack

- Astro (static site)
- Python + Telethon (Telegram sync)
- Cloudflare Pages + R2

## Local setup

1. Install dependencies:

```bash
npm install
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Create `.env` from `.env.example` and fill all required variables.

3. Run RU source sync:

```bash
npm run sync:ru
```

4. Prepare EN drafts/review queue:

```bash
npm run translate:en
```

5. Start site:

```bash
npm run dev
```

## Content model

- RU source posts: `content/ru/posts/{id}.md`
- EN translation posts: `content/en/posts/{id}.md`
- Site descriptions:
  - `content/site/en.md`
  - `content/site/ru.md`
- Sync state: `data/state/en_sync_state.json`

EN translation status values:

- `draft`: hidden from EN public pages (redirect to RU source)
- `reviewed`: public/indexable
- `needs_review`: public/indexable after RU source changed
- `locked`: public/indexable, never auto-modified

## GitHub secrets

Configure these repository secrets:

- `CLOUDFLARE_API_TOKEN`
- `CLOUDFLARE_ACCOUNT_ID`
- `CF_PAGES_PROJECT_NAME`
- `R2_ENDPOINT`
- `R2_BUCKET`
- `R2_ACCESS_KEY_ID`
- `R2_SECRET_ACCESS_KEY`
- `R2_PUBLIC_BASE_URL`
- `TELEGRAM_API_ID`
- `TELEGRAM_API_HASH`
- `TELEGRAM_STRING_SESSION`
- `TELEGRAM_CHANNEL`
- `PUBLIC_SITE_URL` (recommended)
- `PUBLIC_CF_ANALYTICS_TOKEN` (optional)

## Daily automation

Workflow `.github/workflows/daily-sync-deploy.yml` runs daily at `18:00 UTC`:

1. sync RU source content incrementally
2. commit content changes to `main` (if any)
3. build Astro site
4. deploy to Cloudflare Pages via Wrangler

## Generating Telegram StringSession

Run once locally with your dedicated Telegram account:

```bash
python3 scripts/generate_string_session.py
```

Copy printed session string into GitHub secret `TELEGRAM_STRING_SESSION`.
