# Comprehensive Legal Data Collection Plan

## Executive Summary
This document outlines the complete strategy for building a comprehensive legal documents database covering all 50 US states, federal laws, constitutional documents, Supreme Court cases, state court cases, and legal dictionaries.

---

## 1. Data Sources

### 1.1 US Constitution & Bill of Rights
**Official Source:** National Archives (archives.gov)
- **URL:** https://www.archives.gov/founding-docs/bill-of-rights-transcript
- **Content:** Full text of Constitution, Bill of Rights (first 10 amendments), and all 27 amendments
- **Format:** HTML/Text
- **Scraping Method:** Direct web scraping
- **Authority:** Official U.S. Government source

**Alternative/Supplementary:** Cornell LII
- **URL:** https://www.law.cornell.edu/constitution
- **Format:** Structured HTML with annotations

### 1.2 All 50 States' Laws & Statutes

#### Primary Sources (Ranked by Priority):

**1. State Official Legislative Websites (Best - Authoritative)**
- Each state maintains its own official legislative website
- Most authoritative source
- Requires state-specific scrapers (50 different implementations)
- Examples:
  - California: leginfo.legislature.ca.gov
  - New York: nysenate.gov/legislation
  - Texas: statutes.capitol.texas.gov

**2. Cornell Legal Information Institute (LII)**
- **URL:** https://www.law.cornell.edu/states/listing
- **Coverage:** All 50 states
- **Content:** Constitutions, statutes, recent legislation
- **Format:** Well-structured HTML
- **Authority:** High (academic institution)
- **API:** None (requires scraping)

**3. Justia (Currently Implemented)**
- **URL:** https://law.justia.com/
- **Coverage:** All 50 states
- **Content:** State codes, statutes, cases
- **Format:** HTML
- **Authority:** High (established legal research platform)
- **Already Implemented:** Yes (src/scrapers/justia_scraper.py)

**4. FindLaw by Thomson Reuters**
- **URL:** https://codes.findlaw.com/
- **Coverage:** All 50 states + federal codes
- **Content:** State and federal statutes
- **Format:** HTML
- **Authority:** Very High (Thomson Reuters)

### 1.3 Supreme Court Cases (Past 50 Years: 1974-2024)

#### Primary Source: CourtListener (Recommended)
- **URL:** https://www.courtlistener.com
- **Operator:** Free Law Project (501c3 nonprofit)
- **API:** Yes (REST API v4)
- **API Docs:** https://www.courtlistener.com/help/api/rest/
- **Bulk Data:** Yes (preferred for large datasets)
- **Coverage:** Complete Supreme Court corpus
- **Format:** JSON/XML
- **Cost:** Free (rate-limited API, or full bulk download)
- **Authentication:** Optional API key for higher rate limits
- **Data Quality:** Excellent - includes SCDB metadata

#### Alternative Source: Caselaw Access Project (Harvard)
- **URL:** https://case.law/
- **Coverage:** All official US case law through 2020
- **API:** Yes (but limited after Sept 2024)
- **Integration:** Now searches via CourtListener
- **Format:** JSON

### 1.4 State Court Cases (All 50 States, Public Records)

#### Primary Source: CourtListener
- **Coverage:** 470+ jurisdictions including:
  - U.S. Supreme Court
  - Federal Appellate Courts
  - Federal District & Bankruptcy Courts
  - **State Supreme Courts (all 50 states)**
  - **State Appellate Courts (all 50 states)**
- **API:** https://www.courtlistener.com/help/api/rest/v3/case-law/
- **Bulk Data:** Available
- **Recommended Approach:** Use bulk data download for initial load, API for updates

#### Alternative/Supplementary Sources:
1. **Caselaw Access Project (CAP)**
   - Historical cases through 2020
   - Now integrated with CourtListener for search

2. **State-Specific Court Websites**
   - Official state court systems
   - Varies by state (some have APIs, most require scraping)
   - Most authoritative but least standardized

### 1.5 Federal Laws (U.S. Code, CFR)

#### Primary Source: U.S. House of Representatives
- **URL:** https://uscode.house.gov/
- **Coverage:** Complete U.S. Code (USC)
- **Format:** XML/HTML
- **Authority:** Official source
- **API:** Limited

#### Alternative: Cornell LII
- **URL:** https://www.law.cornell.edu/uscode/text
- **Format:** Well-structured HTML
- **Easier to scrape than official source

### 1.6 Legal Dictionaries (Top 3 Sources)

#### 1. Wex by Cornell LII (Best - Free & Comprehensive)
- **URL:** https://www.law.cornell.edu/wex
- **Content:** Comprehensive legal dictionary and encyclopedia
- **Authors:** Legal experts and academics
- **Format:** Structured HTML
- **Scraping:** Easy (well-structured)
- **Authority:** Very High (Cornell Law School)
- **Cost:** Free

#### 2. TheLawDictionary.org (Black's Law Dictionary 2nd Edition)
- **URL:** https://thelawdictionary.org/
- **Content:** Based on Black's Law Dictionary 2nd Ed.
- **Format:** HTML
- **Authority:** High (Black's is the gold standard)
- **Cost:** Free
- **Note:** 2nd edition is older but still authoritative

#### 3. FindLaw Legal Dictionary
- **URL:** https://dictionary.findlaw.com/
- **Content:** 8,200+ legal terms
- **Source:** Merriam-Webster's Dictionary of Law (1996)
- **Format:** HTML
- **Authority:** High (Merriam-Webster/Thomson Reuters)
- **Cost:** Free

#### Supplementary: Nolo's Free Dictionary
- **URL:** https://www.nolo.com/dictionary
- **Content:** Plain-English legal definitions
- **Format:** HTML
- **Best For:** Simplified definitions for non-lawyers

---

## 2. Data Structure & Database Schema

### 2.1 Core Tables (Already Implemented)

#### `state_laws`
```sql
- id (UUID)
- state (VARCHAR(2)) - 2-letter state code
- statute_number (VARCHAR(100))
- title (TEXT)
- chapter (VARCHAR(100))
- section (VARCHAR(100))
- full_text (TEXT)
- effective_date (DATE)
- last_amended (DATE)
- jurisdiction (VARCHAR(50))
- source_url (TEXT)
- metadata (JSONB)
- embedding (VECTOR(1536))
- created_at, updated_at (TIMESTAMP)
```

#### `federal_laws`
```sql
- id (UUID)
- usc_title (INTEGER)
- section (VARCHAR(100))
- title (TEXT)
- full_text (TEXT)
- effective_date (DATE)
- agency (VARCHAR(200))
- cfr_reference (VARCHAR(100))
- source_url (TEXT)
- metadata (JSONB)
- embedding (VECTOR(1536))
- created_at, updated_at
```

#### `cases`
```sql
- id (UUID)
- case_name (TEXT)
- citation (VARCHAR(200))
- court (VARCHAR(200))
- jurisdiction (VARCHAR(100))
- date_decided (DATE)
- judges (TEXT[]) - Array
- docket_number (VARCHAR(100))
- opinion_text (TEXT)
- opinion_type (VARCHAR(50)) - majority/dissent/concurring
- metadata (JSONB)
- embedding (VECTOR(1536))
- created_at, updated_at
```

#### `legal_terms`
```sql
- id (UUID)
- term (TEXT UNIQUE)
- definition (TEXT)
- jurisdiction (VARCHAR(100))
- source (VARCHAR(200))
- metadata (JSONB)
- embedding (VECTOR(1536))
- created_at, updated_at
```

#### `precedent_relationships`
```sql
- id (UUID)
- citing_case_id (UUID FK)
- cited_case_id (UUID FK)
- relationship_type (VARCHAR(50)) - followed/distinguished/overruled/cited
- context (TEXT)
- created_at
```

### 2.2 New Table Needed: Constitutional Documents

```sql
CREATE TABLE IF NOT EXISTS constitutional_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_type VARCHAR(100) NOT NULL, -- 'constitution', 'amendment', 'bill_of_rights'
    article_number VARCHAR(50),
    section_number VARCHAR(50),
    amendment_number INTEGER,
    title TEXT NOT NULL,
    full_text TEXT NOT NULL,
    ratified_date DATE,
    jurisdiction VARCHAR(50) DEFAULT 'federal',
    source_url TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    embedding VECTOR(1536)
);
```

### 2.3 Metadata Standards

Each `metadata` JSONB field should include:
```json
{
  "scrape_date": "2024-12-10",
  "scraper_version": "1.0.0",
  "source_name": "CourtListener",
  "original_format": "json",
  "data_quality_score": 0.95,
  "verification_status": "verified|unverified",
  "tags": ["criminal_law", "constitutional_rights"],
  "related_documents": ["case_id_1", "statute_id_2"]
}
```

---

## 3. Scraping Strategy

### 3.1 Priority Order (Recommended Implementation Sequence)

1. **US Constitution & Bill of Rights** (Easiest, ~1 hour)
   - Single scraper for National Archives
   - Small dataset
   - Critical foundation document

2. **Legal Dictionaries** (Easy, ~2-4 hours)
   - 3 scrapers (Wex, TheLawDictionary, FindLaw)
   - Well-structured HTML
   - ~10,000-15,000 terms total

3. **Supreme Court Cases via CourtListener API** (Medium, ~4-8 hours)
   - Use REST API or bulk data
   - Filter by date range (1974-2024)
   - ~5,000-6,000 cases

4. **State Laws - Enhanced** (Medium-Hard, ~1-2 weeks)
   - Improve existing Justia scraper
   - Add Cornell LII scraper
   - Add FindLaw scraper
   - Validate against official state sources for critical states

5. **Federal Laws (U.S. Code)** (Medium-Hard, ~1 week)
   - Cornell LII scraper
   - House.gov XML parser

6. **State Court Cases via CourtListener** (Hard, ~1-2 weeks)
   - Use bulk data download (recommended)
   - Or API with careful rate limiting
   - Largest dataset: millions of cases

### 3.2 Technical Approach

#### A. For Simple HTML Scrapers
- **Libraries:** `httpx` (async), `BeautifulSoup4`, `lxml`
- **Rate Limiting:** 1-2 requests/second
- **Retries:** Exponential backoff (tenacity library)
- **Caching:** Cache responses to avoid re-scraping
- **User Agent:** Rotate user agents, identify as research bot

#### B. For APIs (CourtListener)
- **Authentication:** API key (free registration)
- **Rate Limits:** Respect API limits (documented)
- **Bulk Data:** Preferred for large datasets
- **Format:** JSON
- **Pagination:** Handle cursor-based pagination

#### C. For Bulk Data Downloads
- **Storage:** Download to `data/raw/` directory
- **Processing:** Stream processing for large files
- **Validation:** Checksum verification
- **Deduplication:** Check against existing DB records

### 3.3 Data Quality & Validation

#### Quality Checks:
1. **Completeness:** All required fields populated
2. **Format Validation:** Dates, citations, jurisdiction codes
3. **Deduplication:** Check unique constraints before insertion
4. **Text Quality:** Remove HTML artifacts, normalize whitespace
5. **Citation Validation:** Use existing citation_checker.py
6. **Embedding Generation:** Generate after text cleaning

#### Error Handling:
- Log all failures with source URL and error type
- Quarantine problematic records for manual review
- Continue on error (don't fail entire scrape)
- Generate scraping report with statistics

---

## 4. Scraper Implementation Plan

### 4.1 Scrapers to Create (12 total)

| # | Scraper Name | Source | Priority | Complexity | Est. Time |
|---|-------------|--------|----------|------------|-----------|
| 1 | `constitution_scraper.py` | National Archives | HIGH | Easy | 1-2 hours |
| 2 | `wex_dictionary_scraper.py` | Cornell Wex | HIGH | Easy | 2-3 hours |
| 3 | `lawdict_scraper.py` | TheLawDictionary.org | HIGH | Easy | 2-3 hours |
| 4 | `findlaw_dict_scraper.py` | FindLaw Dictionary | HIGH | Easy | 2-3 hours |
| 5 | `courtlistener_scotus_scraper.py` | CourtListener API | HIGH | Medium | 4-6 hours |
| 6 | `cornell_state_laws_scraper.py` | Cornell LII States | MEDIUM | Medium | 6-8 hours |
| 7 | `findlaw_codes_scraper.py` | FindLaw Codes | MEDIUM | Medium | 6-8 hours |
| 8 | `cornell_usc_scraper.py` | Cornell USC | MEDIUM | Medium | 6-8 hours |
| 9 | `courtlistener_state_courts_scraper.py` | CourtListener API | HIGH | Hard | 8-12 hours |
| 10 | `courtlistener_bulk_processor.py` | CourtListener Bulk | HIGH | Hard | 8-12 hours |
| 11 | Enhance `justia_scraper.py` | Justia | MEDIUM | Medium | 4-6 hours |
| 12 | State-specific official scrapers | Various | LOW | Very Hard | Ongoing |

### 4.2 Master Orchestration Script

Create `scripts/scrape_all_legal_data.py`:
```python
# Master script to orchestrate all scraping
# - Run scrapers in priority order
# - Generate comprehensive reports
# - Handle errors gracefully
# - Support resume/incremental updates
```

Features:
- Progress tracking with tqdm
- Parallel scraping where appropriate
- Database health checks
- Backup before large imports
- Detailed logging and reports

---

## 5. Estimated Data Volumes

| Data Type | Estimated Count | Storage Size |
|-----------|----------------|--------------|
| US Constitution + Amendments | ~50 documents | < 1 MB |
| State Laws (all 50 states) | 500,000 - 2M statutes | 5-20 GB |
| Federal Laws (USC) | 50,000+ sections | 2-5 GB |
| Supreme Court Cases (50 yrs) | ~5,000 cases | 500 MB - 1 GB |
| State Court Cases | 10M+ cases | 100+ GB |
| Legal Dictionary Terms | 15,000 terms | 5-10 MB |
| **TOTAL** | **10M+ records** | **100-150 GB** |

### Storage Recommendations:
- **Database:** 200+ GB (with indexes and embeddings)
- **Raw Data Storage:** 100-150 GB
- **Vector Embeddings:** 50-75 GB (1536-dim vectors for all text)

---

## 6. Rate Limiting & Ethics

### 6.1 Rate Limiting Guidelines

| Source | Max Rate | Daily Limit | Notes |
|--------|----------|-------------|-------|
| National Archives | 1 req/sec | Unlimited | Small dataset |
| Cornell LII | 1 req/sec | 10,000 | Be respectful |
| Justia | 1 req/sec | 10,000 | Currently used |
| FindLaw | 1 req/sec | 10,000 | Commercial site |
| CourtListener API | As per docs | Varies by tier | Get API key |
| Official State Sites | 0.5 req/sec | 5,000 | Very conservative |

### 6.2 Ethical Scraping Practices

1. **Respect robots.txt** - Always check and honor
2. **Identify your bot** - Use descriptive user agent
3. **Rate limiting** - Never overwhelm servers
4. **Off-peak hours** - Run heavy scraping at night (US time)
5. **Use APIs when available** - Prefer official APIs
6. **Cache aggressively** - Don't re-scrape same content
7. **Give attribution** - Credit sources in metadata

### 6.3 Legal Considerations

- **Public Domain:** US government documents are public domain
- **Case Law:** Generally public information, free to republish
- **Terms of Service:** Review each site's ToS
- **Commercial Use:** If planning commercial use, verify licensing
- **Personal Use/Research:** Generally protected under fair use

---

## 7. Implementation Timeline

### Phase 1: Foundation (Week 1)
- [ ] Create constitutional_documents table
- [ ] Implement Constitution scraper
- [ ] Implement 3 legal dictionary scrapers
- [ ] Test database ingestion pipeline

### Phase 2: Case Law (Week 2-3)
- [ ] Set up CourtListener API access
- [ ] Implement Supreme Court scraper
- [ ] Test with sample data
- [ ] Implement state court cases scraper
- [ ] Begin bulk data processing

### Phase 3: Statutory Law (Week 4-5)
- [ ] Implement Cornell state laws scraper
- [ ] Implement FindLaw codes scraper
- [ ] Enhance Justia scraper
- [ ] Implement USC scraper

### Phase 4: Integration & Testing (Week 6)
- [ ] Create master orchestration script
- [ ] Full system test with all scrapers
- [ ] Data quality validation
- [ ] Performance optimization
- [ ] Documentation

### Phase 5: Full Data Collection (Ongoing)
- [ ] Run complete scraping process
- [ ] Monitor and handle errors
- [ ] Generate embeddings for all text
- [ ] Create backup and archival strategy

---

## 8. Next Steps

1. **Review and approve this plan**
2. **Set up CourtListener API account**
3. **Create constitutional_documents table**
4. **Implement scrapers in priority order**
5. **Test each scraper with sample data before full run**

---

## 9. Resources & Documentation

### Official Documentation:
- [CourtListener API Docs](https://www.courtlistener.com/help/api/)
- [Cornell LII](https://www.law.cornell.edu/)
- [National Archives](https://www.archives.gov/)

### Legal Research Libraries:
- Harvard Law School Library
- Georgetown Law Library
- Library of Congress Legal Research Guides

### Python Libraries:
- `httpx` - Async HTTP client
- `beautifulsoup4` - HTML parsing
- `lxml` - Fast XML/HTML processing
- `tenacity` - Retry logic
- `tqdm` - Progress bars
- `pydantic` - Data validation

---

**Document Version:** 1.0
**Last Updated:** 2025-12-10
**Author:** Legal AI System Development Team
