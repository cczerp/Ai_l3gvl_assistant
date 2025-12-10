"""
CourtListener Supreme Court Cases Scraper

Scrapes Supreme Court cases from the past 50 years (1974-2024) using the
CourtListener REST API v4. CourtListener is operated by Free Law Project,
a 501(c)(3) nonprofit.

API Documentation: https://www.courtlistener.com/help/api/rest/
"""

import asyncio
import json
from typing import List, Dict, Optional, AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
import httpx

from .base_scraper import BaseScraper, ScraperConfig


@dataclass
class SupremeCourtCase:
    """Represents a Supreme Court case"""
    case_name: str
    citation: str
    court: str = "Supreme Court of the United States"
    jurisdiction: str = "federal"
    date_decided: Optional[str] = None
    judges: List[str] = field(default_factory=list)
    docket_number: Optional[str] = None
    opinion_text: str = ""
    opinion_type: str = "majority"
    courtlistener_id: Optional[int] = None
    source_url: str = ""
    metadata: Dict = field(default_factory=dict)


class CourtListenerSCOTUSScraper(BaseScraper):
    """
    Scraper for Supreme Court cases from CourtListener API

    The API is free but rate-limited. Register for an API key to get higher limits:
    https://www.courtlistener.com/sign-in/register/
    """

    API_BASE = "https://www.courtlistener.com/api/rest/v4"
    API_VERSION = "v4"

    # Supreme Court identifier in CourtListener
    SCOTUS_COURT_ID = "scotus"

    def __init__(self, api_key: Optional[str] = None, config: Optional[ScraperConfig] = None):
        """
        Initialize the CourtListener scraper

        Args:
            api_key: Optional API key for higher rate limits
            config: Scraper configuration
        """
        if config is None:
            config = ScraperConfig(
                rate_limit_delay=2.0,  # 2 seconds between requests (conservative)
                timeout=60.0,  # Longer timeout for API
                max_retries=3,
                cache_enabled=True
            )
        super().__init__(config)

        self.api_key = api_key
        self.headers = {
            "User-Agent": "LegalAI-Scraper/1.0 (Research Project)",
            "Accept": "application/json"
        }

        if self.api_key:
            self.headers["Authorization"] = f"Token {self.api_key}"
            self.logger.info("Using API key for authentication")
        else:
            self.logger.warning("No API key provided. Rate limits will be lower. Get one at: https://www.courtlistener.com/")

    async def scrape_cases_by_date_range(
        self,
        start_date: str,
        end_date: str,
        max_cases: Optional[int] = None
    ) -> List[SupremeCourtCase]:
        """
        Scrape Supreme Court cases within a date range

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            max_cases: Maximum number of cases to scrape

        Returns:
            List of SupremeCourtCase objects
        """
        cases = []

        self.logger.info(f"Scraping SCOTUS cases from {start_date} to {end_date}")

        async for case in self.iter_cases(start_date, end_date):
            cases.append(case)

            if max_cases and len(cases) >= max_cases:
                self.logger.info(f"Reached max_cases limit of {max_cases}")
                break

            if len(cases) % 100 == 0:
                self.logger.info(f"Scraped {len(cases)} cases so far...")

        self.logger.info(f"Successfully scraped {len(cases)} Supreme Court cases")
        return cases

    async def scrape_last_n_years(self, years: int = 50, max_cases: Optional[int] = None) -> List[SupremeCourtCase]:
        """
        Scrape Supreme Court cases from the last N years

        Args:
            years: Number of years to go back
            max_cases: Maximum number of cases to scrape

        Returns:
            List of SupremeCourtCase objects
        """
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=years * 365)

        return await self.scrape_cases_by_date_range(
            start_date.isoformat(),
            end_date.isoformat(),
            max_cases
        )

    async def iter_cases(
        self,
        start_date: str,
        end_date: str
    ) -> AsyncGenerator[SupremeCourtCase, None]:
        """
        Iterate through cases using pagination

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Yields:
            SupremeCourtCase objects
        """
        # Search for opinions
        endpoint = f"{self.API_BASE}/search/"

        params = {
            "type": "o",  # Opinions
            "court": self.SCOTUS_COURT_ID,
            "filed_after": start_date,
            "filed_before": end_date,
            "order_by": "dateFiled",
            "format": "json"
        }

        next_url = endpoint
        page = 1

        while next_url:
            self.logger.info(f"Fetching page {page}...")

            response_data = await self.fetch_api(next_url, params if page == 1 else None)

            if not response_data:
                self.logger.error("Failed to fetch search results")
                break

            results = response_data.get("results", [])

            if not results:
                self.logger.info("No more results")
                break

            for result in results:
                # Get full opinion details
                opinion = await self.fetch_opinion_details(result)

                if opinion:
                    case = self._parse_opinion_to_case(opinion)
                    if case:
                        yield case

            # Get next page
            next_url = response_data.get("next")
            page += 1

            # Respect rate limiting
            await asyncio.sleep(self.config.rate_limit_delay)

    async def fetch_opinion_details(self, search_result: Dict) -> Optional[Dict]:
        """
        Fetch full details for an opinion

        Args:
            search_result: Search result from the API

        Returns:
            Full opinion data
        """
        # The search result may include the full opinion or just a reference
        if "absolute_url" in search_result:
            # Need to fetch full details
            url = f"{self.API_BASE}/opinions/{search_result['id']}/"
            return await self.fetch_api(url)
        else:
            # Already have full data
            return search_result

    async def fetch_api(self, url: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """
        Fetch data from CourtListener API

        Args:
            url: API endpoint URL
            params: Query parameters

        Returns:
            JSON response data
        """
        try:
            async with httpx.AsyncClient(timeout=self.config.timeout) as client:
                response = await client.get(
                    url,
                    params=params,
                    headers=self.headers,
                    follow_redirects=True
                )

                # Check rate limiting
                if response.status_code == 429:
                    self.logger.warning("Rate limited! Waiting before retry...")
                    await asyncio.sleep(10)  # Wait 10 seconds
                    return await self.fetch_api(url, params)  # Retry

                response.raise_for_status()

                self.stats["requests_made"] = self.stats.get("requests_made", 0) + 1

                return response.json()

        except httpx.HTTPStatusError as e:
            self.logger.error(f"HTTP error fetching {url}: {e}")
            self.stats["requests_failed"] = self.stats.get("requests_failed", 0) + 1
            return None

        except Exception as e:
            self.logger.error(f"Error fetching {url}: {e}")
            self.stats["requests_failed"] = self.stats.get("requests_failed", 0) + 1
            return None

    def _parse_opinion_to_case(self, opinion_data: Dict) -> Optional[SupremeCourtCase]:
        """
        Parse API opinion data into a SupremeCourtCase object

        Args:
            opinion_data: Opinion data from API

        Returns:
            SupremeCourtCase object or None
        """
        try:
            # Extract basic case information
            case_name = opinion_data.get("case_name", "")
            if not case_name:
                return None

            # Get citation
            citation = self._extract_citation(opinion_data)

            # Get date
            date_filed = opinion_data.get("date_filed")

            # Get docket number
            docket_number = opinion_data.get("docket_number")

            # Get opinion text
            opinion_text = self._extract_opinion_text(opinion_data)

            # Get opinion type
            opinion_type = self._determine_opinion_type(opinion_data)

            # Get judges
            judges = self._extract_judges(opinion_data)

            # Build source URL
            source_url = f"https://www.courtlistener.com{opinion_data.get('absolute_url', '')}"

            # Build metadata
            metadata = {
                "scrape_date": datetime.now().isoformat(),
                "source_name": "CourtListener",
                "api_version": self.API_VERSION,
                "courtlistener_id": opinion_data.get("id"),
                "cluster_id": opinion_data.get("cluster_id"),
                "download_url": opinion_data.get("download_url"),
                "scdb_id": opinion_data.get("scdb_id"),  # Supreme Court Database ID
                "scdb_votes_majority": opinion_data.get("scdb_votes_majority"),
                "scdb_votes_minority": opinion_data.get("scdb_votes_minority")
            }

            return SupremeCourtCase(
                case_name=case_name,
                citation=citation,
                date_decided=date_filed,
                docket_number=docket_number,
                opinion_text=opinion_text,
                opinion_type=opinion_type,
                judges=judges,
                courtlistener_id=opinion_data.get("id"),
                source_url=source_url,
                metadata=metadata
            )

        except Exception as e:
            self.logger.error(f"Error parsing opinion: {e}")
            return None

    def _extract_citation(self, opinion_data: Dict) -> str:
        """Extract citation from opinion data"""
        # Try to get citation from various fields
        if "citation" in opinion_data:
            return opinion_data["citation"]

        # Build from volume, reporter, page
        citations = opinion_data.get("citations", [])
        if citations:
            # Use the first citation
            cit = citations[0]
            volume = cit.get("volume", "")
            reporter = cit.get("reporter", "")
            page = cit.get("page", "")
            return f"{volume} {reporter} {page}".strip()

        return ""

    def _extract_opinion_text(self, opinion_data: Dict) -> str:
        """Extract opinion text"""
        # Try different text fields
        text_fields = ["plain_text", "html", "html_with_citations"]

        for field in text_fields:
            if field in opinion_data and opinion_data[field]:
                return opinion_data[field]

        return ""

    def _determine_opinion_type(self, opinion_data: Dict) -> str:
        """Determine opinion type (majority, dissent, concurring)"""
        opinion_type = opinion_data.get("type", "").lower()

        if "dissent" in opinion_type:
            return "dissent"
        elif "concur" in opinion_type:
            return "concurring"
        elif "majority" in opinion_type or not opinion_type:
            return "majority"
        else:
            return opinion_type

    def _extract_judges(self, opinion_data: Dict) -> List[str]:
        """Extract judges/justices"""
        judges = []

        # Author
        if "author" in opinion_data and opinion_data["author"]:
            author = opinion_data["author"]
            if isinstance(author, dict):
                judges.append(author.get("name", ""))
            else:
                judges.append(str(author))

        # Joined by
        if "joined_by" in opinion_data:
            for judge in opinion_data["joined_by"]:
                if isinstance(judge, dict):
                    judges.append(judge.get("name", ""))
                else:
                    judges.append(str(judge))

        return [j for j in judges if j]  # Filter empty strings

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

    # Get API key from environment variable if available
    api_key = os.getenv("COURTLISTENER_API_KEY")

    scraper = CourtListenerSCOTUSScraper(api_key=api_key)

    try:
        # Scrape cases from last 5 years (test with smaller dataset)
        cases = await scraper.scrape_last_n_years(years=5, max_cases=10)

        print(f"\nScraped {len(cases)} Supreme Court cases:")
        print("=" * 80)

        for case in cases:
            print(f"\nCase: {case.case_name}")
            print(f"Citation: {case.citation}")
            print(f"Date Decided: {case.date_decided}")
            print(f"Docket: {case.docket_number}")
            print(f"Opinion Type: {case.opinion_type}")
            print(f"Judges: {', '.join(case.judges)}")
            print(f"Text Length: {len(case.opinion_text)} characters")
            print(f"Source: {case.source_url}")
            print("-" * 80)

        print(f"\nStats: {scraper.get_stats()}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
