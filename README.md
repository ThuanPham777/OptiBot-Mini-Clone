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

**Note on Cache Persistence:**

- **Local:** Cache persists in `storage/articles.json` - only uploads delta
- **DigitalOcean Jobs:** Stateless containers - cache resets each run
- **Impact:** All articles re-uploaded daily, but old files are deleted first (no duplicates)
- **Production Enhancement:** Use DigitalOcean Spaces or managed database for persistent cache

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
