# Complete Setup Guide - Legal-AI Assistant

## 📋 Table of Contents

1. [Getting API Keys & Credentials](#getting-api-keys--credentials)
2. [Setting Up Database (Supabase)](#setting-up-database-supabase)
3. [Configuring Vector Storage](#configuring-vector-storage)
4. [Downloading AI Models](#downloading-ai-models)
5. [Environment Configuration](#environment-configuration)
6. [Troubleshooting](#troubleshooting)

---

## 🔑 Getting API Keys & Credentials

This section provides step-by-step instructions for obtaining every credential needed in your `.env` file.

### 1. OpenAI API Key (Optional - Paid)

**What it's for:** GPT-4 for complex legal reasoning

**Cost:** ~$0.01-0.05 per query (pay-as-you-go)

**Steps:**

1. Go to https://platform.openai.com/signup
2. Create an account or sign in
3. Click on your profile (top right) → "View API Keys"
4. Click "Create new secret key"
5. Give it a name (e.g., "Legal-AI-Assistant")
6. Copy the key (starts with `sk-...`)
7. **IMPORTANT:** Save it immediately - you can't see it again!

**Add to .env:**
```bash
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxx
```

**Free Alternative:** Skip this and use Groq or HuggingFace (see Free AI Options below)

---

### 2. Anthropic API Key (Optional - Paid)

**What it's for:** Claude 3 Opus for legal analysis

**Cost:** Pay-per-use (similar to OpenAI)

**Steps:**

1. Go to https://console.anthropic.com/
2. Sign up for an account
3. Navigate to "API Keys" in the dashboard
4. Click "Create Key"
5. Copy the key (starts with `sk-ant-...`)

**Add to .env:**
```bash
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxx
```

**Free Alternative:** Skip this and use Groq or HuggingFace (see Free AI Options)

---

### 3. HuggingFace API Key (FREE - RECOMMENDED)

**What it's for:** Free access to Llama-2, Mistral, Mixtral, and more

**Cost:** FREE tier: 30,000 requests/month

**Steps:**

1. Go to https://huggingface.co/join
2. Create a free account
3. Go to Settings → Access Tokens (https://huggingface.co/settings/tokens)
4. Click "New token"
5. Give it a name (e.g., "Legal-AI")
6. Select "Read" permission
7. Click "Generate a token"
8. Copy the token (starts with `hf_...`)

**Add to .env:**
```bash
HUGGINGFACE_API_KEY=hf_xxxxxxxxxxxxxxxxxxxx
```

**Available Models (FREE):**
- `mistralai/Mistral-7B-Instruct-v0.2`
- `meta-llama/Llama-2-70b-chat-hf`
- `HuggingFaceH4/zephyr-7b-beta`

---

### 4. Groq API Key (FREE - FASTEST INFERENCE)

**What it's for:** Ultra-fast inference for Llama-3, Mixtral (FREE!)

**Cost:** FREE tier: 14,400 requests/day (10 requests/min)

**Steps:**

1. Go to https://console.groq.com/
2. Sign up with Google, GitHub, or email
3. Navigate to "API Keys" section
4. Click "Create API Key"
5. Give it a name
6. Copy the key (starts with `gsk_...`)

**Add to .env:**
```bash
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx
```

**Available Models (FREE):**
- `llama3-8b-8192` - Llama 3 8B (8k context)
- `llama3-70b-8192` - Llama 3 70B (8k context)
- `mixtral-8x7b-32768` - Mixtral 8x7B (32k context)
- `gemma-7b-it` - Google Gemma 7B

**This is the BEST free option for fast, quality AI!**

---

### 5. Supabase Credentials (Database)

**What it's for:** PostgreSQL database with vector search (pgvector)

**Cost:** FREE tier: 500 MB storage, 2 GB bandwidth/month

**Steps:**

1. Go to https://supabase.com/
2. Click "Start your project" → Sign up (GitHub recommended)
3. Click "New project"
4. Fill in:
   - **Name:** `legal-ai-assistant`
   - **Database Password:** (generate a strong password - save it!)
   - **Region:** Choose closest to you
   - **Pricing Plan:** Free
5. Click "Create new project" (takes ~2 minutes)
6. Once ready, go to "Settings" → "API"
7. Copy:
   - **Project URL** (under "Project API keys")
   - **anon public** key (for client-side) OR **service_role** key (for server-side)

**Add to .env:**
```bash
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xxxxxxxxxxxx
```

**Next Step:** Run the database schema:
1. Go to Supabase Dashboard → SQL Editor
2. Copy contents of `scripts/supabase_schema.sql`
3. Paste and click "Run"

---

### 6. Pinecone API Key (Optional - Vector Database)

**What it's for:** Cloud vector storage (alternative to FAISS)

**Cost:** FREE tier: 1 index, 100K vectors

**Steps:**

1. Go to https://www.pinecone.io/
2. Sign up for free account
3. Create a new index:
   - Name: `legal-ai`
   - Dimensions: `1536` (for OpenAI) or `384` (for local embeddings)
   - Metric: `cosine`
4. Go to "API Keys" in dashboard
5. Copy your API key and environment

**Add to .env:**
```bash
PINECONE_API_KEY=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
PINECONE_ENVIRONMENT=us-west1-gcp
VECTOR_STORE_TYPE=pinecone
```

**Free Alternative:** Use FAISS (default, no setup needed) or ChromaDB

---

### 7. Qdrant API Key (Optional - FREE Vector DB)

**What it's for:** Free cloud vector database

**Cost:** FREE tier: 1GB storage

**Steps:**

1. Go to https://cloud.qdrant.io/
2. Sign up with email or GitHub
3. Create a new cluster (FREE tier)
4. Get your API key from dashboard
5. Copy your cluster URL

**Add to .env:**
```bash
QDRANT_API_KEY=xxxxxxxxxxxxxxxxxxxx
QDRANT_URL=https://xxxxx.qdrant.io:6333
VECTOR_STORE_TYPE=qdrant
```

---

### 8. API Secret Key (Required)

**What it's for:** JWT authentication for your API

**Steps:**

1. Open terminal
2. Generate a random key:
   ```bash
   openssl rand -hex 32
   ```
3. Copy the output

**Add to .env:**
```bash
API_SECRET_KEY=your_generated_random_key_here
```

---

## 🗄️ Setting Up Database (Supabase)

### Step 1: Create Supabase Project

Follow the steps in [Section 5 above](#5-supabase-credentials-database)

### Step 2: Run Database Schema

1. Open Supabase Dashboard
2. Go to **SQL Editor** (left sidebar)
3. Click **New query**
4. Copy and paste the entire contents of `scripts/supabase_schema.sql`
5. Click **Run** (or press Ctrl+Enter)

You should see:
```
✅ Legal AI Database Schema Created Successfully!
Tables created: state_laws, federal_laws, cases, legal_terms, precedent_relationships
```

### Step 3: Verify Setup

Run this query in SQL Editor:
```sql
SELECT * FROM get_database_stats();
```

You should see all tables with 0 rows (they're empty until you scrape data).

---

## 📦 Configuring Vector Storage

### Option 1: FAISS (Recommended - FREE, Local)

**No setup needed!** FAISS is the default and stores vectors locally.

**Configuration:**
```bash
VECTOR_STORE_TYPE=faiss
```

**Storage Location:** `data/vector_store/`

**Pros:**
- Completely free
- No API limits
- Fast for small-medium datasets
- Works offline

**Cons:**
- Slower for very large datasets (>1M vectors)
- Stored on disk (requires local storage)

---

### Option 2: ChromaDB (FREE, Local)

**No setup needed!** ChromaDB is also local and free.

**Configuration:**
```bash
VECTOR_STORE_TYPE=chromadb
```

**Pros:**
- Free and local
- Better for larger datasets than FAISS
- Persistent storage with metadata

**Cons:**
- Slightly slower than FAISS for small datasets

---

### Option 3: Qdrant (FREE Cloud)

**Setup:** See [Section 7 above](#7-qdrant-api-key-optional---free-vector-db)

**Configuration:**
```bash
VECTOR_STORE_TYPE=qdrant
QDRANT_API_KEY=your_key
QDRANT_URL=https://your-cluster.qdrant.io:6333
```

**Pros:**
- Free 1GB storage
- Cloud-hosted (no local storage needed)
- Fast vector search

**Cons:**
- Requires internet connection
- Limited to 1GB on free tier

---

### Option 4: Pinecone (Freemium)

**Setup:** See [Section 6 above](#6-pinecone-api-key-optional---vector-database)

**Configuration:**
```bash
VECTOR_STORE_TYPE=pinecone
PINECONE_API_KEY=your_key
PINECONE_ENVIRONMENT=us-west1-gcp
```

**Pros:**
- Industry-standard vector DB
- Very fast
- Good free tier

**Cons:**
- Limited to 100K vectors on free tier

---

## 🤖 Downloading AI Models

### For Local Inference (Optional but Recommended)

Local models let you run AI without any API keys or internet!

### Prerequisites

```bash
# Install HuggingFace CLI
pip install huggingface-hub

# Login to HuggingFace
huggingface-cli login
# Paste your HF token (from Section 3 above)
```

### Download Llama 3 8B (~16 GB)

```bash
huggingface-cli download \
  meta-llama/Meta-Llama-3-8B-Instruct \
  --local-dir models/llama3-8b-instruct
```

**Note:** You'll need to accept Meta's license on HuggingFace first:
1. Go to https://huggingface.co/meta-llama/Meta-Llama-3-8B-Instruct
2. Click "Access repository"
3. Accept terms

### Download Mixtral 8x7B (~47 GB)

```bash
huggingface-cli download \
  mistralai/Mixtral-8x7B-Instruct-v0.1 \
  --local-dir models/mixtral-8x7b-instruct
```

### Download Embeddings Model (Auto-downloaded)

These models download automatically on first use:
- `sentence-transformers/all-MiniLM-L6-v2` (~90 MB) - Fast, good quality
- `sentence-transformers/all-mpnet-base-v2` (~420 MB) - Better quality

---

## ⚙️ Environment Configuration

### Complete .env Setup

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### Minimum Configuration (FREE Options Only)

```bash
# FREE AI (Choose one or both)
HUGGINGFACE_API_KEY=hf_xxxxxxxxxxxx  # 30K requests/month
GROQ_API_KEY=gsk_xxxxxxxxxxxx      # 14,400 requests/day

# Database (required)
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGxxx...

# Vector Storage (default to FAISS - no key needed)
VECTOR_STORE_TYPE=faiss

# Embeddings (use free local model)
EMBEDDING_MODEL=local

# Security (generate with: openssl rand -hex 32)
API_SECRET_KEY=your_random_secret_key

# Model routing (use free models first)
MODEL_ROUTING_STRATEGY=cost_optimized
```

### Full Configuration (All Options)

See `.env.example` for complete configuration with all options documented.

---

## 🔧 Troubleshooting

### Issue: "Import Error: No module named 'xyz'"

**Solution:**
```bash
# Make sure you're in virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: "Supabase connection failed"

**Solution:**
1. Check `SUPABASE_URL` and `SUPABASE_KEY` in `.env`
2. Make sure you used the correct key (anon or service_role)
3. Verify your IP isn't blocked in Supabase dashboard

### Issue: "Vector index not found"

**Solution:**
```bash
# Initialize vector store
python scripts/init_vector_store.py
```

### Issue: "Model not found" for local models

**Solution:**
1. Check model path in `.env`:
   ```bash
   LLAMA3_MODEL_PATH=models/llama3-8b-instruct
   ```
2. Verify files exist:
   ```bash
   ls models/llama3-8b-instruct/
   ```
3. Re-download if missing (see Downloading AI Models section)

### Issue: "Out of memory" when loading models

**Solution:**
1. Use 4-bit quantization:
   ```bash
   MODEL_QUANTIZATION=4bit
   ```
2. Or use cloud APIs instead of local models:
   ```bash
   USE_LOCAL_MODELS_ONLY=false
   ```

### Issue: "Rate limit exceeded" on free APIs

**Solution:**
1. **Groq:** 10 requests/min limit - add delays between requests
2. **HuggingFace:** 30K/month limit - use caching:
   ```bash
   CACHE_ENABLED=true
   CACHE_TTL=3600
   ```

---

## ✅ Verification Checklist

Run this checklist to ensure everything is set up:

- [ ] Python 3.9+ installed
- [ ] Virtual environment created and activated
- [ ] All dependencies installed from `requirements.txt`
- [ ] `.env` file created and configured
- [ ] At least one AI API key configured (Groq or HuggingFace recommended)
- [ ] Supabase project created
- [ ] Supabase credentials added to `.env`
- [ ] Database schema run in Supabase
- [ ] Directory structure created (`data/`, `models/`, `logs/`)
- [ ] Vector store configured (FAISS default)
- [ ] Embedding model configured (local recommended)
- [ ] API secret key generated

### Test Your Setup

```bash
# Activate virtual environment
source venv/bin/activate

# Run test script
python -c "
import os
from dotenv import load_dotenv
load_dotenv()

print('Checking configuration...')
print(f'✓ Groq API: {'SET' if os.getenv('GROQ_API_KEY') else 'NOT SET'}')
print(f'✓ HuggingFace API: {'SET' if os.getenv('HUGGINGFACE_API_KEY') else 'NOT SET'}')
print(f'✓ Supabase URL: {'SET' if os.getenv('SUPABASE_URL') else 'NOT SET'}')
print(f'✓ Supabase Key: {'SET' if os.getenv('SUPABASE_KEY') else 'NOT SET'}')
print(f'✓ API Secret: {'SET' if os.getenv('API_SECRET_KEY') else 'NOT SET'}')
print('Configuration check complete!')
"
```

---

## 🚀 Next Steps

Once setup is complete:

1. **Scrape Legal Data:**
   ```bash
   python scripts/scrape_to_supabase.py
   ```

2. **Start API Server:**
   ```bash
   uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Test API:**
   ```bash
   curl http://localhost:8000/health
   ```

4. **Run Tests:**
   ```bash
   pytest tests/
   ```

---

## 📚 Additional Resources

- [Free AI Options Guide](FREE_AI_OPTIONS.md) - Detailed guide to free AI services
- [API Documentation](API.md) - API endpoints and usage
- [Contributing Guide](CONTRIBUTING.md) - How to contribute to the project

---

**Need help?** Open an issue on GitHub or check the troubleshooting section above.
