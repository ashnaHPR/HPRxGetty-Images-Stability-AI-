import feedparser
from datetime import datetime, timezone
import pytz

BST = pytz.timezone('Europe/London')

topics = { 
    # ... (your full feed list)
}

spokespersons = ['tim erridge', 'scott mckinnon', 'carla baker', 'anna chung', 'sam rubin']

def is_today_bst(pub_date):
    if not pub_date:
        print("No published date found.")
        return False
    try:
        dt_utc = datetime(*pub_date[:6], tzinfo=timezone.utc)
    except Exception as e:
        print(f"Error parsing date: {e}")
        return False
    dt_bst = dt_utc.astimezone(BST)
    now_bst = datetime.now(BST)
    print(f"Article date BST: {dt_bst.date()}, Today BST: {now_bst.date()}")
    return dt_bst.date() == now_bst.date()

def contains_spokesperson(text):
    if not text:
        return False
    text_lower = text.lower()
    return any(name in text_lower for name in spokespersons)

articles = []

for publication, feed_url in topics.items():
    print(f"Checking feed: {publication}")
    d = feedparser.parse(feed_url)
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
            if publication.startswith('Palo Alto Networks') or contains_spokesperson(full_content):
                articles.append({
                    'publication': publication,
                    'title': entry.title,
                    'link': entry.link,
                    'published': datetime(*entry.published_parsed[:6], tzinfo=timezone.utc).astimezone(BST).strftime('%Y-%m-%d %H:%M:%S %Z'),
                    'summary': entry.get('summary', '')[:200] + '...' if entry.get('summary') else '',
                })

print(f"Total articles found: {len(articles)}")

# Prepare README content as before
readme_content = "# Today's News Articles\n\n"
if articles:
    readme_content += "| Date (BST) | Publication | Title | Summary |\n"
    readme_content += "|------------|-------------|-------|---------|\n"
    for art in articles:
        readme_content += f"| {art['published']} | {art['publication']} | [{art['title']}]({art['link']}) | {art['summary']} |\n"
else:
    readme_content += "No articles found for today.\n"

with open('README.md', 'w', encoding='utf-8') as f:
    f.write(readme_content)

print(f"README.md updated with {len(articles)} articles.")
