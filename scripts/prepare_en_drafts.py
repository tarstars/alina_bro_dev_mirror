#!/usr/bin/env python3
"""Prepare EN translation drafts from RU source posts without overwriting reviewed content."""

from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path
from typing import Any

import frontmatter

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / 'content' / 'ru' / 'posts'
EN_DIR = ROOT / 'content' / 'en' / 'posts'
QUEUE_PATH = ROOT / 'data' / 'state' / 'en_translation_queue.md'

SYNC_KEYS = [
    'slug',
    'date',
    'edited_at',
    'channel',
    'source_url',
    'summary',
    'album_id',
    'reactions',
    'media',
]


def load_post(path: Path) -> frontmatter.Post:
    return frontmatter.load(path)


def save_post(path: Path, post: frontmatter.Post) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(frontmatter.dumps(post), encoding='utf-8')


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def update_en_metadata(source_meta: dict[str, Any], en_post: frontmatter.Post) -> tuple[bool, bool]:
    """Returns (changed, needs_review_marked)."""
    changed = False
    needs_review_marked = False

    en_meta = en_post.metadata

    for key in SYNC_KEYS:
        if en_meta.get(key) != source_meta.get(key):
            en_meta[key] = source_meta.get(key)
            changed = True

    if en_meta.get('deleted') != source_meta.get('deleted', False):
        en_meta['deleted'] = source_meta.get('deleted', False)
        changed = True

    status = en_meta.get('translation_status', 'draft')
    old_ru_hash = str(en_meta.get('ru_source_hash') or en_meta.get('en_source_hash') or '')
    new_ru_hash = str(source_meta.get('source_hash') or '')

    if old_ru_hash and old_ru_hash != new_ru_hash and status in {'reviewed', 'needs_review'}:
        if status != 'needs_review':
            en_meta['translation_status'] = 'needs_review'
            changed = True
            needs_review_marked = True

    if old_ru_hash != new_ru_hash:
        en_meta['ru_source_hash'] = new_ru_hash
        changed = True

    en_meta['updated_at'] = now_iso()
    return changed, needs_review_marked


def create_en_draft(source_post: frontmatter.Post) -> frontmatter.Post:
    src = source_post.metadata
    draft_content = (
        '> TODO: translate this RU post to EN and mark `translation_status: reviewed` when ready.\n\n'
        + source_post.content.strip()
        + '\n'
    )

    metadata = {
        'id': src['id'],
        'slug': src['slug'],
        'title': f"[DRAFT] {src['title']}",
        'summary': '',
        'date': src['date'],
        'edited_at': src.get('edited_at'),
        'channel': src.get('channel', 'alina_yerevan_js'),
        'source_url': src['source_url'],
        'source_hash': '',
        'deleted': src.get('deleted', False),
        'album_id': src.get('album_id'),
        'reactions': src.get('reactions', []),
        'media': src.get('media', []),
        'translation_status': 'draft',
        'ru_source_hash': src.get('source_hash', ''),
        'updated_at': now_iso(),
    }

    return frontmatter.Post(draft_content, **metadata)


def main() -> None:
    parser = argparse.ArgumentParser(description='Prepare EN translation drafts and review queue.')
    parser.add_argument('--queue-path', default=str(QUEUE_PATH), help='Path to queue markdown output file.')
    args = parser.parse_args()

    EN_DIR.mkdir(parents=True, exist_ok=True)

    created: list[tuple[int, str, str]] = []
    needs_review: list[tuple[int, str, str]] = []
    touched = 0

    source_files = sorted(SOURCE_DIR.glob('*.md'), key=lambda p: int(p.stem))
    for src_path in source_files:
        src_post = load_post(src_path)
        src_meta = src_post.metadata

        post_id = int(src_meta['id'])
        en_path = EN_DIR / f'{post_id}.md'

        if not en_path.exists():
            draft_post = create_en_draft(src_post)
            save_post(en_path, draft_post)
            created.append((post_id, str(src_meta.get('title', f'Post {post_id}')), str(src_meta.get('source_url', ''))))
            touched += 1
            continue

        en_post = load_post(en_path)
        changed, marked = update_en_metadata(src_meta, en_post)
        if marked:
            needs_review.append((post_id, str(src_meta.get('title', f'Post {post_id}')), str(src_meta.get('source_url', ''))))

        if changed:
            save_post(en_path, en_post)
            touched += 1

    queue_path = Path(args.queue_path)
    queue_path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        '# EN Translation Queue',
        '',
        f'Generated: {now_iso()}',
        '',
        f'- New drafts: **{len(created)}**',
        f'- Needs review: **{len(needs_review)}**',
        '',
        '## New Drafts',
        ''
    ]

    if created:
        lines.extend([f'- `{pid}` · {title} · {url}' for pid, title, url in created])
    else:
        lines.append('- None')

    lines.extend(['', '## Needs Review', ''])
    if needs_review:
        lines.extend([f'- `{pid}` · {title} · {url}' for pid, title, url in needs_review])
    else:
        lines.append('- None')

    queue_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')

    print(f'EN draft prep completed. Files touched: {touched}')
    print(f'New drafts: {len(created)} | Needs review: {len(needs_review)}')
    print(f'Queue file: {queue_path.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
