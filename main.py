import os
import json
import hashlib
from dotenv import load_dotenv

from scraper.zendesk_client import fetch_articles
from scraper.cleaner import clean_html
from scraper.markdown import html_to_markdown
from vector_store.chunker import split_by_headings
from vector_store.uploader import upload_chunks

load_dotenv()

ARTICLES_URL = os.getenv("ZENDESK_ARTICLES_URL")
VECTOR_STORE_ID = os.getenv("VECTOR_STORE_ID")

CACHE_FILE = "storage/articles.json"
DATA_DIR = "storage/data"

os.makedirs(DATA_DIR, exist_ok=True)

# Load cache
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r") as f:
        cache = json.load(f)
else:
    cache = {}

added = updated = skipped = total_chunks = 0

articles = fetch_articles(ARTICLES_URL)

for article in articles:
    article_id = str(article["id"])
    title = article["title"]
    body = article["body"]
    url = article["html_url"]

    clean = clean_html(body)
    md_body = html_to_markdown(clean)

    md_full = f"""# {title}

Article URL: {url}

{md_body}
"""

    content_hash = hashlib.md5(md_full.encode()).hexdigest()
    old = cache.get(article_id)

    if old and old["hash"] == content_hash:
        skipped += 1
        continue

    slug = title.lower().replace(" ", "-")
    path = f"{DATA_DIR}/{slug}.md"

    with open(path, "w", encoding="utf-8") as f:
        f.write(md_full)

    chunks = split_by_headings(md_full)
    total_chunks += upload_chunks(chunks, slug, VECTOR_STORE_ID)

    cache[article_id] = {
        "hash": content_hash,
        "updated_at": article["updated_at"]
    }

    if old:
        updated += 1
    else:
        added += 1

with open(CACHE_FILE, "w") as f:
    json.dump(cache, f, indent=2)

print(f"Added: {added}, Updated: {updated}, Skipped: {skipped}")
print(f"Embedded chunks: {total_chunks}")
