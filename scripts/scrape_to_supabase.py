#!/usr/bin/env python3
"""
Scrape state laws and upload directly to Supabase.

Usage:
    # Test with one state
    python scripts/scrape_to_supabase.py --state CA --test

    # Scrape and upload full state
    python scripts/scrape_to_supabase.py --state CA

    # Scrape multiple states
    python scripts/scrape_to_supabase.py --states CA,NY,TX

    # Skip existing statutes (don't re-upload)
    python scripts/scrape_to_supabase.py --state CA --skip-existing
"""

import asyncio
import argparse
import logging
import sys
from pathlib import Path
from typing import List, Dict, Any

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.scrapers import JustiaScraper, ScraperConfig
from src.scrapers.base_scraper import US_STATES
from src.database import get_supabase_client

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Scrape state laws and upload to Supabase",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    state_group = parser.add_mutually_exclusive_group(required=True)
    state_group.add_argument('--state', type=str, help='Single state code (e.g., CA)')
    state_group.add_argument('--states', type=str, help='Comma-separated state codes')

    parser.add_argument('--test', action='store_true', help='Test mode (few statutes)')
    parser.add_argument('--max-statutes', type=int, default=5, help='Max in test mode')
    parser.add_argument('--skip-existing', action='store_true', help='Skip duplicates')
    parser.add_argument('--batch-size', type=int, default=50, help='Upload batch size')
    parser.add_argument('--rate-limit', type=float, default=1.0, help='Request delay')
    parser.add_argument('--cache-dir', type=str, help='Cache directory')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose logging')

    return parser.parse_args()


async def scrape_and_upload_state(
    state_code: str,
    scraper: JustiaScraper,
    supabase,
    skip_existing: bool = False,
    batch_size: int = 50,
    test_mode: bool = False,
    max_statutes: int = 5
) -> Dict[str, int]:
    """
    Scrape a state and upload to Supabase.

    Returns:
        Stats dictionary
    """
    stats = {
        "scraped": 0,
        "uploaded": 0,
        "skipped": 0,
        "failed": 0
    }

    try:
        logger.info(f"📥 Scraping {state_code} - {US_STATES.get(state_code)}...")

        # Scrape
        if test_mode:
            statutes = await scraper.scrape_state(
                state_code,
                max_statutes=max_statutes,
                sample_mode=True
            )
        else:
            statutes = await scraper.scrape_state(state_code)

        stats["scraped"] = len(statutes)
        logger.info(f"✓ Scraped {len(statutes)} statutes from {state_code}")

        if not statutes:
            logger.warning(f"No statutes found for {state_code}")
            return stats

        # Filter out existing if requested
        if skip_existing:
            filtered_statutes = []
            for statute in statutes:
                statute_dict = statute.to_dict()
                exists = await supabase.check_duplicate_statute(
                    statute_dict["state"],
                    statute_dict["statute_number"]
                )

                if exists:
                    stats["skipped"] += 1
                else:
                    filtered_statutes.append(statute_dict)

            logger.info(
                f"Filtered: {len(filtered_statutes)} new, "
                f"{stats['skipped']} existing"
            )
            statute_dicts = filtered_statutes
        else:
            statute_dicts = [s.to_dict() for s in statutes]

        # Upload in batches
        if statute_dicts:
            logger.info(f"📤 Uploading {len(statute_dicts)} statutes to Supabase...")

            uploaded = await supabase.insert_state_laws_batch(
                statute_dicts,
                batch_size=batch_size
            )

            stats["uploaded"] = uploaded
            stats["failed"] = len(statute_dicts) - uploaded

            logger.info(
                f"✓ {state_code}: Uploaded {uploaded}/{len(statute_dicts)} statutes"
            )

    except Exception as e:
        logger.error(f"✗ {state_code}: Failed - {str(e)}")
        stats["failed"] = stats["scraped"]

    return stats


async def main():
    """Main entry point."""
    args = parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Parse state codes
    if args.state:
        state_codes = [args.state.upper()]
    else:
        state_codes = [s.strip().upper() for s in args.states.split(',')]

    # Validate
    invalid = [s for s in state_codes if s not in US_STATES]
    if invalid:
        logger.error(f"Invalid state codes: {', '.join(invalid)}")
        sys.exit(1)

    logger.info(f"🚀 Starting scrape-to-Supabase for: {', '.join(state_codes)}")

    if not args.test:
        logger.warning(
            "⚠️  Running in PRODUCTION mode - will scrape ALL statutes!"
        )
        logger.warning("Use --test for testing with limited data")

    # Initialize
    try:
        supabase = get_supabase_client()
        logger.info("✓ Connected to Supabase")
    except Exception as e:
        logger.error(f"✗ Failed to connect to Supabase: {str(e)}")
        logger.error("Make sure SUPABASE_URL and SUPABASE_KEY are set in .env")
        sys.exit(1)

    # Create scraper
    config = ScraperConfig(
        rate_limit_delay=args.rate_limit,
        cache_dir=Path(args.cache_dir) if args.cache_dir else None
    )

    overall_stats = {
        "total_scraped": 0,
        "total_uploaded": 0,
        "total_skipped": 0,
        "total_failed": 0
    }

    async with JustiaScraper(config) as scraper:
        for state_code in state_codes:
            logger.info(f"\n{'='*60}")
            logger.info(f"Processing: {state_code}")
            logger.info(f"{'='*60}\n")

            stats = await scrape_and_upload_state(
                state_code,
                scraper,
                supabase,
                skip_existing=args.skip_existing,
                batch_size=args.batch_size,
                test_mode=args.test,
                max_statutes=args.max_statutes
            )

            overall_stats["total_scraped"] += stats["scraped"]
            overall_stats["total_uploaded"] += stats["uploaded"]
            overall_stats["total_skipped"] += stats["skipped"]
            overall_stats["total_failed"] += stats["failed"]

    # Final summary
    logger.info(f"\n{'='*60}")
    logger.info("FINAL SUMMARY")
    logger.info(f"{'='*60}")
    logger.info(f"States processed: {len(state_codes)}")
    logger.info(f"Total scraped: {overall_stats['total_scraped']}")
    logger.info(f"Total uploaded: {overall_stats['total_uploaded']}")
    logger.info(f"Total skipped: {overall_stats['total_skipped']}")
    logger.info(f"Total failed: {overall_stats['total_failed']}")
    logger.info(f"{'='*60}\n")

    # Get database stats
    try:
        db_stats = await supabase.get_stats()
        logger.info("📊 Database Statistics:")
        for table, count in db_stats.items():
            logger.info(f"  {table}: {count:,} records")
    except Exception as e:
        logger.warning(f"Could not fetch database stats: {str(e)}")

    logger.info("\n✅ Complete!")


if __name__ == '__main__':
    asyncio.run(main())
