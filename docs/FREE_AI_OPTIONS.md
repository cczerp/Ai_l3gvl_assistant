# Free AI Options for Legal-AI Assistant

## 🆓 Complete Guide to FREE AI Services

This guide shows you how to use the Legal-AI Assistant **completely free** - no credit card required!

---

## 📊 Quick Comparison

| Service | Cost | Rate Limit | Best For | Quality | Speed |
|---------|------|------------|----------|---------|-------|
| **Groq** | FREE | 14,400/day | Production use | ⭐⭐⭐⭐⭐ | ⚡ Fastest |
| **HuggingFace** | FREE | 30,000/month | Development | ⭐⭐⭐⭐ | Medium |
| **Local Models** | FREE | Unlimited | Offline use | ⭐⭐⭐⭐ | Slow (CPU) |
| OpenAI GPT-4 | $0.01-0.05/query | Pay-as-you-go | Best quality | ⭐⭐⭐⭐⭐ | Fast |
| Anthropic Claude | Similar to OpenAI | Pay-as-you-go | Long contexts | ⭐⭐⭐⭐⭐ | Fast |

**Recommendation:** Use **Groq** for the best free experience!

---

## 🚀 Option 1: Groq (RECOMMENDED)

### What is Groq?

Groq provides **ultra-fast inference** for open-source models using custom AI chips. It's **completely free** and beats many paid services in speed!

### Features

- ✅ **FREE Forever** - No credit card required
- ✅ **14,400 requests/day** (10 requests/minute)
- ✅ **Fastest inference** - Responses in < 1 second
- ✅ **Latest models:** Llama 3 70B, Mixtral 8x7B, Gemma
- ✅ **Large context:** Up to 32K tokens (Mixtral)
- ✅ **Compatible with OpenAI API** format

### Sign Up (2 minutes)

1. Go to https://console.groq.com/
2. Click "Sign up" (use Google/GitHub for instant access)
3. Navigate to "API Keys"
4. Click "Create API Key"
5. Copy your key (starts with `gsk_...`)

### Add to .env

```bash
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx
```

### Available Models

| Model | Parameters | Context | Best For | Speed |
|-------|------------|---------|----------|-------|
| `llama3-70b-8192` | 70B | 8K | Complex legal reasoning | Very Fast |
| `llama3-8b-8192` | 8B | 8K | Quick queries | Fastest |
| `mixtral-8x7b-32768` | 8x7B | 32K | Long documents | Fast |
| `gemma-7b-it` | 7B | 8K | General purpose | Very Fast |

### Example Usage

```python
from groq import Groq

client = Groq(api_key="gsk_...")

response = client.chat.completions.create(
    model="llama3-70b-8192",
    messages=[{
        "role": "user",
        "content": "What is habeas corpus?"
    }],
    temperature=0.3,
    max_tokens=1024
)

print(response.choices[0].message.content)
```

### Rate Limits

- **10 requests per minute**
- **14,400 requests per day**
- **6,000 tokens per minute** (input)
- **20,000 tokens per minute** (output)

**Tip:** Enable caching in .env to stay within limits:
```bash
CACHE_ENABLED=true
CACHE_TTL=3600
```

### Pros & Cons

**Pros:**
- Absolutely FREE
- Fastest inference available
- High daily limit (14,400 requests)
- Latest open-source models
- No credit card required

**Cons:**
- Rate limited (10 req/min)
- Smaller context than paid services

---

## 🤗 Option 2: HuggingFace Inference API

### What is HuggingFace?

HuggingFace is the GitHub of AI models. Their Inference API lets you run thousands of models for **free** via HTTP requests.

### Features

- ✅ **FREE Tier** - 30,000 requests/month
- ✅ **1000+ models** available
- ✅ **No credit card** required
- ✅ **OpenAI-compatible** API
- ✅ **Serverless** - no infrastructure needed

### Sign Up (1 minute)

1. Go to https://huggingface.co/join
2. Sign up with email or GitHub
3. Go to Settings → Access Tokens
4. Click "New token"
5. Select "Read" permission
6. Copy token (starts with `hf_...`)

### Add to .env

```bash
HUGGINGFACE_API_KEY=hf_xxxxxxxxxxxxxxxxxxxx
```

### Available Models (Free)

| Model | Parameters | Best For | Quality |
|-------|------------|----------|---------|
| `mistralai/Mistral-7B-Instruct-v0.2` | 7B | General legal queries | ⭐⭐⭐⭐ |
| `meta-llama/Llama-2-70b-chat-hf` | 70B | Complex reasoning | ⭐⭐⭐⭐⭐ |
| `HuggingFaceH4/zephyr-7b-beta` | 7B | Fast responses | ⭐⭐⭐⭐ |
| `google/flan-t5-xxl` | 11B | Question answering | ⭐⭐⭐ |

### Example Usage

```python
import requests

API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
headers = {"Authorization": f"Bearer hf_..."}

payload = {
    "inputs": "What is the statute of limitations for contract disputes?",
    "parameters": {
        "max_new_tokens": 500,
        "temperature": 0.3
    }
}

response = requests.post(API_URL, headers=headers, json=payload)
print(response.json()[0]['generated_text'])
```

### Rate Limits

- **30,000 requests per month** (free tier)
- **~1000 requests per day**
- Some models may have additional rate limits

**Upgrade (Optional):**
- **Inference Endpoints:** $0.60/hour for dedicated hosting
- **Pro subscription:** $9/month for faster inference

### Pros & Cons

**Pros:**
- Completely free
- Access to 1000+ models
- No rate limit per minute
- Easy to use

**Cons:**
- Slower than Groq
- Monthly limit (not daily)
- Cold starts (first request may be slow)
- Some models may be queued

---

## 💻 Option 3: Local Models (Offline & FREE)

### What are Local Models?

Run AI models **directly on your computer** - no internet, no API keys, no limits!

### Features

- ✅ **Completely FREE**
- ✅ **Unlimited requests**
- ✅ **100% private** (data never leaves your machine)
- ✅ **Works offline**
- ✅ **No rate limits**

### Requirements

**Minimum (CPU only):**
- 16 GB RAM
- 50 GB free disk space
- Modern CPU (4+ cores)

**Recommended (GPU):**
- 16 GB RAM
- NVIDIA GPU with 8 GB+ VRAM
- 50 GB free disk space

### Setup

#### Step 1: Install Dependencies

Already in `requirements.txt`:
```bash
torch
transformers
accelerate
bitsandbytes  # For 4-bit quantization
sentence-transformers
```

#### Step 2: Download Models

**Quick Download (HuggingFace CLI):**
```bash
# Install CLI
pip install huggingface-hub

# Login
huggingface-cli login

# Download Llama 3 8B (~16 GB)
huggingface-cli download \
  meta-llama/Meta-Llama-3-8B-Instruct \
  --local-dir models/llama3-8b-instruct

# Download Mixtral 8x7B (~47 GB)
huggingface-cli download \
  mistralai/Mixtral-8x7B-Instruct-v0.1 \
  --local-dir models/mixtral-8x7b-instruct
```

**Note:** You'll need to accept Meta's license for Llama 3:
1. Visit https://huggingface.co/meta-llama/Meta-Llama-3-8B-Instruct
2. Click "Access repository"
3. Accept terms

#### Step 3: Configure .env

```bash
# Enable local models
USE_LOCAL_MODELS_ONLY=true

# Model paths
LLAMA3_MODEL_PATH=models/llama3-8b-instruct
MIXTRAL_MODEL_PATH=models/mixtral-8x7b-instruct

# Use 4-bit quantization (saves memory)
MODEL_QUANTIZATION=4bit

# Enable GPU if available
USE_GPU=true  # or false for CPU only
```

### Available Models

| Model | Size | RAM Needed | Quality | Speed (GPU) | Speed (CPU) |
|-------|------|------------|---------|-------------|-------------|
| Llama 3 8B | 16 GB | 6 GB (4-bit) | ⭐⭐⭐⭐ | Fast | Slow |
| Llama 3 70B | 140 GB | 40 GB (4-bit) | ⭐⭐⭐⭐⭐ | Medium | Very Slow |
| Mixtral 8x7B | 47 GB | 24 GB (4-bit) | ⭐⭐⭐⭐⭐ | Medium | Very Slow |
| Mistral 7B | 14 GB | 4 GB (4-bit) | ⭐⭐⭐⭐ | Fast | Slow |

### Example Usage

```python
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# Load model (4-bit quantization)
model_id = "models/llama3-8b-instruct"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.float16,
    load_in_4bit=True,
    device_map="auto"
)

# Generate response
messages = [{"role": "user", "content": "What is tort law?"}]
inputs = tokenizer.apply_chat_template(messages, return_tensors="pt")
outputs = model.generate(inputs, max_new_tokens=256)
print(tokenizer.decode(outputs[0]))
```

### Pros & Cons

**Pros:**
- Completely free
- Unlimited requests
- 100% private/offline
- No rate limits
- No dependency on external services

**Cons:**
- Requires powerful hardware
- Slow on CPU
- Large download sizes (16-140 GB per model)
- More complex setup

---

## 🆓 Free Embeddings (for Vector Search)

### Option 1: Local Sentence Transformers (RECOMMENDED)

**Model:** `sentence-transformers/all-MiniLM-L6-v2`
- **Size:** 90 MB (auto-downloads)
- **Dimension:** 384
- **Speed:** Very fast
- **Quality:** Good for legal text

**Configuration:**
```bash
EMBEDDING_MODEL=local
```

### Option 2: Better Quality Local

**Model:** `sentence-transformers/all-mpnet-base-v2`
- **Size:** 420 MB
- **Dimension:** 768
- **Speed:** Medium
- **Quality:** Better

### Option 3: HuggingFace API

**Model:** Any sentence-transformers model via API
- **Requires:** `HUGGINGFACE_API_KEY`
- **Counts against:** 30K monthly limit

**Configuration:**
```bash
EMBEDDING_MODEL=huggingface
HUGGINGFACE_API_KEY=hf_...
```

---

## 💡 Recommended FREE Setup

### For Best Experience (Free)

```bash
# AI Inference
GROQ_API_KEY=gsk_...  # Primary (fast, free)
HUGGINGFACE_API_KEY=hf_...  # Backup

# Database
SUPABASE_URL=https://...
SUPABASE_KEY=...

# Vector Storage (local, free)
VECTOR_STORE_TYPE=faiss

# Embeddings (local, free)
EMBEDDING_MODEL=local

# Model Routing
MODEL_ROUTING_STRATEGY=cost_optimized
MODEL_FALLBACK_ENABLED=true
```

### For Offline/Private Use

```bash
# Use local models only
USE_LOCAL_MODELS_ONLY=true

# Local model paths
LLAMA3_MODEL_PATH=models/llama3-8b-instruct
MODEL_QUANTIZATION=4bit

# Local vector storage
VECTOR_STORE_TYPE=faiss

# Local embeddings
EMBEDDING_MODEL=local

# Local database (instead of Supabase)
DATABASE_URL=postgresql://localhost/legal_ai
```

---

## 📊 Cost Comparison (Monthly)

| Setup | Cost/Month | Requests/Month | Best For |
|-------|------------|----------------|----------|
| **Groq Only** | $0 | 432,000 | High volume, free |
| **HuggingFace Only** | $0 | 30,000 | Low volume, free |
| **Local Only** | $0 | Unlimited | Privacy, offline |
| **Groq + HuggingFace** | $0 | 462,000 | Maximum free |
| OpenAI GPT-4 | ~$100 | ~10,000 | Best quality |
| Anthropic Claude | ~$100 | ~10,000 | Long contexts |

---

## 🎯 Which Option Should You Choose?

### Choose Groq if:
- ✅ You want the best free experience
- ✅ You need fast responses
- ✅ You can work within 14,400 requests/day

### Choose HuggingFace if:
- ✅ You need variety of models
- ✅ You want to experiment
- ✅ Speed is not critical

### Choose Local Models if:
- ✅ You need complete privacy
- ✅ You work offline
- ✅ You have powerful hardware (GPU)
- ✅ You need unlimited requests

### Use Combination:
**Best approach:**
1. **Primary:** Groq (fast, free)
2. **Backup:** HuggingFace (when Groq limit hit)
3. **Fallback:** Local models (offline/privacy)

Configure in .env:
```bash
# Enable all three
GROQ_API_KEY=gsk_...
HUGGINGFACE_API_KEY=hf_...
LLAMA3_MODEL_PATH=models/llama3-8b-instruct

# Let the system choose
MODEL_ROUTING_STRATEGY=cost_optimized
MODEL_FALLBACK_ENABLED=true
```

---

## 🔍 What is Vector Storage?

### Simple Explanation

**Vector storage** converts text into numbers (vectors) so you can find similar documents using math instead of keywords.

### Example

**Traditional keyword search:**
- Query: "contract dispute"
- Finds: Only documents with exact words "contract" and "dispute"

**Vector search:**
- Query: "contract dispute"
- Finds: Documents about "breach of agreement", "contractual disagreement", "violation of terms"
- **Why?** These phrases have similar *meaning* (similar vectors)

### How It Works

1. **Text → Vector:** "This is a law" → `[0.23, -0.41, 0.67, ...]` (1536 numbers)
2. **Store vectors:** Save in database alongside text
3. **Search:** Convert query → vector, find most similar vectors
4. **Return:** Get original text from similar vectors

### Why You Need It

For legal AI:
- Find relevant laws even if wording differs
- Match cases by legal concepts, not keywords
- Discover precedents with similar reasoning
- Semantic search across millions of documents

### Free Options

All vector storage options below are **completely FREE**:

#### 1. FAISS (Default - FREE, Local)
- **Cost:** Free
- **Storage:** Local files
- **Best for:** Small-medium datasets
- **Setup:** None (just works)

#### 2. ChromaDB (FREE, Local)
- **Cost:** Free
- **Storage:** Local files
- **Best for:** Medium datasets with metadata
- **Setup:** None (just works)

#### 3. Qdrant (FREE Cloud)
- **Cost:** Free (1 GB)
- **Storage:** Cloud
- **Best for:** Sharing across devices
- **Setup:** Sign up at https://cloud.qdrant.io/

---

## 🚀 Quick Start with FREE Setup

### 1. Get Free API Keys (5 minutes)

```bash
# Groq (FASTEST)
# 1. Go to: https://console.groq.com/
# 2. Sign up with Google/GitHub
# 3. Get API key

# HuggingFace (BACKUP)
# 1. Go to: https://huggingface.co/settings/tokens
# 2. Create token
```

### 2. Get Supabase (2 minutes)

```bash
# 1. Go to: https://supabase.com/
# 2. Create project (free tier)
# 3. Get URL and key
```

### 3. Configure .env

```bash
# Copy template
cp .env.example .env

# Edit .env and add:
GROQ_API_KEY=gsk_...
HUGGINGFACE_API_KEY=hf_...
SUPABASE_URL=https://...
SUPABASE_KEY=...

# Use defaults for everything else (all free)
```

### 4. Run Setup

```bash
bash scripts/setup_environment.sh
```

### 5. Start Using!

```bash
# Start API
uvicorn src.api.main:app --reload

# Test query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is habeas corpus?"}'
```

**Total cost: $0** 🎉

---

## 📚 Additional Resources

- [Complete Setup Guide](SETUP_GUIDE.md) - Detailed setup instructions
- [API Documentation](API.md) - API usage guide
- [Groq Documentation](https://console.groq.com/docs) - Groq API docs
- [HuggingFace Docs](https://huggingface.co/docs/api-inference/) - HF API docs

---

**Questions?** Open an issue on GitHub or check the setup guide!
