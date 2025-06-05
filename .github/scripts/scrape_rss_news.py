import feedparser
from datetime import datetime
import pytz

# Timezone
BST = pytz.timezone('Europe/London')

# Google News RSS feed for "Stability AI" and "Getty Images"
feed_url = 'https://news.google.com/rss/search?q="Stability+AI"+"Getty+Images"&hl=en&gl=US&ceid=US:en'

def is_today_bst(pub_date):
    if not pub_date:
        return False
    try:
        dt_utc = datetime(*pub_date[:6], tzinfo=pytz.utc)
    except Exception:
        return False
    dt_bst = dt_utc.astimezone(BST)
    now_bst = datetime.now(BST)
    return dt_bst.date() == now_bst.date()

def fetch_articles():
    articles = []
    feed = feedparser.parse(feed_url)
    for entry in feed.entries:
        if hasattr(entry, 'published_parsed') and is_today_bst(entry.published_parsed):
            content = ' '.join([
                entry.get('title', ''),
                entry.get('summary', ''),
                entry.get('description', '')
            ]).lower()

            # Optional: Extra filtering if needed
            if "stability ai" in content and "getty images" in content:
                articles.append({
                    'title': entry.title,
                    'link': entry.link,
                    'published': datetime(*entry.published_parsed[:6], tzinfo=pytz.utc).astimezone(BST).strftime('%Y-%m-%d %H:%M:%S %Z'),
                    'summary': entry.get('summary', '')[:200] + '...' if entry.get('summary') else '',
                    'source': entry.get('source', {}).get('title', 'Unknown')
                })
    return articles

def generate_readme(articles):
    readme_content = "# Stability AI vs Getty Images: Today's News\n\n"
    if articles:
        readme_content += "| Date (BST) | Source | Title | Summary |\n"
        readme_content += "|------------|--------|-------|---------|\n"
        for article in articles:
            readme_content += f"| {article['published']} | {article['source']} | [{article['title']}]({article['link']}) | {article['summary']} |\n"
    else:
        readme_content += "No articles found today.\n"
    return readme_content

def main():
    articles = fetch_articles()
    readme = generate_readme(articles)
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(readme)
    print(f"README.md updated with {len(articles)} articles.")

if __name__ == '__main__':
    main()
