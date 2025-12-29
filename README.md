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

---

### Run Locally

```bash
python main.py
```

The script will:

1. Fetch 30+ articles from OptSigns Zendesk
2. Convert each to clean Markdown (saved in `storage/data/`)
3. Detect changes using content hashing
4. Upload only new/updated articles to OpenAI Vector Store
5. Log results: Added, Updated, Skipped, Total chunks

---

### Docker Usage

Build and run:

```bash
docker build -t optibot-scraper .
docker run -e OPENAI_API_KEY=your_key -e VECTOR_STORE_ID=your_id optibot-scraper
```

The container runs once and exits with code 0 on success.

---

### Chunking Strategy

**Semantic Heading-Based Chunking**:

- Markdown is split at `## ` (H2 headings) for semantic coherence
- Each section maintains context with its heading
- Large sections are split into 500-token chunks with 50-token overlap
- Optimized for support articles where headings represent logical topics
- Preserves question/answer structure typical in help documentation

**Why this approach?**

- Support articles are naturally structured by topics
- Headings provide semantic boundaries
- Better retrieval accuracy vs. arbitrary length splits
- Maintains context within each chunk

---

### Daily Job Deployment

Deployed on **DigitalOcean App Platform** as a scheduled job (runs daily at 2 AM UTC).

**Logs & Monitoring**:

- View logs: [DigitalOcean Dashboard](https://cloud.digitalocean.com/apps) → Jobs → optibot-scraper → Logs
- Job shows: articles added/updated/skipped, chunks embedded
- Automated retries on failure

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

**Test Question**: "How do I add a YouTube video?"

- Screenshot: [See `screenshots/playground-test.png`]
- Shows correct answer with cited article URLs

---

### Project Structure

```
src/
├── main.py                    # Main orchestration pipeline
├── scraper/
│   ├── zendesk_client.py     # Fetch articles from Zendesk API
│   ├── cleaner.py            # Remove nav/ads from HTML
│   └── markdown.py           # Convert HTML to Markdown
├── vector_store/
│   ├── chunker.py            # Split markdown by headings
│   └── uploader.py           # Upload chunks to OpenAI
├── storage/
│   ├── articles.json         # Cache (hashes, timestamps)
│   └── data/                 # Saved markdown files
├── Dockerfile
├── requirements.txt
└── .env.sample
```

---

### Deployment Steps (DigitalOcean)

1. Push code to GitHub
2. Create new App on DigitalOcean Platform
3. Select "Jobs" component type
4. Connect GitHub repo
5. Set environment variables in Settings
6. Configure schedule: `0 2 * * *` (cron format)
7. Deploy

---

### Sample Output

```
2025-12-29 14:23:01 - INFO - Fetching articles from Zendesk...
2025-12-29 14:23:03 - INFO - Fetched 35 articles
2025-12-29 14:23:04 - INFO - Processing article 1/35: Getting Started with OptiSigns
2025-12-29 14:23:04 - INFO -   Created 4 chunks
2025-12-29 14:23:06 - INFO -   Uploaded 4 chunks to vector store
2025-12-29 14:23:06 - INFO -   Added: Getting Started with OptiSigns
...
============================================================
Summary:
  Added: 5
  Updated: 2
  Skipped: 28
  Total articles processed: 35
  Embedded chunks: 87
============================================================
```
