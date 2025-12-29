import requests
import logging

logger = logging.getLogger(__name__)

def fetch_articles(base_url: str, min_count: int = 30):
    """
    Fetch articles from Zendesk API with pagination support.

    Args:
        base_url: Zendesk API endpoint URL
        min_count: Minimum number of articles to fetch (default: 30)

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

        # Continue pagination if we haven't reached min_count
        url = data.get("next_page")
        if len(articles) >= min_count:
            break

        page_num += 1

    logger.info(f"Total articles fetched: {len(articles)}")
    return articles
