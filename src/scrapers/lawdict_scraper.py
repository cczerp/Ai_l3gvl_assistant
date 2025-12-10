"""
TheLawDictionary.org Scraper

Scrapes legal terms and definitions from TheLawDictionary.org,
which is based on Black's Law Dictionary 2nd Edition.

Source: https://thelawdictionary.org/
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
    source: str = "TheLawDictionary"
    source_url: str = ""
    metadata: Dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class LawDictScraper(BaseScraper):
    """
    Scraper for TheLawDictionary.org (Black's Law Dictionary 2nd Ed.)
    """

    BASE_URL = "https://thelawdictionary.org"

    def __init__(self, config: Optional[ScraperConfig] = None):
        """Initialize the LawDict scraper"""
        if config is None:
            config = ScraperConfig(
                rate_limit_delay=1.5,  # Slightly slower for smaller site
                timeout=30.0,
                max_retries=3,
                cache_enabled=True
            )
        super().__init__(config)

    async def scrape_all(self, max_terms: Optional[int] = None) -> List[LegalTerm]:
        """
        Scrape all legal terms

        Args:
            max_terms: Maximum number of terms to scrape (None for all)

        Returns:
            List of LegalTerm objects
        """
        terms = []

        self.logger.info("Starting scrape of TheLawDictionary.org")

        # Get alphabetical index
        index_urls = self.get_alphabetical_urls()

        self.logger.info(f"Scraping {len(index_urls)} alphabetical sections")

        for letter, url in index_urls.items():
            self.logger.info(f"Scraping terms starting with '{letter}'...")

            letter_terms = await self.scrape_letter_section(url, letter)
            terms.extend(letter_terms)

            self.logger.info(f"  Found {len(letter_terms)} terms for letter '{letter}'")

            if max_terms and len(terms) >= max_terms:
                self.logger.info(f"Reached max_terms limit of {max_terms}")
                terms = terms[:max_terms]
                break

        self.logger.info(f"Successfully scraped {len(terms)} legal terms")
        return terms

    def get_alphabetical_urls(self) -> Dict[str, str]:
        """
        Generate URLs for each letter

        Returns:
            Dictionary mapping letters to URLs
        """
        urls = {}

        # TheLawDictionary.org uses /letter/{letter} format
        for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            urls[letter] = f"{self.BASE_URL}/letter/{letter.lower()}/"

        return urls

    async def scrape_letter_section(self, url: str, letter: str) -> List[LegalTerm]:
        """
        Scrape all terms from a single letter section

        Args:
            url: URL of the letter section
            letter: The letter being scraped

        Returns:
            List of LegalTerm objects
        """
        html = await self.fetch(url)

        if not html:
            self.logger.error(f"Failed to fetch {url}")
            return []

        soup = BeautifulSoup(html, 'lxml')
        terms = []

        # Find all term entries
        # TheLawDictionary typically uses specific HTML structure
        entries = self._find_term_entries(soup)

        for entry in entries:
            term = self._parse_term_entry(entry)
            if term:
                terms.append(term)

        return terms

    def _find_term_entries(self, soup: BeautifulSoup) -> List:
        """Find all term entries in the page"""
        entries = []

        # Try different selectors
        # Option 1: div with specific class
        entries = soup.find_all('div', class_='dictionary-entry')

        # Option 2: article tags
        if not entries:
            entries = soup.find_all('article')

        # Option 3: Look for links to term pages
        if not entries:
            # Find all links that go to term definitions
            links = soup.find_all('a', href=re.compile(r'/[\w-]+/$'))
            entries = links

        return entries

    def _parse_term_entry(self, entry) -> Optional[LegalTerm]:
        """
        Parse a single term entry

        Args:
            entry: BeautifulSoup element

        Returns:
            LegalTerm object or None
        """
        try:
            # Extract term name
            term_name = None

            # Try to find term in heading
            heading = entry.find(['h1', 'h2', 'h3', 'h4'])
            if heading:
                term_name = heading.get_text().strip()

            # Try to find in link
            if not term_name and entry.name == 'a':
                term_name = entry.get_text().strip()

            # Try to find in title attribute
            if not term_name:
                term_name = entry.get('title', '').strip()

            if not term_name:
                return None

            # Extract definition
            definition = self._extract_definition(entry)

            if not definition:
                # If no definition in entry, need to fetch the full page
                url = self._get_term_url(entry, term_name)
                if url:
                    definition = await self.fetch_term_definition(url)

            if not definition:
                return None

            # Build metadata
            metadata = {
                "scrape_date": datetime.now().isoformat(),
                "source_name": "TheLawDictionary (Black's 2nd Ed.)",
                "source_edition": "Black's Law Dictionary 2nd Edition"
            }

            return LegalTerm(
                term=term_name,
                definition=definition,
                jurisdiction="general",
                source="TheLawDictionary",
                source_url=self._get_term_url(entry, term_name) or "",
                metadata=metadata
            )

        except Exception as e:
            self.logger.warning(f"Error parsing term entry: {e}")
            return None

    def _extract_definition(self, entry) -> str:
        """Extract definition from entry"""
        # Look for definition paragraph
        definition_p = entry.find('p', class_='definition')
        if definition_p:
            return definition_p.get_text().strip()

        # Look for any paragraph
        p = entry.find('p')
        if p:
            return p.get_text().strip()

        # Get all text
        text = entry.get_text().strip()

        # Remove term name from beginning if present
        lines = text.split('\n')
        if len(lines) > 1:
            return '\n'.join(lines[1:]).strip()

        return ""

    def _get_term_url(self, entry, term_name: str) -> Optional[str]:
        """Get URL for term"""
        # If entry is a link
        if entry.name == 'a' and entry.get('href'):
            href = entry['href']
            if href.startswith('http'):
                return href
            return f"{self.BASE_URL}{href}"

        # Find link in entry
        link = entry.find('a', href=True)
        if link:
            href = link['href']
            if href.startswith('http'):
                return href
            return f"{self.BASE_URL}{href}"

        # Generate URL from term name
        slug = term_name.lower().replace(' ', '-').replace('/', '-')
        return f"{self.BASE_URL}/{slug}/"

    async def fetch_term_definition(self, url: str) -> str:
        """
        Fetch full definition from term page

        Args:
            url: URL of term definition page

        Returns:
            Definition text
        """
        html = await self.fetch(url)

        if not html:
            return ""

        soup = BeautifulSoup(html, 'lxml')

        # Look for main content
        content = soup.find('div', class_='entry-content') or soup.find('main') or soup

        # Find definition paragraphs
        paragraphs = content.find_all('p')

        definition = []
        for p in paragraphs:
            text = p.get_text().strip()
            if len(text) > 20:  # Skip very short paragraphs
                definition.append(text)

        return ' '.join(definition)

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
    scraper = LawDictScraper()

    try:
        # Scrape first 10 terms as a test
        terms = await scraper.scrape_all(max_terms=10)

        print(f"\nScraped {len(terms)} legal terms:")
        print("=" * 80)

        for term in terms:
            print(f"\nTerm: {term.term}")
            print(f"Definition: {term.definition[:200]}..." if len(term.definition) > 200 else f"Definition: {term.definition}")
            print(f"Source: {term.source_url}")
            print("-" * 80)

        print(f"\nStats: {scraper.get_stats()}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
