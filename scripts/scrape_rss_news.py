import feedparser
from datetime import datetime, timezone
import pytz

BST = pytz.timezone('Europe/London')

# Only Google News RSS for Getty Images + Stability AI mentions
google_news_feed = 'https://news.google.com/rss/search?q="Getty+Images"+"Stability+AI"&hl=en-GB&gl=GB&ceid=GB:en'

def is_today_bst(pub_date):
    if not pub_date:
        return False
    try:
        dt_utc = datetime(*pub_date[:6], tzinfo=timezone.utc)
    except Exception:
        return False
    dt_bst = dt_utc.astimezone(BST)
    now_bst = datetime.now(BST)
    return dt_bst.date() == now_bst.date()

def contains_keywords(text):
    if not text:
        return False
    text_lower = text.lower()
    return 'getty images' in text_lower and 'stability ai' in text_lower

articles = []

d = feedparser.parse(google_news_feed)
for entry in d.entries:
    if hasattr(entry, 'published_parsed') and is_today_bst(entry.published_parsed):
        content_parts = []
        if hasattr(entry, 'title'):
            content_parts.append(entry.title)
        if hasattr(entry, 'summary'):
            content_parts.append(entry.summary)
        if hasattr(entry, 'description'):
            content_parts.append(entry.description)
        if hasattr(entry, 'content'):
            content_parts.extend([c.value for c in entry.content if hasattr(c, 'value')])
        full_content = ' '.join(content_parts).lower()
        if contains_keywords(full_content):
            articles.append({
                'publication': 'Google News',
                'title': entry.title,
                'link': entry.link,
                'published': datetime(*entry.published_parsed[:6], tzinfo=timezone.utc).astimezone(BST).strftime('%Y-%m-%d %H:%M:%S %Z'),
                'summary': entry.get('summary', '')[:200] + '...' if entry.get('summary') else '',
            })

readme_content = "# Today's Getty Images & Stability AI News\n\n"

if articles:
    readme_content += "| Date (BST) | Publication | Title | Summary |\n"
    readme_content += "|------------|-------------|-------|---------|\n"
    for art in articles:
        readme_content += f"| {art['published']} | {art['publication']} | [{art['title']}]({art['link']}) | {art['summary']} |\n"
else:
    readme_content += "No articles found mentioning Getty Images and Stability AI for today.\n"

with open('README.md', 'w', encoding='utf-8') as f:
    f.write(readme_content)

print(f"README.md updated with {len(articles)} articles.")
