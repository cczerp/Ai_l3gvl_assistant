"""
CourtListener State Courts Scraper

Scrapes state court cases from all 50 states using the CourtListener REST API.
Includes state supreme courts and appellate courts (470+ jurisdictions).

API Documentation: https://www.courtlistener.com/help/api/rest/
"""

import asyncio
import json
from typing import List, Dict, Optional, AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import httpx

from .base_scraper import BaseScraper, ScraperConfig


@dataclass
class StateCourtCase:
    """Represents a state court case"""
    case_name: str
    citation: str
    court: str
    jurisdiction: str  # 2-letter state code
    date_decided: Optional[str] = None
    judges: List[str] = field(default_factory=list)
    docket_number: Optional[str] = None
    opinion_text: str = ""
    opinion_type: str = "majority"
    courtlistener_id: Optional[int] = None
    source_url: str = ""
    metadata: Dict = field(default_factory=dict)


class CourtListenerStateCourtsScraper(BaseScraper):
    """
    Scraper for state court cases from CourtListener API

    Covers all 50 states' supreme and appellate courts
    """

    API_BASE = "https://www.courtlistener.com/api/rest/v4"
    API_VERSION = "v4"

    # Mapping of state codes to CourtListener court identifiers
    STATE_COURTS = {
        # Format: state_code: [list of court IDs for that state]
        # These are example IDs - you may need to fetch the full court list from API
        'AL': ['ala', 'alactapp', 'alacrimapp', 'alacivapp'],
        'AK': ['alaska', 'alaskactapp'],
        'AZ': ['ariz', 'arizctapp', 'ariztaxct'],
        'AR': ['ark', 'arkctapp', 'arkworkcompcom', 'arkag'],
        'CA': ['cal', 'calctapp'],
        # ... (would need complete mapping for all 50 states)
    }

    def __init__(self, api_key: Optional[str] = None, config: Optional[ScraperConfig] = None):
        """
        Initialize the scraper

        Args:
            api_key: Optional API key for higher rate limits
            config: Scraper configuration
        """
        if config is None:
            config = ScraperConfig(
                rate_limit_delay=2.0,
                timeout=60.0,
                max_retries=3,
                cache_enabled=True
            )
        super().__init__(config)

        self.api_key = api_key
        self.headers = {
            "User-Agent": "LegalAI-StateCourts-Scraper/1.0 (Research Project)",
            "Accept": "application/json"
        }

        if self.api_key:
            self.headers["Authorization"] = f"Token {self.api_key}"

        # Cache for court list
        self.court_list: Optional[List[Dict]] = None

    async def get_all_state_courts(self) -> List[Dict]:
        """
        Fetch list of all state courts from API

        Returns:
            List of court dictionaries
        """
        if self.court_list:
            return self.court_list

        self.logger.info("Fetching complete list of courts from API...")

        endpoint = f"{self.API_BASE}/courts/"
        all_courts = []

        next_url = endpoint

        while next_url:
            data = await self.fetch_api(next_url)

            if not data:
                break

            results = data.get("results", [])
            all_courts.extend(results)

            next_url = data.get("next")

        # Filter for state courts
        state_courts = [
            court for court in all_courts
            if court.get("jurisdiction") == "S"  # State jurisdiction
        ]

        self.logger.info(f"Found {len(state_courts)} state courts")
        self.court_list = state_courts

        return state_courts

    async def scrape_state_cases(
        self,
        state_code: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        max_cases: Optional[int] = None
    ) -> List[StateCourtCase]:
        """
        Scrape cases for a specific state

        Args:
            state_code: 2-letter state code (e.g., 'CA', 'NY')
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            max_cases: Maximum number of cases

        Returns:
            List of StateCourtCase objects
        """
        self.logger.info(f"Scraping cases for state: {state_code}")

        # Get courts for this state
        all_courts = await self.get_all_state_courts()

        # Filter courts for this state
        state_courts = [
            court for court in all_courts
            if court.get("id", "").startswith(state_code.lower())
            or state_code.lower() in court.get("id", "")
        ]

        if not state_courts:
            self.logger.warning(f"No courts found for state {state_code}")
            return []

        self.logger.info(f"Found {len(state_courts)} courts for {state_code}")

        cases = []

        for court in state_courts:
            court_id = court.get("id")
            court_name = court.get("name")

            self.logger.info(f"  Scraping {court_name} ({court_id})...")

            court_cases = await self.scrape_court_cases(
                court_id=court_id,
                court_name=court_name,
                state_code=state_code,
                start_date=start_date,
                end_date=end_date,
                max_cases=max_cases
            )

            cases.extend(court_cases)

            if max_cases and len(cases) >= max_cases:
                break

        self.logger.info(f"Total cases scraped for {state_code}: {len(cases)}")
        return cases

    async def scrape_all_states(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        max_cases_per_state: Optional[int] = None
    ) -> Dict[str, List[StateCourtCase]]:
        """
        Scrape cases for all 50 states

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            max_cases_per_state: Maximum cases per state

        Returns:
            Dictionary mapping state codes to lists of cases
        """
        from .base_scraper import US_STATES

        all_cases = {}

        for state_code, state_name in US_STATES.items():
            self.logger.info(f"\n{'='*80}")
            self.logger.info(f"Starting {state_name} ({state_code})")
            self.logger.info(f"{'='*80}\n")

            try:
                cases = await self.scrape_state_cases(
                    state_code=state_code,
                    start_date=start_date,
                    end_date=end_date,
                    max_cases=max_cases_per_state
                )

                all_cases[state_code] = cases

            except Exception as e:
                self.logger.error(f"Error scraping {state_name}: {e}")
                all_cases[state_code] = []

        return all_cases

    async def scrape_court_cases(
        self,
        court_id: str,
        court_name: str,
        state_code: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        max_cases: Optional[int] = None
    ) -> List[StateCourtCase]:
        """
        Scrape cases for a specific court

        Args:
            court_id: CourtListener court ID
            court_name: Name of the court
            state_code: 2-letter state code
            start_date: Start date
            end_date: End date
            max_cases: Maximum cases

        Returns:
            List of StateCourtCase objects
        """
        cases = []

        endpoint = f"{self.API_BASE}/search/"

        params = {
            "type": "o",  # Opinions
            "court": court_id,
            "order_by": "dateFiled",
            "format": "json"
        }

        if start_date:
            params["filed_after"] = start_date

        if end_date:
            params["filed_before"] = end_date

        page = 1
        next_url = endpoint

        while next_url:
            data = await self.fetch_api(next_url, params if page == 1 else None)

            if not data:
                break

            results = data.get("results", [])

            if not results:
                break

            for result in results:
                case = self._parse_result_to_case(result, court_name, state_code)
                if case:
                    cases.append(case)

                if max_cases and len(cases) >= max_cases:
                    return cases

            next_url = data.get("next")
            page += 1

            await asyncio.sleep(self.config.rate_limit_delay)

        return cases

    async def fetch_api(self, url: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Fetch data from API"""
        try:
            async with httpx.AsyncClient(timeout=self.config.timeout) as client:
                response = await client.get(
                    url,
                    params=params,
                    headers=self.headers,
                    follow_redirects=True
                )

                if response.status_code == 429:
                    self.logger.warning("Rate limited! Waiting...")
                    await asyncio.sleep(10)
                    return await self.fetch_api(url, params)

                response.raise_for_status()

                self.stats["requests_made"] = self.stats.get("requests_made", 0) + 1

                return response.json()

        except Exception as e:
            self.logger.error(f"Error fetching {url}: {e}")
            self.stats["requests_failed"] = self.stats.get("requests_failed", 0) + 1
            return None

    def _parse_result_to_case(
        self,
        result: Dict,
        court_name: str,
        state_code: str
    ) -> Optional[StateCourtCase]:
        """Parse API result to StateCourtCase"""
        try:
            case_name = result.get("caseName") or result.get("case_name", "")
            if not case_name:
                return None

            citation = self._extract_citation(result)
            date_filed = result.get("dateFiled") or result.get("date_filed")
            docket_number = result.get("docketNumber") or result.get("docket_number")
            opinion_text = self._extract_text(result)
            opinion_type = self._determine_opinion_type(result)

            source_url = f"https://www.courtlistener.com{result.get('absolute_url', '')}"

            metadata = {
                "scrape_date": datetime.now().isoformat(),
                "source_name": "CourtListener",
                "courtlistener_id": result.get("id"),
                "cluster_id": result.get("cluster_id")
            }

            return StateCourtCase(
                case_name=case_name,
                citation=citation,
                court=court_name,
                jurisdiction=state_code,
                date_decided=date_filed,
                docket_number=docket_number,
                opinion_text=opinion_text,
                opinion_type=opinion_type,
                courtlistener_id=result.get("id"),
                source_url=source_url,
                metadata=metadata
            )

        except Exception as e:
            self.logger.error(f"Error parsing result: {e}")
            return None

    def _extract_citation(self, result: Dict) -> str:
        """Extract citation"""
        return result.get("citation", "") or result.get("neutral_cite", "")

    def _extract_text(self, result: Dict) -> str:
        """Extract opinion text"""
        return result.get("snippet", "") or result.get("text", "")

    def _determine_opinion_type(self, result: Dict) -> str:
        """Determine opinion type"""
        op_type = result.get("type", "").lower()

        if "dissent" in op_type:
            return "dissent"
        elif "concur" in op_type:
            return "concurring"
        else:
            return "majority"

    def get_stats(self) -> Dict:
        """Get scraping statistics"""
        return {
            "requests_made": self.stats.get("requests_made", 0),
            "requests_failed": self.stats.get("requests_failed", 0),
            "total_cases": self.stats.get("total_cases", 0)
        }


async def main():
    """Example usage"""
    import os

    api_key = os.getenv("COURTLISTENER_API_KEY")
    scraper = CourtListenerStateCourtsScraper(api_key=api_key)

    try:
        # Test: Scrape 10 cases from California
        cases = await scraper.scrape_state_cases(
            state_code="CA",
            max_cases=10
        )

        print(f"\nScraped {len(cases)} state court cases:")
        print("=" * 80)

        for case in cases:
            print(f"\nCase: {case.case_name}")
            print(f"Court: {case.court}")
            print(f"State: {case.jurisdiction}")
            print(f"Citation: {case.citation}")
            print(f"Date: {case.date_decided}")
            print(f"Source: {case.source_url}")
            print("-" * 80)

        print(f"\nStats: {scraper.get_stats()}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
