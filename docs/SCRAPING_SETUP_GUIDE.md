# Legal Data Scraping System - Setup Guide

This guide will help you set up and use the comprehensive legal data scraping system.

## Table of Contents
1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Usage](#usage)
6. [Data Sources](#data-sources)
7. [Database Setup](#database-setup)
8. [Troubleshooting](#troubleshooting)

---

## Overview

This system collects comprehensive legal data from multiple authoritative sources:

- ✅ **US Constitution & Bill of Rights** - All articles and 27 amendments
- ✅ **Legal Dictionaries** - 3 sources (Wex, Black's Law Dictionary, FindLaw)
- ✅ **Supreme Court Cases** - Past 50 years (1974-2024)
- ✅ **State Laws** - All 50 states' statutes and codes
- ✅ **State Court Cases** - All 50 states' supreme and appellate courts
- 🚧 **Federal Laws** - U.S. Code (USC) and CFR

### Data Volume Estimates

| Data Type | Count | Size |
|-----------|-------|------|
| Constitutional Documents | ~50 | <1 MB |
| Legal Dictionary Terms | 10,000-15,000 | 5-10 MB |
| Supreme Court Cases (50 years) | ~5,000 | 500 MB - 1 GB |
| State Laws (all 50 states) | 500K-2M | 5-20 GB |
| State Court Cases | 10M+ | 100+ GB |
| **TOTAL** | **10M+ records** | **100-150 GB** |

---

## Prerequisites

### 1. System Requirements

- **Python:** 3.9 or higher
- **RAM:** Minimum 8GB (16GB recommended for large datasets)
- **Disk Space:** 200GB+ free space
- **Internet:** Stable broadband connection

### 2. API Keys

#### CourtListener API Key (Required for case law)
1. Go to https://www.courtlistener.com/sign-in/register/
2. Create a free account
3. Navigate to your account settings
4. Generate an API key
5. Save the key for configuration

**Rate Limits:**
- Without API key: ~100 requests/day
- With free API key: ~5,000-10,000 requests/day
- Consider supporting Free Law Project if scraping heavily

---

## Installation

### 1. Clone the Repository

```bash
cd Ai_l3gvl_assistant
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

If `requirements.txt` doesn't include these, install manually:

```bash
pip install httpx beautifulsoup4 lxml tenacity tqdm pydantic asyncio
```

### 3. Verify Installation

```bash
python -c "import httpx, bs4, lxml; print('✓ All dependencies installed')"
```

---

## Configuration

### 1. Environment Variables

Create a `.env` file in the project root:

```bash
# CourtListener API Key (for Supreme Court and state court cases)
COURTLISTENER_API_KEY=your_api_key_here

# Database Configuration (for later upload)
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# Data Directory
DATA_DIR=./data
```

### 2. Directory Structure

The system will create these directories automatically:

```
data/
├── constitutional_documents/   # US Constitution & amendments
├── legal_dictionaries/         # Legal terms from 3 sources
├── cases/
│   ├── supreme_court/          # SCOTUS cases
│   └── state_courts/           # State court cases by state
├── state_laws/                 # State statutes by state
├── federal_laws/               # U.S. Code sections
└── reports/                    # Scraping reports and logs
```

---

## Usage

### Quick Start

#### 1. Test Run (Recommended First)

Test with a small dataset to ensure everything works:

```bash
python scripts/scrape_all_legal_data.py --constitution --test-mode
```

#### 2. Collect Specific Data

**US Constitution & Bill of Rights:**
```bash
python scripts/scrape_all_legal_data.py --constitution
```

**Legal Dictionaries (all 3 sources):**
```bash
python scripts/scrape_all_legal_data.py --dictionaries
```

**Supreme Court Cases (past 50 years):**
```bash
python scripts/scrape_all_legal_data.py --supreme-court
```

**State Laws (specific states):**
```bash
python scripts/scrape_all_legal_data.py --state-laws --states CA,NY,TX
```

**State Court Cases (specific states):**
```bash
python scripts/scrape_all_legal_data.py --state-courts --states CA,NY --max-cases 100
```

#### 3. Collect Everything

**WARNING:** This will take days/weeks and use 100+ GB of storage

```bash
python scripts/scrape_all_legal_data.py --all
```

### Advanced Options

```bash
python scripts/scrape_all_legal_data.py \
  --supreme-court \
  --scotus-years 10 \          # Last 10 years instead of 50
  --max-cases 1000 \           # Limit to 1000 cases
  --api-key YOUR_KEY \         # Override env var
  --data-dir ./my_data         # Custom data directory
```

### Incremental Collection Strategy

For massive datasets, collect incrementally:

```bash
# Day 1: Constitution and dictionaries (quick)
python scripts/scrape_all_legal_data.py --constitution --dictionaries

# Day 2: Supreme Court cases
python scripts/scrape_all_legal_data.py --supreme-court

# Day 3-7: State laws (5 states per day)
python scripts/scrape_all_legal_data.py --state-laws --states CA,NY,TX,FL,IL

# Weeks 2-4: State court cases (incremental by state)
python scripts/scrape_all_legal_data.py --state-courts --states CA --max-cases 10000
python scripts/scrape_all_legal_data.py --state-courts --states NY --max-cases 10000
# ... continue for each state
```

---

## Data Sources

### Source Details

| Source | Type | URL | Auth | Rate Limit |
|--------|------|-----|------|------------|
| National Archives | Constitution | archives.gov | None | Reasonable use |
| Cornell Wex | Dictionary | law.cornell.edu/wex | None | 1 req/sec |
| TheLawDictionary | Dictionary | thelawdictionary.org | None | 1 req/sec |
| CourtListener | Cases | courtlistener.com | API Key | With key: high |
| Justia | State Laws | law.justia.com | None | 1 req/sec |

### Data Quality Notes

1. **National Archives** - Authoritative official source
2. **CourtListener** - Excellent quality, includes SCDB metadata
3. **Legal Dictionaries** - Wex is most comprehensive
4. **State Laws** - Justia is reliable but consider validating against official state sources for critical use

---

## Database Setup

### 1. Create Database

If using Supabase:

1. Go to https://supabase.com
2. Create a new project
3. Navigate to SQL Editor
4. Run the schema:

```bash
cat scripts/supabase_schema.sql
```

Copy and paste into Supabase SQL Editor and execute.

### 2. Verify Schema

Check that all tables were created:

```sql
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public';
```

Expected tables:
- `constitutional_documents`
- `state_laws`
- `federal_laws`
- `cases`
- `legal_terms`
- `precedent_relationships`
- `us_states`

### 3. Upload Scraped Data

After scraping, use the ingestion pipeline:

```bash
# Upload constitutional documents
python scripts/upload_to_supabase.py --type constitution --file data/constitutional_documents/us_constitution.json

# Upload legal terms
python scripts/upload_to_supabase.py --type dictionary --file data/legal_dictionaries/wex_dictionary.json

# Upload cases
python scripts/upload_to_supabase.py --type cases --file data/cases/supreme_court/scotus_cases_50years.json
```

---

## Individual Scraper Testing

### Constitution Scraper

```bash
python src/scrapers/constitution_scraper.py
```

Expected output:
- ~50 constitutional documents
- Preamble, 7 articles, 27 amendments

### Wex Dictionary Scraper

```bash
python src/scrapers/wex_dictionary_scraper.py
```

Test with 10 terms first:
```python
# Edit main() in wex_dictionary_scraper.py
terms = await scraper.scrape_all(max_terms=10)
```

### Supreme Court Scraper

```bash
# Set your API key first
export COURTLISTENER_API_KEY=your_key_here

python src/scrapers/courtlistener_scotus_scraper.py
```

### State Laws Scraper

```bash
# Test with California
python scripts/scrape_laws.py --state CA --test
```

---

## Troubleshooting

### Common Issues

#### 1. Rate Limiting

**Error:** `429 Too Many Requests`

**Solution:**
- Get CourtListener API key
- Increase `rate_limit_delay` in scraper config
- Use `--test-mode` for testing

#### 2. Timeout Errors

**Error:** `ReadTimeout` or `ConnectTimeout`

**Solution:**
- Increase timeout in scraper config
- Check internet connection
- Try again during off-peak hours

#### 3. Memory Issues

**Error:** `MemoryError` or system slowdown

**Solution:**
- Process data in smaller batches
- Use `--max-cases` or `--max-terms` limits
- Close other applications
- Upgrade RAM if persistently failing

#### 4. Disk Space

**Error:** `No space left on device`

**Solution:**
- Check available space: `df -h`
- Clean up old scraping attempts
- Use external drive for data storage
- Use `--data-dir` to specify alternate location

#### 5. Import Errors

**Error:** `ModuleNotFoundError`

**Solution:**
```bash
pip install httpx beautifulsoup4 lxml tenacity tqdm
```

### Debugging

Enable verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Or add to scraper:

```bash
python scripts/scrape_all_legal_data.py --verbose --supreme-court
```

---

## Best Practices

### 1. Ethical Scraping

- ✅ Respect robots.txt
- ✅ Use reasonable rate limits (1-2 req/sec)
- ✅ Identify your bot with proper User-Agent
- ✅ Scrape during off-peak hours
- ✅ Cache responses to avoid re-scraping
- ✅ Use APIs when available

### 2. Data Management

- 📁 Organize by source and date
- 💾 Backup raw data before processing
- 🔍 Validate data quality regularly
- 📊 Generate and review scraping reports
- 🗑️ Clean up intermediate files

### 3. Performance Optimization

- ⚡ Use async scrapers for speed
- 🔄 Enable caching
- 📦 Process in batches
- 🌙 Run heavy scraping overnight
- 💻 Use adequate hardware

---

## Next Steps

After collecting data:

1. **Generate Embeddings**
   - Use OpenAI API or local models
   - Add embeddings to database

2. **Build Vector Index**
   - Configure FAISS or Pinecone
   - Enable semantic search

3. **Set Up RAG System**
   - Configure retrieval pipeline
   - Test query performance

4. **Create API**
   - Use FastAPI endpoints
   - Add authentication

---

## Support & Resources

### Documentation
- [Main Architecture](./ARCHITECTURE.md)
- [Data Collection Plan](./LEGAL_DATA_COLLECTION_PLAN.md)
- [API Documentation](./API.md)

### External Resources
- CourtListener API: https://www.courtlistener.com/help/api/
- Cornell LII: https://www.law.cornell.edu/
- Free Law Project: https://free.law/

### Issues
If you encounter bugs:
1. Check this troubleshooting guide
2. Review scraper logs in `data/reports/`
3. Open an issue on GitHub with logs

---

## License & Legal

### Data Licensing
- US Government documents (Constitution, cases, statutes): **Public Domain**
- Legal dictionaries: Check individual source licenses
- CourtListener data: Free for research and non-commercial use

### Attribution
Please attribute data sources:
- National Archives for Constitution
- Free Law Project for CourtListener data
- Cornell LII for Wex dictionary
- Justia for state laws

### Commercial Use
If planning commercial use:
- Review each source's Terms of Service
- Consider purchasing commercial licenses
- Support nonprofit sources (Free Law Project, Cornell LII)

---

**Version:** 1.0
**Last Updated:** 2025-12-10
**Maintained by:** Legal AI Development Team
