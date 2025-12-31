## OptiBot Mini Clone

Daily ingestion pipeline for OptiSigns support articles using OpenAI Assistants API with Vector Store (RAG).

---

### Setup

1. **Clone the repository**

   ```bash
   git clone <your-repo-url>
   cd <repo-name>/src
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   - Copy `.env.sample` → `.env`
   - Fill in the required values:
     - `OPENAI_API_KEY`: Your OpenAI API key from platform.openai.com
     - `VECTOR_STORE_ID`: Create a Vector Store in OpenAI and paste the ID
     - `ZENDESK_ARTICLES_URL`: Already set to OptSigns Zendesk API endpoint
     - `S3_BUCKET_NAME`: Your AWS S3 bucket name
     - `S3_ACCESS_KEY`: AWS access key ID
     - `S3_SECRET_KEY`: AWS secret access key
     - `S3_REGION`: AWS region (default: us-east-1)

---

### Run Locally

```bash
python main.py
```

The script will:

1. Fetch 30+ articles from OptSigns Zendesk
2. Convert each to clean Markdown
3. Save markdown files to **local** (`storage/markdown/*.md`) and **S3** (`markdown/*.md`)
4. Load cache from S3 (fallback to local `storage/cache/articles.json`) for change detection
5. Upload only new/updated articles to OpenAI Vector Store
6. Save updated cache to both **local** and **S3**
7. Log results: Added, Updated, Skipped, Total chunks

---

### Docker Usage

Build and run:

```bash
docker build -t optibot-scraper .
docker run \
  -e OPENAI_API_KEY=your_key \
  -e VECTOR_STORE_ID=your_id \
  -e S3_BUCKET_NAME=your_bucket \
  -e S3_ACCESS_KEY=your_access_key \
  -e S3_SECRET_KEY=your_secret_key \
  -e S3_REGION=us-east-1 \
  optibot-scraper
```

The container runs once and exits with code 0 on success.

---

### Chunking Strategy

**Semantic Heading-Based Chunking with Citation Preservation**:

- Each chunk includes **Title + "Article URL:"** at the beginning for proper citations
- Splits at `## ` or `### ` headings for semantic coherence
- Articles without headings are kept as single chunks (up to 800 tokens)
- Large sections are split into 800-token chunks with 100-token overlap
- Separator `---` added between header and content for clarity

**Why this approach?**

- **Citations work**: Every chunk has "Article URL:" so Assistant can cite sources (system prompt requirement)
- **Semantic coherence**: Headings represent logical topics in support docs
- **Context preservation**: Each chunk is self-contained with article identity
- **Better retrieval**: Heading-based splits maintain question/answer structure
- **Flexible**: Handles articles with `##`, `###`, or no headings at all

**Example chunk format**:

```markdown
# Accepted Payment Methods

Article URL: https://support.optisigns.com/hc/en-us/articles/...

---

### How to initiate the Purchase Order process:

[content...]
```

This ensures the system prompt requirement: **"Cite up to 3 'Article URL:' lines per reply"** works correctly.

---

### Daily Job Deployment

Deployed on **DigitalOcean App Platform** as a scheduled job (runs daily at 2 AM UTC).

**Logs & Monitoring**:

- View logs: [DigitalOcean Dashboard](https://cloud.digitalocean.com/apps) → Jobs → optibot-scraper → Logs
- Job shows: articles added/updated/skipped, chunks embedded
- Automated retries on failure

**Cache Persistence & Storage:**

- **Dual Storage (Local + S3):**

  ```
  Local: storage/
  ├── cache/
  │   └── articles.json      # Cache (hashes, timestamps, file_ids)
  └── markdown/
      ├── add-youtube-video.md
      ├── screen-layout.md
      └── ...                # All article markdown files

  S3: bucket-name/
  ├── cache/
  │   └── articles.json      # Same cache synced to S3
  └── markdown/
      ├── add-youtube-video.md
      ├── screen-layout.md
      └── ...                # Same markdown files
  ```

- **Load priority:** S3 first, fallback to local
- **Save behavior:** Both local and S3 simultaneously
- **Delta uploads:** Only new/updated articles are uploaded to Vector Store
- **Old file cleanup:** When articles change, old files are deleted before uploading new ones
- **Efficient:** Unchanged articles are skipped entirely (no upload, no deletion)
- **Backup:** All markdown files preserved locally and in S3

---

### Assistant Configuration

**System Prompt** (set in OpenAI Playground):

```
You are OptiBot, the customer-support bot for OptiSigns.com.
• Tone: helpful, factual, concise.
• Only answer using the uploaded docs.
• Max 5 bullet points; else link to the doc.
• Cite up to 3 "Article URL:" lines per reply.
```

**Test Questions with Screenshots:**

1. **"How to create a video wall with OptiSigns?"**

   - Screenshot: https://drive.google.com/file/d/1EjwxLNy7g8ZP_9yK2JHSHDYWMDOytnPw/view?usp=sharing

2. **"How do I set up background music on my digital signs?"**

   - Screenshot: https://drive.google.com/file/d/1i67iZyISkYJGVIwaM4A4E64LHBtxUvXc/view?usp=sharing

3. **"How can I display PowerBI dashboards on my screens?"**
   - Screenshot: https://drive.google.com/file/d/1Z9Br9FaNQQtAh5MWeI4IzD3woH38oeTV/view?usp=sharing

---

### Project Structure

**Local:**

```
src/
├── main.py                    # Main orchestration pipeline
├── config.py                  # Centralized configuration
├── storage_utils.py           # Dual storage (Local + S3)
├── scraper/
│   ├── zendesk_client.py     # Fetch articles from Zendesk API
│   ├── cleaner.py            # Remove nav/ads from HTML
│   └── markdown.py           # Convert HTML to Markdown
├── vector_store/
│   ├── chunker.py            # Split markdown by headings
│   └── uploader.py           # Upload chunks to OpenAI
├── storage/
│   ├── cache/
│   │   └── articles.json     # Local cache
│   └── markdown/
│       ├── article-1.md
│       └── ...               # Local markdown files
├── Dockerfile
├── requirements.txt
└── .env.sample
```

**AWS S3:**

```
bucket-name/
├── cache/
│   └── articles.json         # S3 cache (synced with local)
└── markdown/
    ├── article-1.md
    ├── article-2.md
    └── ...                   # S3 markdown files (synced with local)
```

│ ├── zendesk_client.py # Fetch articles from Zendesk API
│ ├── cleaner.py # Remove nav/ads from HTML
│ └── markdown.py # Convert HTML to Markdown
├── vector_store/
│ ├── chunker.py # Split markdown by headings
│ └── uploader.py # Upload chunks to OpenAI
├── storage/ # (Empty - all data in S3)
├── Dockerfile
├── requirements.txt
└── .env.sample

```

**AWS S3:**

```

bucket-name/
├── cache/
│ └── articles.json # Cache (hashes, timestamps, file_ids)
└── markdown/
├── add-youtube-video.md
├── screen-layout.md
└── ... # All article markdown files

```

---

### Deployment Steps (DigitalOcean)

1. **Create AWS S3 Bucket**

   - Create bucket in AWS S3
   - Generate IAM credentials with S3 read/write access

2. **Push code to GitHub**

3. **Create DigitalOcean App**

   - Create new App on DigitalOcean Platform
   - Select "Jobs" component type
   - Connect GitHub repo

4. **Configure Environment Variables**

   - `OPENAI_API_KEY`
   - `VECTOR_STORE_ID`
   - `ZENDESK_ARTICLES_URL`
   - `S3_BUCKET_NAME`
   - `S3_ACCESS_KEY`
   - `S3_SECRET_KEY`
   - `S3_REGION`

5. **Set Schedule**

   - Configure cron: `0 2 * * *` (daily at 2 AM UTC)

6. **Deploy**

---
```
