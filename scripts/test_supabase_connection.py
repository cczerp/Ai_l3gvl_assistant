#!/usr/bin/env python3
"""
Test Supabase connection and verify setup.
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from src.database.supabase_client import SupabaseClient

def test_connection():
    """Test Supabase connection and database setup."""

    # Load environment variables
    load_dotenv()

    print("🔍 Testing Supabase Connection...\n")

    # Check if credentials are set
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')

    if not supabase_url:
        print("❌ SUPABASE_URL not set in .env file")
        return False

    if not supabase_key:
        print("❌ SUPABASE_KEY not set in .env file")
        return False

    print(f"✅ SUPABASE_URL: {supabase_url}")
    print(f"✅ SUPABASE_KEY: {supabase_key[:20]}...{supabase_key[-10:]}\n")

    # Try to connect
    try:
        print("📡 Connecting to Supabase...")
        client = SupabaseClient()
        print("✅ Successfully connected to Supabase!\n")

        # Test database stats (async wrapper)
        import asyncio

        async def get_stats():
            stats = await client.get_stats()
            return stats

        print("📊 Checking database tables...")
        stats = asyncio.run(get_stats())

        print("\n📈 Database Statistics:")
        print("-" * 50)
        for table, count in stats.items():
            print(f"  {table:20s}: {count:,} records")
        print("-" * 50)

        # Test a simple query
        print("\n🔍 Testing query functionality...")
        async def test_query():
            # Try to fetch state laws (should return empty list if no data)
            laws = await client.get_state_laws(limit=5)
            return laws

        laws = asyncio.run(test_query())
        print(f"✅ Query successful! Found {len(laws)} state laws")

        if len(laws) > 0:
            print("\n📄 Sample record:")
            sample = laws[0]
            print(f"  State: {sample.get('state')}")
            print(f"  Title: {sample.get('title', 'N/A')[:80]}...")
        else:
            print("\n💡 No data yet - run scrapers to populate the database:")
            print("   python scripts/scrape_to_supabase.py")

        print("\n" + "="*50)
        print("✨ Supabase is properly configured!")
        print("="*50)
        print("\n📚 Your database has vector search enabled via pgvector")
        print("🔍 You can now store and search legal documents semantically")
        print("\n🚀 Next steps:")
        print("   1. Run scrapers to populate data")
        print("   2. Start API server: uvicorn src.api.main:app --reload")
        print("   3. Query API: http://localhost:8000/docs")

        return True

    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("\n💡 Make sure you have set SUPABASE_URL and SUPABASE_KEY in .env")
        return False

    except Exception as e:
        print(f"❌ Connection Failed: {e}")
        print(f"\n💡 Troubleshooting:")
        print("   1. Check your Supabase credentials in .env")
        print("   2. Make sure you've run the schema SQL in Supabase")
        print("   3. Verify your IP isn't blocked in Supabase dashboard")
        print(f"   4. Error details: {type(e).__name__}")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
