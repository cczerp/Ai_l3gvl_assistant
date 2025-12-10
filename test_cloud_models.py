"""
Quick test for your 4 FREE cloud APIs.
Run this BEFORE downloading the local model to verify everything works.
"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def test_cloud_apis():
    """Test your 4 cloud APIs: Groq, Gemini, HuggingFace, DeepInfra."""

    print("\n" + "="*70)
    print("🧪 TESTING YOUR 4 FREE CLOUD APIS")
    print("="*70)

    test_prompt = "What is a contract? Answer in one sentence."
    results = []

    # Check API keys first
    print("\n📋 Checking API Keys...")
    keys = {
        'GROQ_API_KEY': os.getenv('GROQ_API_KEY'),
        'GOOGLE_API_KEY': os.getenv('GOOGLE_API_KEY'),
        'HUGGINGFACE_API_KEY': os.getenv('HUGGINGFACE_API_KEY'),
        'DEEPINFRA_API': os.getenv('DEEPINFRA_API'),
    }

    for key_name, key_value in keys.items():
        if key_value:
            print(f"   ✅ {key_name}: Set ({key_value[:10]}...)")
        else:
            print(f"   ❌ {key_name}: NOT SET")

    if not all(keys.values()):
        print("\n⚠️  Warning: Some API keys are missing!")
        print("   Add them to your .env file before continuing.\n")
        return

    print("\n" + "-"*70)

    # Test 1: Groq
    print("\n1️⃣  GROQ LLAMA-3-70B")
    print("-"*70)
    try:
        from src.models import GroqModel
        groq = GroqModel(model_name="llama-3-70b-8192")
        print("   🔄 Sending request...")
        response = await groq.generate(test_prompt, max_tokens=100)
        print(f"   ✅ SUCCESS!")
        print(f"   📝 Response: {response.content[:150]}...")
        print(f"   ⚡ Speed: {response.latency:.2f}s")
        print(f"   🎯 Tokens: {response.tokens_used}")
        print(f"   💰 Cost: ${response.cost:.6f} (FREE!)")
        results.append(('Groq', True))
    except Exception as e:
        print(f"   ❌ FAILED: {str(e)[:100]}")
        results.append(('Groq', False))

    # Test 2: Gemini
    print("\n2️⃣  GOOGLE GEMINI PRO")
    print("-"*70)
    try:
        from src.models import GeminiModel
        gemini = GeminiModel()
        print("   🔄 Sending request...")
        response = await gemini.generate(test_prompt, max_tokens=100)
        print(f"   ✅ SUCCESS!")
        print(f"   📝 Response: {response.content[:150]}...")
        print(f"   ⚡ Speed: {response.latency:.2f}s")
        print(f"   🎯 Tokens: {response.tokens_used}")
        print(f"   💰 Cost: ${response.cost:.6f} (FREE!)")
        results.append(('Gemini', True))
    except Exception as e:
        print(f"   ❌ FAILED: {str(e)[:100]}")
        results.append(('Gemini', False))

    # Test 3: HuggingFace
    print("\n3️⃣  HUGGINGFACE MIXTRAL-8X7B")
    print("-"*70)
    try:
        from src.models import HuggingFaceModel
        hf = HuggingFaceModel()
        print("   🔄 Sending request...")
        print("   ⏳ Note: May take 20-30s if model needs to load...")
        response = await hf.generate(test_prompt, max_tokens=100)
        print(f"   ✅ SUCCESS!")
        print(f"   📝 Response: {response.content[:150]}...")
        print(f"   ⚡ Speed: {response.latency:.2f}s")
        print(f"   🎯 Tokens: {response.tokens_used}")
        print(f"   💰 Cost: ${response.cost:.6f} (FREE!)")
        results.append(('HuggingFace', True))
    except Exception as e:
        print(f"   ❌ FAILED: {str(e)[:100]}")
        results.append(('HuggingFace', False))

    # Test 4: DeepInfra (Final Judge)
    print("\n4️⃣  DEEPINFRA LLAMA-3-70B (FINAL JUDGE)")
    print("-"*70)
    try:
        from src.models import DeepInfraModel
        deepinfra = DeepInfraModel()
        print("   🔄 Sending request...")
        response = await deepinfra.generate(test_prompt, max_tokens=100)
        print(f"   ✅ SUCCESS!")
        print(f"   📝 Response: {response.content[:150]}...")
        print(f"   ⚡ Speed: {response.latency:.2f}s")
        print(f"   🎯 Tokens: {response.tokens_used}")
        print(f"   💰 Cost: ${response.cost:.6f} (FREE within 10M tokens/month!)")
        print(f"   ⚖️  Role: FINAL JUDGE")
        results.append(('DeepInfra', True))
    except Exception as e:
        print(f"   ❌ FAILED: {str(e)[:100]}")
        results.append(('DeepInfra', False))

    # Summary
    print("\n" + "="*70)
    print("📊 SUMMARY")
    print("="*70)

    working = [name for name, success in results if success]
    failed = [name for name, success in results if not success]

    for name, success in results:
        status = "✅ Working" if success else "❌ Failed"
        print(f"   {name:15s} {status}")

    print("\n" + "-"*70)

    if len(working) == 4:
        print("🎉 PERFECT! All 4 cloud APIs are working!")
        print("\n✨ Next step: Download local model")
        print("   Run: huggingface-cli download meta-llama/Meta-Llama-3-8B-Instruct --local-dir ./models/llama3-8b")
        print("\n📖 See docs/YOUR_SETUP.md for complete instructions")
    elif len(working) >= 3:
        print("⚠️  3/4 APIs working - Good enough to proceed!")
        print(f"   Failed: {', '.join(failed)}")
        print("\n✨ You can still use the consensus system with 3 primary + 1 verifier")
    else:
        print("❌ Not enough APIs working. Please check:")
        print("   1. API keys are correct in .env")
        print("   2. You have internet connection")
        print("   3. API services are not down")
        print(f"\n   Failed: {', '.join(failed)}")

    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    try:
        asyncio.run(test_cloud_apis())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
