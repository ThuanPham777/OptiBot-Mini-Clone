import sys
import hashlib
import logging

from config import Config
from scraper.zendesk_client import fetch_articles
from scraper.cleaner import clean_html
from scraper.markdown import html_to_markdown
from vector_store.chunker import split_by_headings
from vector_store.uploader import upload_chunks
from storage_utils import CacheStorage

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main pipeline for scraping and uploading OptiSigns articles."""
    try:
        Config.validate()

        cache_storage = CacheStorage()
        cache = cache_storage.load()

        added = updated = skipped = total_chunks = 0

        logger.info("Fetching articles from Zendesk...")
        articles = fetch_articles(Config.ZENDESK_ARTICLES_URL, fetch_all=False)
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

            slug = title.lower().replace(" ", "-").replace("/", "-")
            for char in '<>:"|?*':
                slug = slug.replace(char, "")

            # Save markdown to S3
            cache_storage.save_markdown(f"{slug}.md", md_full)

            chunks = split_by_headings(md_full)
            logger.info(f"  Created {len(chunks)} chunks")

            old_file_ids = old.get("file_ids", []) if old else None
            uploaded, new_file_ids = upload_chunks(chunks, slug, Config.VECTOR_STORE_ID, old_file_ids)
            total_chunks += uploaded
            logger.info(f"  Uploaded {uploaded} chunks to vector store")

            # Update cache
            cache[article_id] = {
                "hash": content_hash,
                "updated_at": article.get("updated_at", ""),
                "file_ids": new_file_ids
            }

            if old:
                updated += 1
                logger.info(f"  Updated: {title}")
            else:
                added += 1
                logger.info(f"  Added: {title}")

        cache_storage.save(cache)

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
