import requests

def fetch_articles(base_url: str, min_count: int = 30):
    articles = []
    url = base_url

    while url and len(articles) < min_count:
        res = requests.get(url, timeout=30)
        res.raise_for_status()
        data = res.json()

        articles.extend(data.get("articles", []))
        url = data.get("next_page")

    return articles[:min_count]
