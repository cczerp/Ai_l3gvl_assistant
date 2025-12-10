# 5-Model Consensus System Setup Guide

## 🎯 Overview

Your Legal-AI Assistant now uses a **5-model consensus and verification system** for maximum accuracy:

### Primary Models (3) - Generate Responses
1. **GPT-4** (OpenAI) - Complex legal reasoning
2. **Claude Opus** (Anthropic) - Nuanced interpretation
3. **Gemini Pro** (Google) - Cross-domain analysis

### Verification Models (2) - Check for Errors
4. **Llama-3-70b** (Groq) - Fast verification (FREE!)
5. **Mixtral-8x7B** (HuggingFace) - Fact-checking (FREE!)

---

## 📋 Setup Steps

### 1. Install Gemini Package

```bash
pip install google-generativeai==0.3.2
```

Or if you're reinstalling everything:

```bash
git pull
pip install -r requirements.txt
```

### 2. Get Your API Keys

You mentioned you already have:
- ✅ OpenAI API key
- ✅ Claude API key
- ✅ Groq API key
- ✅ HuggingFace API key
- ✅ Gemini API key

If you need a Gemini key:
1. Go to https://makersuite.google.com/app/apikey
2. Click "Create API key"
3. Select a project or create new
4. Copy the key
5. **Free tier**: 60 requests/minute!

### 3. Configure Your `.env` File

```bash
# ========================================
# PRIMARY MODELS (3 models for main work)
# ========================================
OPENAI_API_KEY=sk-proj-xxxxx              # GPT-4
ANTHROPIC_API_KEY=sk-ant-xxxxx            # Claude Opus
GOOGLE_API_KEY=xxxxx                       # Gemini Pro

# ========================================
# VERIFICATION MODELS (2 models to check work)
# ========================================
GROQ_API_KEY=gsk_xxxxx                     # Llama-3-70b (FREE!)
HUGGINGFACE_API_KEY=hf_xxxxx              # Mixtral (FREE!)

# ========================================
# DATABASE (Supabase)
# ========================================
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=<your secret key>

# ========================================
# CONSENSUS SETTINGS
# ========================================
ENABLE_CONSENSUS_MODE=true
MIN_CONSENSUS_CONFIDENCE=0.6               # Require 60% confidence minimum
REQUIRE_VERIFICATION=true                  # Always use verification models
AUTO_FLAG_LOW_CONFIDENCE=true              # Flag for human review if < 60%

# ========================================
# VECTOR STORE & EMBEDDINGS
# ========================================
VECTOR_STORE_TYPE=faiss                    # Local vector store (or use Supabase)
EMBEDDING_MODEL=local                      # Free local embeddings

# ========================================
# API SETTINGS
# ========================================
API_SECRET_KEY=<run: python -c "import secrets; print(secrets.token_hex(32))">
```

### 4. Test Individual Models

Create a test script to verify each model works:

```python
# test_models.py
import asyncio
import os
from dotenv import load_dotenv
from src.models import (
    OpenAIModel,
    AnthropicModel,
    GeminiModel,
    GroqModel,
    HuggingFaceModel
)

load_dotenv()

async def test_all_models():
    """Test all 5 models."""

    test_prompt = "What is a contract?"

    # Test GPT-4
    print("Testing GPT-4...")
    gpt4 = OpenAIModel()
    response = await gpt4.generate(test_prompt)
    print(f"✅ GPT-4: {response.content[:100]}...")

    # Test Claude
    print("\nTesting Claude...")
    claude = AnthropicModel()
    response = await claude.generate(test_prompt)
    print(f"✅ Claude: {response.content[:100]}...")

    # Test Gemini
    print("\nTesting Gemini...")
    gemini = GeminiModel()
    response = await gemini.generate(test_prompt)
    print(f"✅ Gemini: {response.content[:100]}...")

    # Test Groq
    print("\nTesting Groq...")
    groq = GroqModel()
    response = await groq.generate(test_prompt)
    print(f"✅ Groq: {response.content[:100]}...")

    # Test HuggingFace
    print("\nTesting HuggingFace...")
    hf = HuggingFaceModel()
    response = await hf.generate(test_prompt)
    print(f"✅ HuggingFace: {response.content[:100]}...")

    print("\n🎉 All models working!")

if __name__ == "__main__":
    asyncio.run(test_all_models())
```

Run it:
```bash
python test_models.py
```

---

## 🚀 Using the Consensus System

### Basic Usage

```python
import asyncio
from src.router.consensus_router import ConsensusRouter

async def main():
    router = ConsensusRouter()

    result = await router.get_consensus(
        query="What are the elements of a valid contract?",
        context="Legal query about contract law",
        use_verification=True,
        min_confidence=0.6
    )

    print(f"Response: {result.final_response}")
    print(f"Confidence: {result.confidence_score:.2f}")
    print(f"Agreement: {result.agreement_level}")
    print(f"Requires Review: {result.requires_human_review}")

    if result.discrepancies:
        print(f"Discrepancies found: {result.discrepancies}")

    if result.verification_notes:
        print(f"Verification notes: {result.verification_notes}")

asyncio.run(main())
```

### Response Structure

```python
ConsensusResult(
    final_response="...",              # The consensus answer
    confidence_score=0.85,              # 0.0 to 1.0
    agreement_level="strong",           # unanimous, strong, moderate, weak, conflicting
    model_responses=[...],              # Individual model responses
    verification_notes=[...],           # Notes from verification models
    discrepancies=[...],                # Identified contradictions
    requires_human_review=False,        # Flag for manual review
    citations=[...]                     # Aggregated citations
)
```

### Agreement Levels

- **Unanimous** (100%): All models agree perfectly ✅
- **Strong** (80%+): High confidence, minor variations 💪
- **Moderate** (60-80%): Good confidence, some differences ⚠️
- **Weak** (40-60%): Low confidence, significant differences ⚠️⚠️
- **Conflicting** (<40%): Models disagree, requires human review 🚨

---

## 💰 Cost Analysis

### Per Query Cost (Estimated)

**Primary Models:**
- GPT-4: ~$0.03-0.06
- Claude Opus: ~$0.04-0.08
- Gemini Pro: ~$0.001-0.003

**Verification Models:**
- Groq: **FREE** ✅
- HuggingFace: **FREE** ✅

**Total per consensus query: ~$0.07-0.14**

### Cost Optimization Tips

1. **Use verification selectively:**
   ```python
   use_verification = confidence < 0.8  # Only for uncertain queries
   ```

2. **Skip verification for simple queries:**
   ```python
   if query_complexity == "simple":
       use_verification = False
   ```

3. **Cache responses:**
   Enable caching in `.env`:
   ```bash
   CACHE_ENABLED=true
   CACHE_TTL=3600  # 1 hour
   ```

---

## 🔧 Advanced Configuration

### Custom Model Selection

```python
router = ConsensusRouter(config={
    'primary_models': [
        {'name': 'gpt-4', 'provider': 'openai', 'weight': 1.5},
        {'name': 'claude-opus', 'provider': 'anthropic', 'weight': 1.2},
    ],
    'verification_models': [
        {'name': 'llama-3-70b', 'provider': 'groq'},
    ],
    'unanimous_threshold': 0.95,
    'human_review_threshold': 0.7,
})
```

### Confidence Thresholds

Adjust thresholds based on your needs:

```python
# High-stakes legal analysis (more conservative)
router = ConsensusRouter(config={
    'human_review_threshold': 0.80,  # Flag below 80%
    'unanimous_threshold': 0.95,      # Require 95% agreement
})

# Quick legal research (more permissive)
router = ConsensusRouter(config={
    'human_review_threshold': 0.50,  # Flag below 50%
    'unanimous_threshold': 0.85,      # 85% agreement OK
})
```

---

## 📊 Monitoring and Logging

### Enable Detailed Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# See all model calls and consensus analysis
logger = logging.getLogger('src.router.consensus_router')
logger.setLevel(logging.DEBUG)
```

### Track Costs

```python
result = await router.get_consensus(query="...")

total_cost = sum(r.cost for r in result.model_responses)
print(f"Total cost: ${total_cost:.4f}")
```

---

## 🎯 Best Practices

### 1. Use Verification for Critical Queries

```python
# Always verify for legal opinions, contracts, litigation
if query_type in ['legal_opinion', 'contract_review', 'litigation']:
    use_verification = True
    min_confidence = 0.80
```

### 2. Flag Low-Confidence Results

```python
if result.confidence_score < 0.6 or result.agreement_level == 'conflicting':
    print("⚠️  Low confidence - requires human review")
    send_to_human_review(result)
```

### 3. Log Discrepancies

```python
if result.discrepancies:
    logger.warning(f"Discrepancies found: {result.discrepancies}")
    save_for_review(query, result)
```

### 4. Use RAG with Consensus

```python
# Get relevant documents first
from src.rag.retrieval import retrieve_documents

docs = await retrieve_documents(query, top_k=5)
context = "\n\n".join([d.content for d in docs])

# Then use consensus with context
result = await router.get_consensus(
    query=query,
    context=context,  # Provide retrieved documents
    use_verification=True
)
```

---

## 🚨 Troubleshooting

### Model Not Responding

Check API keys:
```bash
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('OpenAI:', 'SET' if os.getenv('OPENAI_API_KEY') else 'NOT SET')"
```

### Rate Limit Errors

- **Groq**: 10 requests/minute (free tier)
- **HuggingFace**: 30,000 requests/month (free tier)
- **Gemini**: 60 requests/minute (free tier)

Add delays between requests:
```python
import asyncio
await asyncio.sleep(6)  # Wait 6 seconds between Groq requests
```

### Model Loading (HuggingFace)

HuggingFace models may take 20-30 seconds to load on first request. The code automatically waits and retries.

---

## 📚 Next Steps

1. ✅ Install packages: `pip install -r requirements.txt`
2. ✅ Configure `.env` with all API keys
3. ✅ Test individual models: `python test_models.py`
4. ✅ Set up Supabase database (run `scripts/supabase_schema.sql`)
5. ✅ Test consensus system with simple query
6. ✅ Integrate with RAG for full legal research
7. ✅ Start API server: `uvicorn src.api.main:app --reload`

---

**Questions?** Check the main documentation or open an issue on GitHub.

**Ready to build a bulletproof legal AI system!** 🚀⚖️
