# Legal-AI Assistant Documentation

Welcome to the Legal-AI Assistant documentation!

## 📚 Documentation Index

### Getting Started

- **[Setup Guide](SETUP_GUIDE.md)** - Complete step-by-step setup instructions
  - Getting all API keys and credentials
  - Setting up Supabase database
  - Configuring vector storage
  - Downloading AI models
  - Troubleshooting common issues

- **[Free AI Options](FREE_AI_OPTIONS.md)** - Guide to using 100% free AI services
  - Groq API (RECOMMENDED - fastest free option)
  - HuggingFace Inference API
  - Local models (offline)
  - Cost comparisons
  - Vector storage explained

### Quick Links

| Document | Purpose | Time to Complete |
|----------|---------|------------------|
| [Setup Guide](SETUP_GUIDE.md) | Full setup instructions | 30 minutes |
| [Free AI Options](FREE_AI_OPTIONS.md) | Free alternatives to paid APIs | 10 minutes |

## 🚀 Quick Start

### Absolute Minimum Setup (5 minutes)

1. **Get Free AI API Key** (choose one):
   - **Groq** (Recommended): https://console.groq.com/ - 14,400 requests/day
   - **HuggingFace**: https://huggingface.co/settings/tokens - 30,000 requests/month

2. **Get Supabase Database** (free):
   - Sign up: https://supabase.com/
   - Create project (takes 2 minutes)
   - Get URL and API key

3. **Configure Environment:**
   ```bash
   cp .env.example .env
   # Edit .env and add your keys
   ```

4. **Run Setup:**
   ```bash
   bash scripts/setup_environment.sh
   ```

5. **Start API:**
   ```bash
   source venv/bin/activate
   uvicorn src.api.main:app --reload
   ```

**Total Cost: $0** ✨

## 🆓 Free vs Paid

### What You Get Free

- ✅ **14,400 AI requests/day** with Groq
- ✅ **500 MB database** with Supabase
- ✅ **Unlimited vector search** with FAISS (local)
- ✅ **Free embeddings** with local models
- ✅ **Full functionality** of the Legal-AI Assistant

### When to Upgrade

You only need paid services if:
- You exceed 14,400 AI requests/day
- You need more than 500 MB database storage
- You want GPT-4/Claude quality (vs Llama 3)

## 🎯 What's This Project?

Legal-AI Assistant is a **hybrid AI system** that helps you:

1. **Search legal documents** - Find relevant laws, cases, and precedents
2. **Answer legal questions** - Get AI-powered answers with citations
3. **Analyze cases** - Extract key information from legal opinions
4. **Track precedents** - Build citation graphs showing case relationships

### Key Features

- 🔍 **Semantic Search** - Find by meaning, not just keywords
- 🤖 **Multiple AI Models** - Cloud (GPT-4, Claude) + Local (Llama 3, Mixtral)
- 📊 **Vector Database** - Fast similarity search over millions of documents
- ⚖️ **Legal Data** - State laws, federal laws, case law, legal terms
- 🔗 **Citation Tracking** - Precedent relationships and citation graphs
- 💰 **Cost Optimized** - Automatically uses cheapest models first

## 🏗️ Architecture

```
┌─────────────┐
│   User      │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│     FastAPI Backend (Python)        │
│  ┌──────────┐  ┌─────────────────┐ │
│  │ REST API │  │  Model Router   │ │
│  └──────────┘  └─────────────────┘ │
└──────┬──────────────┬───────────────┘
       │              │
       ▼              ▼
┌──────────────┐ ┌──────────────────┐
│  Supabase    │ │  AI Models       │
│  (Postgres)  │ │  - Groq          │
│  + pgvector  │ │  - HuggingFace   │
│              │ │  - Local (Llama) │
└──────────────┘ └──────────────────┘
```

## 📖 Vector Storage Explained

**Q: What is vector storage for?**

Vector storage enables **semantic search** - finding similar documents by meaning instead of exact keyword matches.

### How It Works

1. **Convert text to numbers:**
   - "What is habeas corpus?" → `[0.23, -0.41, 0.67, ...1536 numbers]`

2. **Store vectors in database:**
   - Save the vector alongside the original text

3. **Search by similarity:**
   - Convert query to vector
   - Find documents with similar vectors (using cosine similarity)
   - Return the original text

### Why It's Powerful

**Traditional search:**
- Query: "breach of contract"
- Finds: Only documents with exact words "breach" and "contract"

**Vector search:**
- Query: "breach of contract"
- Finds: "violation of agreement", "breaking terms", "contractual default"
- **Why?** These phrases have similar *meaning* (similar vectors)

### Free Options

- **FAISS** (default) - Local, fast, free
- **ChromaDB** - Local, free, good for larger datasets
- **Qdrant** - Cloud, free tier (1 GB)

See [Free AI Options](FREE_AI_OPTIONS.md#-free-embeddings-for-vector-search) for details.

## 💡 Common Questions

### Do I need a GPU?

**No!** You can use:
- Cloud APIs (Groq, HuggingFace) - no GPU needed
- Local models with CPU (slow but works)
- Local models with GPU (faster)

### Do I need to pay for anything?

**No!** Everything can run completely free:
- Groq API: Free (14,400 req/day)
- Supabase: Free tier (500 MB)
- Vector storage: Free (FAISS, local)
- Embeddings: Free (local models)

### How much data can I store?

**Free tier:**
- Supabase: 500 MB (~100,000 laws/cases)
- FAISS: Limited by disk space (can store millions)

**Paid tier:**
- Supabase Pro: 100 GB ($25/month)

### Can this work offline?

**Yes!** Use local-only mode:
- Local AI models (Llama 3)
- Local vector storage (FAISS)
- Local database (PostgreSQL)
- Local embeddings

No internet needed after initial setup.

## 🛠️ Troubleshooting

### Common Issues

1. **"ModuleNotFoundError"**
   - Solution: `pip install -r requirements.txt`

2. **"Supabase connection failed"**
   - Solution: Check `SUPABASE_URL` and `SUPABASE_KEY` in `.env`

3. **"Rate limit exceeded"**
   - Solution: Enable caching (`CACHE_ENABLED=true`) or use local models

See [Setup Guide - Troubleshooting](SETUP_GUIDE.md#-troubleshooting) for more.

## 📞 Getting Help

- 📖 Read the [Setup Guide](SETUP_GUIDE.md) for detailed instructions
- 🆓 Check [Free AI Options](FREE_AI_OPTIONS.md) for cost-free alternatives
- 🐛 Open an issue on GitHub
- 💬 Check existing issues for solutions

## 🎓 Learning Resources

### Understanding RAG (Retrieval-Augmented Generation)

RAG combines:
1. **Retrieval** - Find relevant documents (vector search)
2. **Augmentation** - Add documents to prompt
3. **Generation** - AI generates answer using documents

### Understanding Embeddings

Embeddings convert text to numbers that capture meaning:
- Similar texts → Similar numbers
- "lawyer" and "attorney" → Very similar vectors
- "lawyer" and "banana" → Very different vectors

### Understanding Vector Databases

Vector databases optimize for:
- **Cosine similarity** - Measure how similar two vectors are
- **Approximate search** - Find "close enough" matches quickly
- **Scale** - Search millions of vectors in milliseconds

## 🚀 Next Steps

After setup, explore:

1. **Scrape Legal Data:**
   ```bash
   python scripts/scrape_to_supabase.py
   ```

2. **Try Example Queries:**
   ```bash
   python scripts/example_query.py
   ```

3. **Build Your Application:**
   - Use the REST API
   - Build a web interface
   - Integrate with your tools

Happy building! ⚖️🤖
