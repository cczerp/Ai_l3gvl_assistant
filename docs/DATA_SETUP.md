# Legal Data Setup Guide

Complete guide for setting up and populating your legal AI database with state laws, federal laws, and case law.

## Table of Contents

- [Overview](#overview)
- [Database Setup (Supabase)](#database-setup-supabase)
- [Scraping State Laws](#scraping-state-laws)
- [Data Sources](#data-sources)
- [Architecture](#architecture)
- [Troubleshooting](#troubleshooting)

## Overview

This project uses **Supabase** (PostgreSQL + pgvector) for:
- Structured storage of legal documents
- Vector embeddings for semantic search
- Full-text search capabilities
- Scalable cloud infrastructure

### What Data Can You Get?

- ✅ **State Laws**: All 50 US states via Justia (free)
- ✅ **Federal Laws**: USC, CFR (requires additional scraper)
- ✅ **Case Law**: Court opinions from 1974-2024 (via CourtListener API)
- ✅ **Legal Dictionary**: Terms and definitions

## Database Setup (Supabase)

### Step 1: Create Supabase Project

1. Go to [supabase.com](https://supabase.com) and sign up
2. Create a new project
3. Choose a region close to you
4. Set a strong database password
5. Wait for project to finish provisioning (~2 minutes)

### Step 2: Run Database Schema

1. In your Supabase dashboard, go to **SQL Editor**
2. Copy the entire contents of `scripts/supabase_schema.sql`
3. Paste into the SQL editor
4. Click **Run** (or press Cmd/Ctrl + Enter)
5. You should see: "✅ Legal AI Database Schema Created Successfully!"

This creates:
- `state_laws` table (for state statutes)
- `federal_laws` table (for federal statutes)
- `cases` table (for case law)
- `legal_terms` table (for legal dictionary)
- `precedent_relationships` table (for citation graph)
- Vector indexes for semantic search
- Full-text search indexes
- Helper functions and views

### Step 3: Get API Credentials

1. In Supabase dashboard, go to **Settings** → **API**
2. Copy your **Project URL** (e.g., `https://xxxxx.supabase.co`)
3. Copy your **anon/public key** (starts with `eyJ...`)

### Step 4: Configure Environment

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your Supabase credentials:
   ```bash
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

   # Also add OpenAI key for embeddings (later)
   OPENAI_API_KEY=sk-...
   ```

### Step 5: Install Dependencies

```bash
pip install -r requirements.txt
```

## Scraping State Laws

### Quick Test (Recommended First)

Scrape just a few statutes from California to test everything works:

```bash
python scripts/scrape_to_supabase.py --state CA --test
```

This will:
- Scrape ~5 sample statutes from California
- Upload them to your Supabase database
- Show you a preview of the data

### Scrape a Single State

Scrape all statutes from one state:

```bash
python scripts/scrape_to_supabase.py --state CA
```

**Note**: This can take 30-60 minutes per state depending on how many statutes they have.

### Scrape Multiple States

```bash
python scripts/scrape_to_supabase.py --states CA,NY,TX,FL
```

### Scrape All 50 States

```bash
python scripts/scrape_to_supabase.py --states $(echo {AL,AK,AZ,AR,CA,CO,CT,DE,FL,GA,HI,ID,IL,IN,IA,KS,KY,LA,ME,MD,MA,MI,MN,MS,MO,MT,NE,NV,NH,NJ,NM,NY,NC,ND,OH,OK,OR,PA,RI,SC,SD,TN,TX,UT,VT,VA,WA,WV,WI,WY,DC} | tr ' ' ',')
```

**Warning**: This will take **many hours** and make thousands of requests. Run it overnight.

### Scraper Options

```bash
# Skip statutes that already exist in database
python scripts/scrape_to_supabase.py --state CA --skip-existing

# Adjust rate limiting (seconds between requests)
python scripts/scrape_to_supabase.py --state CA --rate-limit 2.0

# Use caching (faster for re-runs)
python scripts/scrape_to_supabase.py --state CA --cache-dir /tmp/scraper_cache

# Adjust upload batch size
python scripts/scrape_to_supabase.py --state CA --batch-size 100

# Verbose logging
python scripts/scrape_to_supabase.py --state CA -v
```

### Scrape to JSON (Without Uploading)

If you want to scrape to files first, then upload later:

```bash
# Scrape to JSON file
python scripts/scrape_laws.py --state CA --output data/scraped/california.json --pretty

# Later, upload from JSON (you'll need to write this script)
# python scripts/upload_from_json.py --input data/scraped/california.json
```

## Data Sources

### State Laws

**Primary Source: Justia.com**
- URL: https://law.justia.com/codes/
- Coverage: All 50 US states
- Cost: Free
- Format: HTML
- Update frequency: Varies by state
- Our scraper: `JustiaScraper`

**Alternative Sources** (not yet implemented):
- State legislature websites (official, but 50 different formats)
- Legal Information Institute (https://www.law.cornell.edu/)
- Casetext API (paid)

### Federal Laws

**Sources to Implement**:
- **US Code**: https://uscode.house.gov/
- **Code of Federal Regulations**: https://www.ecfr.gov/
- **FDsys/GovInfo API**: https://api.govinfo.gov/

### Case Law

**Recommended Source: CourtListener**
- URL: https://www.courtlistener.com/
- API: https://www.courtlistener.com/api/rest/v3/
- Coverage: Millions of opinions, 1754-present
- Cost: Free (with rate limits)
- Bulk data: Available for download

**To implement**:
```python
# Create src/scrapers/courtlistener_scraper.py
# Use their REST API to fetch cases
# Filter by jurisdiction, date range, etc.
```

### Legal Dictionary

**Sources**:
- Black's Law Dictionary (paid/copyrighted)
- Wex Legal Dictionary (Cornell, free): https://www.law.cornell.edu/wex
- Justia Legal Dictionary: https://www.justia.com/legal-dictionary/

## Architecture

### Data Flow

```
┌─────────────────┐
│   Justia.com    │  (Source)
└────────┬────────┘
         │
         │ HTTP requests (rate-limited)
         ▼
┌─────────────────┐
│  JustiaScraper  │  (src/scrapers/justia_scraper.py)
│  - Fetch HTML   │
│  - Parse data   │
│  - Validate     │
└────────┬────────┘
         │
         │ ScrapedStatute objects
         ▼
┌─────────────────┐
│ Supabase Client │  (src/database/supabase_client.py)
│  - Batch insert │
│  - Dedup check  │
└────────┬────────┘
         │
         │ SQL inserts
         ▼
┌─────────────────┐
│    Supabase     │  (PostgreSQL + pgvector)
│  PostgreSQL DB  │
│  - state_laws   │
│  - federal_laws │
│  - cases        │
│  - legal_terms  │
└─────────────────┘
```

### Scraper Architecture

**Base Class**: `BaseScraper` (`src/scrapers/base_scraper.py`)
- Async HTTP client (httpx)
- Rate limiting
- Retry logic (with exponential backoff)
- Caching support
- Text cleaning and validation

**Justia Scraper**: `JustiaScraper` (`src/scrapers/justia_scraper.py`)
- Scrapes state codes from Justia
- Handles different state formats
- Extracts statute metadata
- Parses statute text

**Factory**: `StateCodesScraperFactory` (`src/scrapers/state_codes_scraper.py`)
- Returns best scraper for each state
- Allows state-specific scrapers (e.g., for official sources)

### Database Schema Highlights

**Vector Embeddings** (for semantic search):
```sql
embedding VECTOR(1536)  -- OpenAI ada-002 dimension
```

**Full-Text Search**:
```sql
CREATE INDEX idx_state_laws_full_text
ON state_laws USING GIN(to_tsvector('english', full_text));
```

**Deduplication**:
```sql
CREATE UNIQUE INDEX idx_state_laws_unique
ON state_laws(state, statute_number);
```

## Next Steps After Data Collection

### 1. Generate Embeddings

After scraping, you'll want to generate vector embeddings for semantic search:

```python
# scripts/generate_embeddings.py (TODO)
# - Fetch all statutes without embeddings
# - Call OpenAI Embeddings API
# - Update embedding column
```

### 2. Build RAG Pipeline

Connect your data to the RAG system:
- Configure vector store (pgvector via Supabase)
- Set up retrieval chain
- Test semantic search

### 3. Ingest Case Law

Scrape and ingest case opinions:
- Use CourtListener API
- Parse opinions and metadata
- Build citation graph

### 4. Add Federal Laws

Implement federal law scrapers:
- US Code scraper
- CFR scraper
- Store in `federal_laws` table

## Troubleshooting

### "Failed to connect to Supabase"

- Check your `.env` file has `SUPABASE_URL` and `SUPABASE_KEY`
- Verify the URL starts with `https://`
- Verify the key is the **anon public key**, not service role key (unless you want full access)

### "Too many requests" / Rate limiting

Justia may rate limit if you scrape too aggressively:
```bash
# Increase delay between requests
python scripts/scrape_to_supabase.py --state CA --rate-limit 2.0
```

### Scraper returns no statutes

- Check the Justia website is accessible: https://law.justia.com/codes/california/
- Justia may have changed their HTML structure (you'll need to update the parser)
- Try with `--verbose` flag to see detailed logs

### Database errors

- Make sure you ran the schema script (`supabase_schema.sql`)
- Check the Supabase dashboard → Table Editor to verify tables exist
- Check logs in Supabase dashboard → Logs → Postgres Logs

### Import errors

```bash
# Make sure all dependencies are installed
pip install -r requirements.txt

# If you get module not found errors, check your Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

## Performance Tips

### Use Caching

Cache scraped pages to avoid re-downloading during testing:
```bash
python scripts/scrape_laws.py --state CA --cache-dir /tmp/scraper_cache
```

### Adjust Batch Size

Larger batches = fewer database round-trips:
```bash
python scripts/scrape_to_supabase.py --state CA --batch-size 100
```

### Run in Background

For long-running scrapes:
```bash
nohup python scripts/scrape_to_supabase.py --states CA,NY,TX > scrape.log 2>&1 &

# Check progress
tail -f scrape.log
```

### Use Screen/Tmux

For multi-hour scraping sessions:
```bash
# Start screen session
screen -S legal-scraper

# Run scraper
python scripts/scrape_to_supabase.py --all

# Detach: Ctrl+A, then D
# Reattach: screen -r legal-scraper
```

## Cost Estimates

### Free Tier Limits

**Supabase Free Tier**:
- 500 MB database storage
- 1 GB file storage
- 2 GB bandwidth/month
- Unlimited API requests

**Estimated Storage**:
- Average statute: ~2-5 KB text
- California: ~30,000 statutes = ~100 MB
- All 50 states: ~500 MB - **fits in free tier!**
- With embeddings: ~2 GB - **need paid tier ($25/mo)**

**OpenAI Embeddings** (for semantic search):
- ada-002: $0.0001 per 1K tokens
- Average statute: ~500 tokens
- 1 million statutes: ~$50

### Recommended Plan

**Start**: Supabase free tier (no credit card needed)
**Scale**: Upgrade to Pro ($25/mo) when you add embeddings

## Legal & Ethical Considerations

### Terms of Service

- **Justia**: Allows reasonable scraping for educational/research purposes
- **CourtListener**: Explicitly allows API access and bulk downloads
- **State Legislature Sites**: Check each state's ToS

### Best Practices

1. **Rate limit respectfully** (1-2 seconds between requests)
2. **Identify your bot** (use descriptive User-Agent)
3. **Cache aggressively** (don't re-download unnecessarily)
4. **Respect robots.txt** (our scraper does this by default)
5. **Don't resell data** (use for your own research/education)

### Attribution

If you build a public-facing app:
- Credit data sources (Justia, CourtListener, etc.)
- Include disclaimers that you're not a law firm
- Don't provide legal advice

## Support

For issues with the scraper:
1. Check this documentation
2. Look at the code in `src/scrapers/`
3. Open an issue on GitHub

For Supabase issues:
- Supabase docs: https://supabase.com/docs
- Supabase community: https://github.com/supabase/supabase/discussions

---

**Ready to start?** Run the test command:
```bash
python scripts/scrape_to_supabase.py --state CA --test
```
