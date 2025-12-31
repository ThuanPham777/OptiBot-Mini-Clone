import requests
import logging

logger = logging.getLogger(__name__)

def fetch_articles(base_url: str, fetch_all: bool = False):
    """
    Fetch articles from Zendesk API with pagination support.

    Args:
        base_url: Zendesk API endpoint URL
        fetch_all: If True, fetches ALL articles. If False, fetches minimum 30 (default: False)

    Returns:
        List of article dictionaries
    """
    articles = []
    url = base_url
    page_num = 1

    while url:
        logger.info(f"Fetching page {page_num} from Zendesk API...")
        res = requests.get(url, timeout=30)
        res.raise_for_status()
        data = res.json()

        page_articles = data.get("articles", [])
        articles.extend(page_articles)
        logger.info(f"  Retrieved {len(page_articles)} articles (total: {len(articles)})")

        url = data.get("next_page")

        if not fetch_all and len(articles) >= 30:
            break

        page_num += 1

    logger.info(f"Total articles fetched: {len(articles)}")
    return articles
