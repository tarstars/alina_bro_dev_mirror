import rss from '@astrojs/rss';
import { getLocalePosts } from '@/lib/content';

export function GET(context: { site: URL | undefined }) {
  const posts = getLocalePosts('ru', { includeDeleted: false, includeDraft: false });

  return rss({
    title: 'Channel Mirror (RU)',
    description: 'Лента зеркала постов канала @alina_yerevan_js.',
    site: context.site,
    customData: '<language>ru-ru</language>',
    items: posts.slice(0, 100).map((post) => ({
      title: post.title,
      description: post.summary,
      pubDate: new Date(post.date),
      link: post.path,
      content: `${post.bodyHtml}<p><a href="${post.source_url}">Оригинал в Telegram</a></p>`
    }))
  });
}
