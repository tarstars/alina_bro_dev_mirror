import rss from '@astrojs/rss';
import { getLocalePosts } from '@/lib/content';

export function GET(context: { site: URL | undefined }) {
  const posts = getLocalePosts('en', { includeDeleted: false, includeDraft: false });

  return rss({
    title: 'Channel Mirror (EN)',
    description: 'Physics, mathematics, and programming from your_channel_username channel.',
    site: context.site,
    customData: '<language>en-us</language>',
    items: posts.slice(0, 100).map((post) => ({
      title: post.title,
      description: post.summary,
      pubDate: new Date(post.date),
      link: post.path,
      content: `${post.bodyHtml}<p><a href="${post.source_url}">Original Telegram post</a></p>`
    }))
  });
}
