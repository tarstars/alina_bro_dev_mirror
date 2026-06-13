# alina_yerevan_js — channel mirror

Bilingual static mirror of the Telegram channel **alina_yerevan_js**, deployed to
**alina-bro.dev** (Astro + Python/Telethon + Cloudflare Pages). **RU is the source**,
EN is a translation. Posts: `content/ru/posts/*.md` (source) and `content/en/posts/*.md`.
A post's short preview is frontmatter `summary`; the long body is the markdown.
(Gotcha: never add `summary` to `SYNC_KEYS` in `scripts/prepare_en_drafts.py` — it
overwrites translated EN summaries with the RU source on every sync.)

## Creating a navigational post

A *navigational post* is a curated index that helps readers follow one thread of
related posts (see existing examples: **#343 "Навигация Раздан"**, **#360 "Севан.
Навигация…"**, and the meta glossary **#20 "Словарь хэштегов"**).

When asked **"create a navigational post for the channel"**, do this — the important
part is choosing *which* group of posts needs one most right now:

1. **Scan topics.** Tally hashtags across `content/ru/posts/*.md` and count the number
   of *distinct* posts per theme.
2. **Check existing coverage.** Find posts that are already navigational: title contains
   `Навигация`, or the body has ≥3 internal links of the form
   `t.me/alina_yerevan_js/<id>`. Note which themes they already cover.
3. **Pick the target = the largest *coherent* theme with no nav post yet.** Skip
   over-broad umbrellas that aren't a single topic (e.g. all of "Ереван", ~50 posts,
   is too heterogeneous — split it instead), skip themes already covered, and prefer
   what is timely now (tourist season → a place/travel thread). This gap is where a
   nav post adds the most.
4. **Draft it in the channel's RU voice** (model on #343 / #360): open with
   `Всем барев!`, one line noting the topic has accumulated posts, then `👇👇👇`;
   list the posts grouped into a few sub-rubrics, each line an emoji + short label +
   link `<https://t.me/alina_yerevan_js/<id>>`; end with the theme's hashtags.
   Optionally also add web links `https://alina-bro.dev/ru/post/<id>-<slug>/`
   (read `id`/`slug` from each post's frontmatter).
5. **Output the markdown** for the user to post to the Telegram channel. Do **not**
   commit it as a content file — once posted, the daily sync imports it automatically,
   then it gets translated to EN like any other post.

## Posting a navigational post (with a collage) to Telegram

The post is authored in Telegram; the repo only mirrors it after the daily sync. To
publish the drafted text together with a collage image as **one message**:

- **Photo + caption in one message.** A photo caption is capped at **1024 UTF-16 units**
  (2048 with Telegram Premium), and only the visible link *labels* count, not the URLs.
  If the text is longer, send the photo with a short caption and the full text as a
  separate follow-up message.
- **Formatting.** Use Telethon markdown (`parse_mode="md"`): links are `[label](url)`
  with a **plain** URL — strip the `<…>` the repo stores — and no MarkdownV2 punctuation
  escaping is needed. (`HTML` parse mode is the other easy option.)
- **Credentials** (the same ones the daily sync uses; GitHub secrets are write-only, so
  re-fetch them rather than read them back):
  - `TELEGRAM_API_ID` + `TELEGRAM_API_HASH` — https://my.telegram.org → *API development
    tools* (shows your existing app's values).
  - `TELEGRAM_STRING_SESSION` — mint one with
    `uv run --with telethon --with qrcode python scripts/generate_string_session.py --qr`
    (scan via Telegram → Settings → Devices → Link Desktop Device).
  - `TELEGRAM_CHANNEL` — `alina_yerevan_js` (not secret).
- **Send it** (run in a normal terminal — sandboxes may cap outbound connections at ~30s):
  ```
  export TELEGRAM_API_ID=… TELEGRAM_API_HASH=… TELEGRAM_STRING_SESSION=… TELEGRAM_CHANNEL=alina_yerevan_js
  uv run --with telethon python scripts/post_telegram.py navpost.md collage.jpg
  ```
  `scripts/post_telegram.py` strips the `<>`, checks the caption limit, and sends the
  photo + markdown caption (or a plain message if no image is given). It posts as your
  user account, which is fine since you own the channel.
