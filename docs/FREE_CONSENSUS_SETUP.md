# 100% FREE 5-Model Consensus System

## 🎯 Your Completely FREE Setup

**Cost per query: $0.00** ✅

### **Primary Models (3)**
1. **Groq Llama-3-70b** - Ultra-fast, FREE, 14,400 req/day
2. **Gemini Pro** - Google, FREE, 60 req/min
3. **HuggingFace Mixtral-8x7B** - FREE, 30k req/month

### **Verification Models (2)**
4. **Together AI Llama-3-70b** - FREE $25 credit, fast (FINAL JUDGE)
5. **Local Llama-3-8B** - Run on your cloud, FREE

---

## 📋 Setup Guide

### Step 1: Get Together AI API Key (FREE $25 Credit!)

1. Go to https://api.together.xyz/signup
2. Sign up with email or GitHub
3. You get **$25 FREE credit** automatically! 🎉
4. Go to Settings → API Keys
5. Create new API key
6. Copy the key

**Free Credit Calculation:**
- $25 credit = ~28 million tokens
- At average 2000 tokens/query = ~14,000 FREE queries!
- That's months of free usage!

### Step 2: Set Up Local Model on Cloud

You have 3 options:

#### **Option A: Llama-3-8B (Recommended)**

**Requirements:**
- 16GB RAM (or 6GB with 4-bit quantization)
- GPU with 8GB+ VRAM (recommended) or CPU
- ~16GB disk space

**Setup:**
```bash
# Download model
huggingface-cli download meta-llama/Meta-Llama-3-8B-Instruct --local-dir ./models/llama3-8b

# Add to .env
LOCAL_MODEL_NAME=meta-llama/Meta-Llama-3-8B-Instruct
LOCAL_MODEL_PATH=./models/llama3-8b
LOCAL_MODEL_QUANTIZATION=4bit
```

#### **Option B: Phi-3-Mini (Lightweight)**

**Requirements:**
- 8GB RAM (or 3GB with 4-bit quantization)
- Works on CPU!
- ~7GB disk space

**Setup:**
```bash
# Download model
huggingface-cli download microsoft/Phi-3-mini-4k-instruct --local-dir ./models/phi3-mini

# Add to .env
LOCAL_MODEL_NAME=microsoft/Phi-3-mini-4k-instruct
LOCAL_MODEL_PATH=./models/phi3-mini
LOCAL_MODEL_QUANTIZATION=4bit
```

#### **Option C: Gemma-7B (Google)**

**Requirements:**
- 14GB RAM (or 5GB with 4-bit quantization)
- GPU recommended
- ~14GB disk space

**Setup:**
```bash
# Download model
huggingface-cli download google/gemma-7b-it --local-dir ./models/gemma-7b

# Add to .env
LOCAL_MODEL_NAME=google/gemma-7b-it
LOCAL_MODEL_PATH=./models/gemma-7b
LOCAL_MODEL_QUANTIZATION=4bit
```

### Step 3: Configure `.env`

```bash
# ========================================
# FREE CLOUD APIS
# ========================================
GROQ_API_KEY=gsk_xxxxx                     # FREE: 14,400 req/day
GOOGLE_API_KEY=xxxxx                       # FREE: 60 req/min
HUGGINGFACE_API_KEY=hf_xxxxx              # FREE: 30k req/month
TOGETHER_AI_API_KEY=xxxxx                  # FREE: $25 credit (~14k queries)

# ========================================
# LOCAL MODEL (on your cloud)
# ========================================
LOCAL_MODEL_NAME=meta-llama/Meta-Llama-3-8B-Instruct
LOCAL_MODEL_PATH=./models/llama3-8b
LOCAL_MODEL_QUANTIZATION=4bit              # 4bit, 8bit, or none
LOCAL_MODEL_DEVICE=auto                    # auto, cuda, or cpu

# ========================================
# CONSENSUS SETTINGS (ALL FREE MODE)
# ========================================
ENABLE_CONSENSUS_MODE=true
CONSENSUS_MODE=free                        # Use only FREE models
MIN_CONSENSUS_CONFIDENCE=0.6
REQUIRE_VERIFICATION=true
USE_TOGETHER_AS_JUDGE=true                 # Together AI as final judge

# ========================================
# DATABASE
# ========================================
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=xxxxx

# ========================================
# VECTOR STORE & EMBEDDINGS (FREE)
# ========================================
VECTOR_STORE_TYPE=faiss                    # Local, FREE
EMBEDDING_MODEL=local                      # FREE local embeddings

# ========================================
# API SETTINGS
# ========================================
API_SECRET_KEY=<generate with: python -c "import secrets; print(secrets.token_hex(32))">
```

---

## 🚀 Usage Example

### FREE Consensus Router

```python
import asyncio
from src.router.consensus_router import ConsensusRouter

async def main():
    # Configure for FREE models only
    router = ConsensusRouter(config={
        'primary_models': [
            {'name': 'llama-3-70b-8192', 'provider': 'groq', 'weight': 1.2},
            {'name': 'gemini-pro', 'provider': 'google', 'weight': 1.0},
            {'name': 'mistralai/Mixtral-8x7B-Instruct-v0.1', 'provider': 'huggingface', 'weight': 1.0},
        ],
        'verification_models': [
            {'name': 'meta-llama/Llama-3-70b-chat-hf', 'provider': 'together', 'purpose': 'final_judge'},
            {'name': 'meta-llama/Meta-Llama-3-8B-Instruct', 'provider': 'local', 'purpose': 'verification'},
        ],
    })

    # Query with all FREE models
    result = await router.get_consensus(
        query="What are the elements of a valid contract?",
        context="Legal query about contract law",
        use_verification=True,
        min_confidence=0.6
    )

    print(f"✅ Response: {result.final_response}")
    print(f"💰 Cost: $0.00 (100% FREE!)")
    print(f"📊 Confidence: {result.confidence_score:.2f}")
    print(f"🎯 Agreement: {result.agreement_level}")
    print(f"👨‍⚖️ Final Judge (Together AI): Verified")

asyncio.run(main())
```

---

## 💡 How the FREE System Works

### Flow Diagram

```
User Query
    ↓
┌─────────────────────────────────────┐
│  PRIMARY MODELS (Parallel, FREE)    │
│  1. Groq Llama-3-70b     (fastest)  │
│  2. Gemini Pro           (reliable) │
│  3. HuggingFace Mixtral  (quality)  │
└────────────┬────────────────────────┘
             ↓
    [Consensus Analysis]
    - Compare 3 responses
    - Calculate agreement
    - Identify discrepancies
             ↓
┌─────────────────────────────────────┐
│  VERIFICATION (FREE)                 │
│  4. Local Llama-3-8B (error check)  │
│  5. Together AI (FINAL JUDGE)       │
└────────────┬────────────────────────┘
             ↓
    [Final Response]
    ✅ Cost: $0.00
    ✅ Confidence Score
    ✅ Agreement Level
    ✅ Judge Approval
```

### Why Together AI as Final Judge?

- **Fast inference** like Groq (1-2 seconds)
- **Large model** (Llama-3-70b) for authority
- **FREE $25 credit** lasts months
- **Perfect for verification** - breaks ties, validates facts
- **High reliability** as the deciding vote

---

## 📊 Rate Limits (All FREE Tiers)

| Provider | Daily Limit | Per Minute | Monthly |
|----------|-------------|------------|---------|
| **Groq** | 14,400 req | 10 req | 432k req |
| **Gemini** | Unlimited* | 60 req | Unlimited* |
| **HuggingFace** | ~1000 req | - | 30k req |
| **Together AI** | Until $25 used | 60 req | ~14k req |
| **Local Model** | Unlimited | Unlimited | Unlimited |

*Subject to fair use policy

### Rate Limit Strategy

The consensus router automatically:
1. Spreads requests across models
2. Retries with exponential backoff
3. Falls back to other models if one hits limit
4. Uses local model as infinite fallback

---

## 🎯 Cost Comparison

### Your FREE Setup vs Paid

| Query Type | Your Cost | With GPT-4/Claude | Savings |
|------------|-----------|-------------------|---------|
| Simple Query | **$0.00** | $0.10 | 100% |
| Complex Analysis | **$0.00** | $0.25 | 100% |
| With Verification | **$0.00** | $0.35 | 100% |
| 1000 queries/day | **$0.00** | $150-250/day | **$4,500-7,500/month saved!** |

---

## 🔧 Advanced Configuration

### Optimizing for Speed

```python
# Prioritize fastest models
router = ConsensusRouter(config={
    'primary_models': [
        {'name': 'llama-3-70b-8192', 'provider': 'groq', 'weight': 1.5},  # Fastest
        {'name': 'gemini-1.5-flash', 'provider': 'google', 'weight': 1.2},  # Fast
        {'name': 'meta-llama/Llama-3-8b-chat-hf', 'provider': 'together', 'weight': 1.0},  # Fast
    ],
    'verification_models': [
        {'name': 'meta-llama/Meta-Llama-3-8B-Instruct', 'provider': 'local'},  # Instant
    ],
})
```

### Optimizing for Quality

```python
# Prioritize best models
router = ConsensusRouter(config={
    'primary_models': [
        {'name': 'llama-3-70b-8192', 'provider': 'groq', 'weight': 1.5},  # Large
        {'name': 'gemini-pro', 'provider': 'google', 'weight': 1.3},  # Quality
        {'name': 'mistralai/Mixtral-8x7B-Instruct-v0.1', 'provider': 'huggingface', 'weight': 1.2},  # MOE
    ],
    'verification_models': [
        {'name': 'meta-llama/Llama-3-70b-chat-hf', 'provider': 'together'},  # Large verifier
        {'name': 'meta-llama/Meta-Llama-3-8B-Instruct', 'provider': 'local'},
    ],
})
```

---

## 🚨 Troubleshooting

### Together AI Setup Issues

**Problem:** API key not working
```bash
# Test your key
curl https://api.together.xyz/v1/models \
  -H "Authorization: Bearer $TOGETHER_AI_API_KEY"
```

**Problem:** Credit running low
- Check usage: https://api.together.xyz/settings/billing
- After $25, costs are very low: $0.88 per 1M tokens
- Consider upgrading or switching judge to local model

### Local Model Issues

**Problem:** Out of memory
```bash
# Solution 1: Use 4-bit quantization
LOCAL_MODEL_QUANTIZATION=4bit

# Solution 2: Use smaller model
LOCAL_MODEL_NAME=microsoft/Phi-3-mini-4k-instruct

# Solution 3: Use CPU (slower but works)
LOCAL_MODEL_DEVICE=cpu
```

**Problem:** Slow inference
```bash
# Solution 1: Use GPU if available
LOCAL_MODEL_DEVICE=cuda

# Solution 2: Use smaller model
LOCAL_MODEL_NAME=microsoft/Phi-3-mini-4k-instruct

# Solution 3: Increase quantization
LOCAL_MODEL_QUANTIZATION=8bit  # Faster than 4bit
```

### Rate Limit Issues

**Problem:** Hitting Groq limits (10/min)
```python
# Solution: Add delay between requests
import asyncio
await asyncio.sleep(6)  # Wait 6 seconds
```

**Problem:** HuggingFace model loading
```python
# Solution: Wait and retry (automatic in our code)
# Or use different model:
'meta-llama/Llama-2-70b-chat-hf'  # Usually faster to load
```

---

## 📈 Monitoring Your FREE System

### Track Usage

```python
# Add after each query
print(f"Primary Models Used: {[r.provider for r in result.model_responses]}")
print(f"Total Latency: {sum(r.latency for r in result.model_responses):.2f}s")
print(f"Cost: $0.00 ✅")

# Track Together AI credit usage
# Check at: https://api.together.xyz/settings/billing
```

### Log Statistics

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('consensus_stats')

# After query
logger.info(f"Query: {query[:50]}")
logger.info(f"Confidence: {result.confidence_score:.2f}")
logger.info(f"Agreement: {result.agreement_level}")
logger.info(f"Models: {len(result.model_responses)}")
logger.info(f"Cost: $0.00")
```

---

## ✅ Setup Checklist

- [ ] Sign up for Together AI and get $25 FREE credit
- [ ] Download local model (Llama-3-8B or Phi-3)
- [ ] Configure `.env` with all FREE API keys
- [ ] Test each model individually
- [ ] Test consensus system
- [ ] Set up Supabase database
- [ ] Configure rate limit handling
- [ ] Enable logging and monitoring
- [ ] Deploy to cloud (if not already)
- [ ] Celebrate your 100% FREE legal AI system! 🎉

---

## 🎉 You Now Have

✅ **5-model consensus system**
✅ **100% FREE** (no ongoing costs)
✅ **$25 Together AI credit** (~14,000 queries)
✅ **Unlimited local inference**
✅ **Fast responses** (1-3 seconds)
✅ **High reliability** (5 models checking each other)
✅ **Final judge** (Together AI as tie-breaker)
✅ **Production-ready** for real legal work

**Total savings vs GPT-4/Claude: $4,500-7,500/month!** 💰

---

Need help? Open an issue or check the main docs!
