export function GET() {
  const site = (import.meta.env.PUBLIC_SITE_URL || 'https://example.com').replace(/\/$/, '');
  const body = `User-agent: *
Allow: /

Host: ${site}
Sitemap: ${site}/sitemap.xml
`;

  return new Response(body, {
    headers: {
      'Content-Type': 'text/plain; charset=utf-8'
    }
  });
}
