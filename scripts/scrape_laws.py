#!/usr/bin/env python3
"""
CLI tool for scraping state laws.

Usage:
    # Test scrape a single state (5 statutes max)
    python scripts/scrape_laws.py --state CA --test

    # Scrape a single state fully
    python scripts/scrape_laws.py --state CA

    # Scrape multiple states
    python scripts/scrape_laws.py --states CA,NY,TX

    # Scrape all 50 states (takes a long time!)
    python scripts/scrape_laws.py --all

    # Save to JSON file
    python scripts/scrape_laws.py --state CA --output data/scraped/california.json

    # Use cache directory (recommended for testing)
    python scripts/scrape_laws.py --state CA --cache-dir /tmp/scraper_cache
"""

import asyncio
import argparse
import json
import logging
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.scrapers import JustiaScraper, StateCodesScraperFactory, ScraperConfig
from src.scrapers.base_scraper import US_STATES

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Scrape state laws from various sources",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    # State selection
    state_group = parser.add_mutually_exclusive_group(required=True)
    state_group.add_argument(
        '--state',
        type=str,
        help='Single state code to scrape (e.g., CA, NY, TX)'
    )
    state_group.add_argument(
        '--states',
        type=str,
        help='Comma-separated list of state codes (e.g., CA,NY,TX)'
    )
    state_group.add_argument(
        '--all',
        action='store_true',
        help='Scrape all 50 states (WARNING: Takes a long time!)'
    )

    # Scraper options
    parser.add_argument(
        '--test',
        action='store_true',
        help='Test mode: only scrape a few statutes per state'
    )
    parser.add_argument(
        '--max-statutes',
        type=int,
        default=5,
        help='Maximum statutes to scrape in test mode (default: 5)'
    )
    parser.add_argument(
        '--source',
        choices=['justia', 'auto'],
        default='auto',
        help='Scraping source (default: auto - uses best available)'
    )

    # Configuration
    parser.add_argument(
        '--rate-limit',
        type=float,
        default=1.0,
        help='Delay between requests in seconds (default: 1.0)'
    )
    parser.add_argument(
        '--max-concurrent',
        type=int,
        default=3,
        help='Maximum concurrent requests (default: 3)'
    )
    parser.add_argument(
        '--timeout',
        type=int,
        default=30,
        help='Request timeout in seconds (default: 30)'
    )
    parser.add_argument(
        '--cache-dir',
        type=str,
        help='Directory to cache scraped pages'
    )

    # Output options
    parser.add_argument(
        '--output',
        type=str,
        help='Output JSON file path (default: print to stdout)'
    )
    parser.add_argument(
        '--pretty',
        action='store_true',
        help='Pretty-print JSON output'
    )
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Verbose logging'
    )

    return parser.parse_args()


async def scrape_states(
    state_codes: List[str],
    config: ScraperConfig,
    test_mode: bool = False,
    max_statutes: int = 5,
    use_justia: bool = False
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Scrape multiple states.

    Args:
        state_codes: List of state codes to scrape
        config: Scraper configuration
        test_mode: If True, only scrape a few statutes
        max_statutes: Max statutes in test mode
        use_justia: Force use of Justia scraper

    Returns:
        Dictionary mapping state codes to lists of statute dicts
    """
    results = {}

    for state_code in state_codes:
        logger.info(f"\n{'='*60}")
        logger.info(f"Scraping {state_code} - {US_STATES.get(state_code, 'Unknown')}")
        logger.info(f"{'='*60}\n")

        try:
            # Get appropriate scraper
            if use_justia:
                scraper = JustiaScraper(config)
            else:
                scraper = StateCodesScraperFactory.get_scraper(state_code, config)

            async with scraper:
                if test_mode:
                    statutes = await scraper.scrape_state(
                        state_code,
                        max_statutes=max_statutes,
                        sample_mode=True
                    )
                else:
                    statutes = await scraper.scrape_state(state_code)

                # Convert to dicts
                results[state_code] = [s.to_dict() for s in statutes]

                logger.info(f"✓ {state_code}: {len(statutes)} statutes scraped")

        except Exception as e:
            logger.error(f"✗ {state_code}: Failed - {str(e)}")
            results[state_code] = []

    return results


def main():
    """Main entry point."""
    args = parse_args()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Determine which states to scrape
    state_codes = []
    if args.state:
        state_codes = [args.state.upper()]
    elif args.states:
        state_codes = [s.strip().upper() for s in args.states.split(',')]
    elif args.all:
        state_codes = list(US_STATES.keys())

    # Validate state codes
    invalid_states = [s for s in state_codes if s not in US_STATES]
    if invalid_states:
        logger.error(f"Invalid state codes: {', '.join(invalid_states)}")
        logger.info(f"Valid codes: {', '.join(sorted(US_STATES.keys()))}")
        sys.exit(1)

    logger.info(f"Will scrape {len(state_codes)} state(s): {', '.join(state_codes)}")

    if args.all and not args.test:
        logger.warning(
            "\n⚠️  WARNING: Scraping all 50 states will take HOURS and make "
            "thousands of requests.\n"
            "Consider using --test mode first, or scraping specific states.\n"
        )
        response = input("Continue? [y/N] ")
        if response.lower() != 'y':
            logger.info("Aborted.")
            sys.exit(0)

    # Create scraper config
    config = ScraperConfig(
        rate_limit_delay=args.rate_limit,
        max_concurrent_requests=args.max_concurrent,
        timeout=args.timeout,
        cache_dir=Path(args.cache_dir) if args.cache_dir else None
    )

    # Run scraper
    logger.info("\n🚀 Starting scraper...\n")

    results = asyncio.run(
        scrape_states(
            state_codes,
            config,
            test_mode=args.test,
            max_statutes=args.max_statutes,
            use_justia=(args.source == 'justia')
        )
    )

    # Summary
    total_statutes = sum(len(statutes) for statutes in results.values())
    successful_states = sum(1 for statutes in results.values() if statutes)

    logger.info(f"\n{'='*60}")
    logger.info("SUMMARY")
    logger.info(f"{'='*60}")
    logger.info(f"States attempted: {len(state_codes)}")
    logger.info(f"States successful: {successful_states}")
    logger.info(f"Total statutes: {total_statutes}")
    logger.info(f"{'='*60}\n")

    # Output results
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with output_path.open('w', encoding='utf-8') as f:
            json.dump(
                results,
                f,
                indent=2 if args.pretty else None,
                ensure_ascii=False
            )

        logger.info(f"✓ Results saved to: {output_path}")

    else:
        # Print to stdout
        print(json.dumps(
            results,
            indent=2 if args.pretty else None,
            ensure_ascii=False
        ))

    # Show sample statute if in test mode
    if args.test and total_statutes > 0:
        logger.info("\n📄 Sample statute:")
        for state, statutes in results.items():
            if statutes:
                sample = statutes[0]
                logger.info(f"\n  State: {sample['state']}")
                logger.info(f"  Number: {sample['statute_number']}")
                logger.info(f"  Title: {sample['title'][:100]}...")
                logger.info(f"  Text: {sample['full_text'][:200]}...")
                logger.info(f"  URL: {sample['source_url']}")
                break


if __name__ == '__main__':
    main()
