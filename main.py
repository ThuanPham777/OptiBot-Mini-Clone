import os
import sys
import json
import hashlib
import logging
from dotenv import load_dotenv

from scraper.zendesk_client import fetch_articles
from scraper.cleaner import clean_html
from scraper.markdown import html_to_markdown
from vector_store.chunker import split_by_headings
from vector_store.uploader import upload_chunks

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

ARTICLES_URL = os.getenv("ZENDESK_ARTICLES_URL")
VECTOR_STORE_ID = os.getenv("VECTOR_STORE_ID")

CACHE_FILE = "storage/articles.json"
DATA_DIR = "storage/data"

def main():
    """Main pipeline for scraping and uploading OptiSigns articles."""
    try:
        # Validate environment variables
        if not ARTICLES_URL:
            logger.error("ZENDESK_ARTICLES_URL not set in .env")
            sys.exit(1)

        if not VECTOR_STORE_ID:
            logger.error("VECTOR_STORE_ID not set in .env")
            sys.exit(1)

        if not os.getenv("OPENAI_API_KEY"):
            logger.error("OPENAI_API_KEY not set in .env")
            sys.exit(1)

        os.makedirs(DATA_DIR, exist_ok=True)

        # Load cache
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, "r") as f:
                cache = json.load(f)
        else:
            cache = {}

        added = updated = skipped = total_chunks = 0

        logger.info("Fetching articles from Zendesk...")
        articles = fetch_articles(ARTICLES_URL)
        logger.info(f"Fetched {len(articles)} articles")

        for idx, article in enumerate(articles, 1):
            article_id = str(article["id"])
            title = article["title"]
            body = article["body"]
            url = article["html_url"]

            logger.info(f"Processing article {idx}/{len(articles)}: {title}")

            # Clean and convert to markdown
            clean = clean_html(body)
            md_body = html_to_markdown(clean)

            md_full = f"""# {title}

Article URL: {url}

{md_body}
"""

            content_hash = hashlib.md5(md_full.encode()).hexdigest()
            old = cache.get(article_id)

            if old and old["hash"] == content_hash:
                logger.info(f"  Skipped (unchanged): {title}")
                skipped += 1
                continue

            # Save markdown file
            slug = title.lower().replace(" ", "-").replace("/", "-")
            path = f"{DATA_DIR}/{slug}.md"

            with open(path, "w", encoding="utf-8") as f:
                f.write(md_full)

            # Chunk and upload to vector store
            chunks = split_by_headings(md_full)
            logger.info(f"  Created {len(chunks)} chunks")

            uploaded = upload_chunks(chunks, slug, VECTOR_STORE_ID)
            total_chunks += uploaded
            logger.info(f"  Uploaded {uploaded} chunks to vector store")

            # Update cache
            cache[article_id] = {
                "hash": content_hash,
                "updated_at": article.get("updated_at", "")
            }

            if old:
                updated += 1
                logger.info(f"  Updated: {title}")
            else:
                added += 1
                logger.info(f"  Added: {title}")

        # Save cache
        with open(CACHE_FILE, "w") as f:
            json.dump(cache, f, indent=2)

        # Final summary
        logger.info("=" * 60)
        logger.info(f"Summary:")
        logger.info(f"  Added: {added}")
        logger.info(f"  Updated: {updated}")
        logger.info(f"  Skipped: {skipped}")
        logger.info(f"  Total articles processed: {len(articles)}")
        logger.info(f"  Embedded chunks: {total_chunks}")
        logger.info("=" * 60)

        sys.exit(0)

    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
