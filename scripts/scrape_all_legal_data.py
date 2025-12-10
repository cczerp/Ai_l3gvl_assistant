"""
Master Legal Data Collection Script

This script orchestrates the collection of all legal data:
- US Constitution & Bill of Rights
- Legal dictionaries (3 sources)
- Supreme Court cases (past 50 years)
- State laws (all 50 states)
- State court cases (all 50 states)
- Federal laws (U.S. Code)

Usage:
    python scripts/scrape_all_legal_data.py --all
    python scripts/scrape_all_legal_data.py --constitution --dictionaries
    python scripts/scrape_all_legal_data.py --supreme-court --max-cases 1000
    python scripts/scrape_all_legal_data.py --state-laws --states CA,NY,TX
"""

import asyncio
import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import logging

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from scrapers.constitution_scraper import ConstitutionScraper, ConstitutionalDocument
from scrapers.wex_dictionary_scraper import WexDictionaryScraper
from scrapers.lawdict_scraper import LawDictScraper
from scrapers.courtlistener_scotus_scraper import CourtListenerSCOTUSScraper
from scrapers.courtlistener_state_courts_scraper import CourtListenerStateCourtsScraper
from scrapers.justia_scraper import JustiaScraper

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LegalDataCollector:
    """Main orchestrator for all legal data collection"""

    def __init__(
        self,
        data_dir: str = "data",
        courtlistener_api_key: Optional[str] = None
    ):
        """
        Initialize the collector

        Args:
            data_dir: Directory to save scraped data
            courtlistener_api_key: API key for CourtListener
        """
        self.data_dir = Path(data_dir)
        self.api_key = courtlistener_api_key

        # Create data directories
        self.dirs = {
            "constitution": self.data_dir / "constitutional_documents",
            "dictionaries": self.data_dir / "legal_dictionaries",
            "supreme_court": self.data_dir / "cases" / "supreme_court",
            "state_laws": self.data_dir / "state_laws",
            "state_courts": self.data_dir / "cases" / "state_courts",
            "federal_laws": self.data_dir / "federal_laws",
            "reports": self.data_dir / "reports"
        }

        for directory in self.dirs.values():
            directory.mkdir(parents=True, exist_ok=True)

        self.stats = {
            "start_time": None,
            "end_time": None,
            "constitution_docs": 0,
            "dictionary_terms": 0,
            "supreme_court_cases": 0,
            "state_laws_statutes": 0,
            "state_court_cases": 0,
            "federal_laws_sections": 0,
            "errors": []
        }

    async def collect_constitution(self) -> bool:
        """Collect US Constitution and Bill of Rights"""
        logger.info("\n" + "="*80)
        logger.info("COLLECTING: US Constitution & Bill of Rights")
        logger.info("="*80 + "\n")

        try:
            scraper = ConstitutionScraper()
            documents = await scraper.scrape_all()

            # Save to JSON
            output_file = self.dirs["constitution"] / "us_constitution.json"
            self._save_json([self._doc_to_dict(doc) for doc in documents], output_file)

            self.stats["constitution_docs"] = len(documents)

            logger.info(f"✓ Successfully collected {len(documents)} constitutional documents")
            return True

        except Exception as e:
            logger.error(f"✗ Error collecting Constitution: {e}")
            self.stats["errors"].append(f"Constitution: {str(e)}")
            return False

    async def collect_dictionaries(self, max_terms_per_source: Optional[int] = None) -> bool:
        """Collect legal dictionaries from 3 sources"""
        logger.info("\n" + "="*80)
        logger.info("COLLECTING: Legal Dictionaries (3 sources)")
        logger.info("="*80 + "\n")

        all_terms = {}

        # Source 1: Wex (Cornell)
        logger.info("1/3: Scraping Wex (Cornell LII)...")
        try:
            wex_scraper = WexDictionaryScraper()
            wex_terms = await wex_scraper.scrape_all(max_terms=max_terms_per_source)

            output_file = self.dirs["dictionaries"] / "wex_dictionary.json"
            self._save_json([self._term_to_dict(term) for term in wex_terms], output_file)

            all_terms["wex"] = len(wex_terms)
            logger.info(f"  ✓ Wex: {len(wex_terms)} terms")

        except Exception as e:
            logger.error(f"  ✗ Wex error: {e}")
            self.stats["errors"].append(f"Wex: {str(e)}")
            all_terms["wex"] = 0

        # Source 2: TheLawDictionary (Black's)
        logger.info("2/3: Scraping TheLawDictionary.org (Black's Law Dictionary)...")
        try:
            lawdict_scraper = LawDictScraper()
            lawdict_terms = await lawdict_scraper.scrape_all(max_terms=max_terms_per_source)

            output_file = self.dirs["dictionaries"] / "blackslawdictionary.json"
            self._save_json([self._term_to_dict(term) for term in lawdict_terms], output_file)

            all_terms["blackslawdictionary"] = len(lawdict_terms)
            logger.info(f"  ✓ Black's: {len(lawdict_terms)} terms")

        except Exception as e:
            logger.error(f"  ✗ Black's error: {e}")
            self.stats["errors"].append(f"Black's: {str(e)}")
            all_terms["blackslawdictionary"] = 0

        # Note: FindLaw dictionary scraper would go here (not implemented yet)

        total_terms = sum(all_terms.values())
        self.stats["dictionary_terms"] = total_terms

        logger.info(f"\n✓ Total dictionary terms collected: {total_terms}")
        return total_terms > 0

    async def collect_supreme_court_cases(self, years: int = 50, max_cases: Optional[int] = None) -> bool:
        """Collect Supreme Court cases"""
        logger.info("\n" + "="*80)
        logger.info(f"COLLECTING: Supreme Court Cases (past {years} years)")
        logger.info("="*80 + "\n")

        try:
            scraper = CourtListenerSCOTUSScraper(api_key=self.api_key)
            cases = await scraper.scrape_last_n_years(years=years, max_cases=max_cases)

            # Save to JSON
            output_file = self.dirs["supreme_court"] / f"scotus_cases_{years}years.json"
            self._save_json([self._case_to_dict(case) for case in cases], output_file)

            self.stats["supreme_court_cases"] = len(cases)

            logger.info(f"✓ Successfully collected {len(cases)} Supreme Court cases")
            return True

        except Exception as e:
            logger.error(f"✗ Error collecting Supreme Court cases: {e}")
            self.stats["errors"].append(f"SCOTUS: {str(e)}")
            return False

    async def collect_state_laws(self, states: Optional[List[str]] = None, test_mode: bool = False) -> bool:
        """
        Collect state laws from Justia

        Args:
            states: List of state codes (e.g., ['CA', 'NY']). None for all 50 states.
            test_mode: If True, collect only a small sample
        """
        logger.info("\n" + "="*80)
        logger.info(f"COLLECTING: State Laws")
        logger.info("="*80 + "\n")

        try:
            scraper = JustiaScraper()

            if states is None:
                # All 50 states
                from scrapers.base_scraper import US_STATES
                states = list(US_STATES.keys())

            total_statutes = 0

            for state in states:
                logger.info(f"Scraping {state}...")

                try:
                    statutes = await scraper.scrape_state(
                        state,
                        sample_size=10 if test_mode else None
                    )

                    if statutes:
                        # Save state data
                        output_file = self.dirs["state_laws"] / f"{state.lower()}_laws.json"
                        self._save_json([self._statute_to_dict(s) for s in statutes], output_file)

                        total_statutes += len(statutes)
                        logger.info(f"  ✓ {state}: {len(statutes)} statutes")

                except Exception as e:
                    logger.error(f"  ✗ {state} error: {e}")
                    self.stats["errors"].append(f"State {state}: {str(e)}")

            self.stats["state_laws_statutes"] = total_statutes

            logger.info(f"\n✓ Total state law statutes collected: {total_statutes}")
            return total_statutes > 0

        except Exception as e:
            logger.error(f"✗ Error collecting state laws: {e}")
            self.stats["errors"].append(f"State Laws: {str(e)}")
            return False

    async def collect_state_court_cases(
        self,
        states: Optional[List[str]] = None,
        max_cases_per_state: Optional[int] = None
    ) -> bool:
        """Collect state court cases"""
        logger.info("\n" + "="*80)
        logger.info(f"COLLECTING: State Court Cases")
        logger.info("="*80 + "\n")

        try:
            scraper = CourtListenerStateCourtsScraper(api_key=self.api_key)

            if states is None:
                # All 50 states
                from scrapers.base_scraper import US_STATES
                states = list(US_STATES.keys())

            total_cases = 0

            for state in states:
                logger.info(f"Scraping {state}...")

                try:
                    cases = await scraper.scrape_state_cases(
                        state_code=state,
                        max_cases=max_cases_per_state
                    )

                    if cases:
                        # Save state data
                        output_file = self.dirs["state_courts"] / f"{state.lower()}_cases.json"
                        self._save_json([self._case_to_dict(case) for case in cases], output_file)

                        total_cases += len(cases)
                        logger.info(f"  ✓ {state}: {len(cases)} cases")

                except Exception as e:
                    logger.error(f"  ✗ {state} error: {e}")
                    self.stats["errors"].append(f"State courts {state}: {str(e)}")

            self.stats["state_court_cases"] = total_cases

            logger.info(f"\n✓ Total state court cases collected: {total_cases}")
            return total_cases > 0

        except Exception as e:
            logger.error(f"✗ Error collecting state court cases: {e}")
            self.stats["errors"].append(f"State Courts: {str(e)}")
            return False

    def _doc_to_dict(self, doc) -> dict:
        """Convert ConstitutionalDocument to dict"""
        return {
            "document_type": doc.document_type,
            "article_number": doc.article_number,
            "section_number": doc.section_number,
            "amendment_number": doc.amendment_number,
            "title": doc.title,
            "full_text": doc.full_text,
            "ratified_date": doc.ratified_date,
            "source_url": doc.source_url,
            "metadata": doc.metadata
        }

    def _term_to_dict(self, term) -> dict:
        """Convert LegalTerm to dict"""
        return {
            "term": term.term,
            "definition": term.definition,
            "jurisdiction": term.jurisdiction,
            "source": term.source,
            "source_url": term.source_url,
            "metadata": term.metadata
        }

    def _case_to_dict(self, case) -> dict:
        """Convert case object to dict"""
        return {
            "case_name": case.case_name,
            "citation": case.citation,
            "court": case.court,
            "jurisdiction": case.jurisdiction,
            "date_decided": case.date_decided,
            "judges": case.judges,
            "docket_number": case.docket_number,
            "opinion_text": case.opinion_text,
            "opinion_type": case.opinion_type,
            "source_url": case.source_url,
            "metadata": case.metadata
        }

    def _statute_to_dict(self, statute) -> dict:
        """Convert statute object to dict"""
        return {
            "state": statute.state,
            "statute_number": statute.statute_number,
            "title": statute.title,
            "chapter": statute.chapter,
            "section": statute.section,
            "full_text": statute.full_text,
            "effective_date": statute.effective_date,
            "source_url": statute.source_url,
            "metadata": statute.metadata if hasattr(statute, 'metadata') else {}
        }

    def _save_json(self, data: List[dict], filepath: Path):
        """Save data to JSON file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.debug(f"Saved to {filepath}")

    def generate_report(self):
        """Generate collection report"""
        self.stats["end_time"] = datetime.now().isoformat()

        if self.stats["start_time"]:
            start = datetime.fromisoformat(self.stats["start_time"])
            end = datetime.fromisoformat(self.stats["end_time"])
            duration = end - start
            self.stats["duration_seconds"] = duration.total_seconds()

        report_file = self.dirs["reports"] / f"collection_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self._save_json(self.stats, report_file)

        # Print summary
        print("\n" + "="*80)
        print("COLLECTION SUMMARY")
        print("="*80)
        print(f"Constitutional documents: {self.stats['constitution_docs']}")
        print(f"Dictionary terms: {self.stats['dictionary_terms']}")
        print(f"Supreme Court cases: {self.stats['supreme_court_cases']}")
        print(f"State law statutes: {self.stats['state_laws_statutes']}")
        print(f"State court cases: {self.stats['state_court_cases']}")
        print(f"Federal law sections: {self.stats['federal_laws_sections']}")
        print(f"\nTotal errors: {len(self.stats['errors'])}")

        if self.stats['errors']:
            print("\nErrors:")
            for error in self.stats['errors']:
                print(f"  - {error}")

        print(f"\nReport saved to: {report_file}")
        print("="*80 + "\n")


async def main():
    parser = argparse.ArgumentParser(description="Collect all legal data")

    # Data collection options
    parser.add_argument("--all", action="store_true", help="Collect all data")
    parser.add_argument("--constitution", action="store_true", help="Collect US Constitution")
    parser.add_argument("--dictionaries", action="store_true", help="Collect legal dictionaries")
    parser.add_argument("--supreme-court", action="store_true", help="Collect Supreme Court cases")
    parser.add_argument("--state-laws", action="store_true", help="Collect state laws")
    parser.add_argument("--state-courts", action="store_true", help="Collect state court cases")

    # Configuration options
    parser.add_argument("--data-dir", default="data", help="Data directory")
    parser.add_argument("--api-key", help="CourtListener API key (or set COURTLISTENER_API_KEY env var)")
    parser.add_argument("--states", help="Comma-separated list of state codes (e.g., CA,NY,TX)")
    parser.add_argument("--max-cases", type=int, help="Maximum cases to collect")
    parser.add_argument("--max-terms", type=int, help="Maximum dictionary terms per source")
    parser.add_argument("--scotus-years", type=int, default=50, help="Years of SCOTUS cases to collect")
    parser.add_argument("--test-mode", action="store_true", help="Test mode (collect small samples)")

    args = parser.parse_args()

    # Get API key
    api_key = args.api_key or os.getenv("COURTLISTENER_API_KEY")

    if not api_key and (args.supreme_court or args.state_courts or args.all):
        logger.warning("No CourtListener API key provided. Rate limits will be lower.")
        logger.warning("Get an API key at: https://www.courtlistener.com/sign-in/register/")

    # Initialize collector
    collector = LegalDataCollector(
        data_dir=args.data_dir,
        courtlistener_api_key=api_key
    )

    collector.stats["start_time"] = datetime.now().isoformat()

    # Parse states if provided
    states = None
    if args.states:
        states = [s.strip().upper() for s in args.states.split(",")]

    # Collect data based on flags
    if args.all or args.constitution:
        await collector.collect_constitution()

    if args.all or args.dictionaries:
        await collector.collect_dictionaries(max_terms_per_source=args.max_terms)

    if args.all or args.supreme_court:
        await collector.collect_supreme_court_cases(
            years=args.scotus_years,
            max_cases=args.max_cases
        )

    if args.all or args.state_laws:
        await collector.collect_state_laws(
            states=states,
            test_mode=args.test_mode
        )

    if args.all or args.state_courts:
        await collector.collect_state_court_cases(
            states=states,
            max_cases_per_state=args.max_cases
        )

    # Generate report
    collector.generate_report()


if __name__ == "__main__":
    asyncio.run(main())
