"""
Wex Legal Dictionary Scraper

Scrapes legal terms and definitions from Cornell Law School's Wex legal dictionary.
Wex is a free legal dictionary and encyclopedia created by legal experts and academics.

Source: https://www.law.cornell.edu/wex
"""

import asyncio
import re
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import httpx
from bs4 import BeautifulSoup

from .base_scraper import BaseScraper, ScraperConfig


@dataclass
class LegalTerm:
    """Represents a legal dictionary term"""
    term: str
    definition: str
    jurisdiction: str = "general"
    source: str = "Wex"
    source_url: str = ""
    metadata: Dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class WexDictionaryScraper(BaseScraper):
    """
    Scraper for Cornell Law School's Wex legal dictionary
    """

    BASE_URL = "https://www.law.cornell.edu"
    WEX_BASE = f"{BASE_URL}/wex"

    def __init__(self, config: Optional[ScraperConfig] = None):
        """Initialize the Wex scraper"""
        if config is None:
            config = ScraperConfig(
                rate_limit_delay=1.0,  # Respectful 1 second delay
                timeout=30.0,
                max_retries=3,
                cache_enabled=True
            )
        super().__init__(config)

    async def scrape_all(self, max_terms: Optional[int] = None) -> List[LegalTerm]:
        """
        Scrape all legal terms from Wex

        Args:
            max_terms: Maximum number of terms to scrape (None for all)

        Returns:
            List of LegalTerm objects
        """
        terms = []

        self.logger.info("Starting scrape of Wex legal dictionary")

        # Get the alphabetical index
        index_urls = await self.get_alphabetical_index()

        self.logger.info(f"Found {len(index_urls)} alphabetical sections")

        for letter, url in index_urls.items():
            self.logger.info(f"Scraping terms starting with '{letter}'...")

            letter_terms = await self.scrape_letter_section(url)
            terms.extend(letter_terms)

            self.logger.info(f"  Found {len(letter_terms)} terms for letter '{letter}'")

            if max_terms and len(terms) >= max_terms:
                self.logger.info(f"Reached max_terms limit of {max_terms}")
                terms = terms[:max_terms]
                break

        self.logger.info(f"Successfully scraped {len(terms)} legal terms from Wex")
        return terms

    async def get_alphabetical_index(self) -> Dict[str, str]:
        """
        Get URLs for each alphabetical section

        Returns:
            Dictionary mapping letters to URLs
        """
        html = await self.fetch(self.WEX_BASE)

        if not html:
            self.logger.error(f"Failed to fetch Wex index from {self.WEX_BASE}")
            return {}

        soup = BeautifulSoup(html, 'lxml')
        index_urls = {}

        # Look for alphabetical navigation
        # Wex has links like /wex/a, /wex/b, etc.
        nav = soup.find('div', class_='alphabet-nav') or soup.find('nav')

        if nav:
            links = nav.find_all('a', href=re.compile(r'/wex/[a-z]$'))
            for link in links:
                letter = link.get_text().strip().upper()
                url = self.BASE_URL + link['href']
                index_urls[letter] = url
        else:
            # Fallback: generate URLs for all letters
            for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                index_urls[letter] = f"{self.WEX_BASE}/{letter.lower()}"

        return index_urls

    async def scrape_letter_section(self, url: str) -> List[LegalTerm]:
        """
        Scrape all terms from a single letter section

        Args:
            url: URL of the letter section

        Returns:
            List of LegalTerm objects
        """
        html = await self.fetch(url)

        if not html:
            self.logger.error(f"Failed to fetch {url}")
            return []

        soup = BeautifulSoup(html, 'lxml')
        terms = []

        # Find all term links
        # Wex typically has a list of terms with links
        content = soup.find('div', class_='content') or soup.find('main') or soup

        term_links = content.find_all('a', href=re.compile(r'/wex/[\w-]+'))

        # Remove duplicates
        seen_hrefs = set()
        unique_links = []

        for link in term_links:
            href = link.get('href')
            if href and href not in seen_hrefs:
                # Skip navigation links
                if not any(skip in href for skip in ['/wex/a', '/wex/b', '/wex/c']):
                    seen_hrefs.add(href)
                    unique_links.append(link)

        self.logger.debug(f"Found {len(unique_links)} unique term links in {url}")

        # Scrape each term's definition page
        for link in unique_links:
            term_url = self.BASE_URL + link['href']
            term_name = link.get_text().strip()

            if not term_name:
                continue

            term = await self.scrape_term_definition(term_name, term_url)
            if term:
                terms.append(term)

        return terms

    async def scrape_term_definition(self, term_name: str, url: str) -> Optional[LegalTerm]:
        """
        Scrape a single term's definition

        Args:
            term_name: Name of the term
            url: URL of the term's definition page

        Returns:
            LegalTerm object or None if failed
        """
        html = await self.fetch(url)

        if not html:
            self.logger.warning(f"Failed to fetch definition for '{term_name}' from {url}")
            return None

        soup = BeautifulSoup(html, 'lxml')

        # Extract definition text
        definition = self._extract_definition(soup)

        if not definition:
            self.logger.warning(f"No definition found for '{term_name}' at {url}")
            return None

        # Extract metadata
        metadata = self._extract_metadata(soup)
        metadata['scrape_date'] = datetime.now().isoformat()
        metadata['source_name'] = 'Wex (Cornell LII)'

        # Determine jurisdiction if mentioned
        jurisdiction = self._determine_jurisdiction(definition)

        return LegalTerm(
            term=term_name,
            definition=definition,
            jurisdiction=jurisdiction,
            source="Wex",
            source_url=url,
            metadata=metadata
        )

    def _extract_definition(self, soup: BeautifulSoup) -> str:
        """Extract the definition text from the page"""
        # Try different content selectors
        content_selectors = [
            ('div', {'class': 'field-item'}),
            ('div', {'class': 'content'}),
            ('div', {'class': 'wex-content'}),
            ('article', {}),
            ('main', {})
        ]

        for tag, attrs in content_selectors:
            content = soup.find(tag, attrs)
            if content:
                # Get text but exclude navigation and other non-definition elements
                definition = []

                # Find paragraphs
                paragraphs = content.find_all('p')

                for p in paragraphs:
                    text = p.get_text().strip()
                    # Skip very short paragraphs (likely navigation)
                    if len(text) > 20:
                        definition.append(text)

                if definition:
                    return ' '.join(definition)

        # Fallback: get all text
        main_content = soup.find('main') or soup.find('article')
        if main_content:
            text = main_content.get_text()
            return self._clean_text(text)

        return ""

    def _extract_metadata(self, soup: BeautifulSoup) -> Dict:
        """Extract metadata from the page"""
        metadata = {}

        # Look for related terms
        related = soup.find('div', class_='related-terms')
        if related:
            related_links = related.find_all('a')
            metadata['related_terms'] = [link.get_text().strip() for link in related_links]

        # Look for categories/topics
        categories = soup.find('div', class_='field-name-field-topics')
        if categories:
            category_links = categories.find_all('a')
            metadata['categories'] = [link.get_text().strip() for link in category_links]

        # Look for citations
        citations = soup.find_all('cite')
        if citations:
            metadata['citations'] = [cite.get_text().strip() for cite in citations]

        return metadata

    def _determine_jurisdiction(self, definition: str) -> str:
        """
        Determine jurisdiction based on definition content

        Args:
            definition: Definition text

        Returns:
            Jurisdiction string
        """
        definition_lower = definition.lower()

        # State-specific terms
        states = {
            'california': 'CA',
            'new york': 'NY',
            'texas': 'TX',
            'florida': 'FL',
            # Add more as needed
        }

        for state_name, state_code in states.items():
            if state_name in definition_lower:
                return state_code

        # Federal terms
        if any(keyword in definition_lower for keyword in
               ['federal', 'u.s.c.', 'united states code', 'supreme court']):
            return 'federal'

        # Default to general
        return 'general'

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove leading/trailing whitespace
        text = text.strip()
        return text

    async def fetch(self, url: str) -> Optional[str]:
        """
        Fetch content from URL with rate limiting and retries

        Args:
            url: URL to fetch

        Returns:
            HTML content or None if failed
        """
        return await self._fetch_with_retry(url)

    def get_stats(self) -> Dict:
        """Get scraping statistics"""
        return {
            "requests_made": self.stats.get("requests_made", 0),
            "requests_failed": self.stats.get("requests_failed", 0),
            "cache_hits": self.stats.get("cache_hits", 0),
            "total_terms": self.stats.get("total_terms", 0)
        }


async def main():
    """Example usage"""
    scraper = WexDictionaryScraper()

    try:
        # Scrape first 10 terms as a test
        terms = await scraper.scrape_all(max_terms=10)

        print(f"\nScraped {len(terms)} legal terms:")
        print("=" * 80)

        for term in terms:
            print(f"\nTerm: {term.term}")
            print(f"Jurisdiction: {term.jurisdiction}")
            print(f"Definition: {term.definition[:200]}..." if len(term.definition) > 200 else f"Definition: {term.definition}")
            print(f"Source: {term.source_url}")
            print(f"Metadata: {term.metadata}")
            print("-" * 80)

        print(f"\nStats: {scraper.get_stats()}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
