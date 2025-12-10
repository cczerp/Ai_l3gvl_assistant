"""
US Constitution and Bill of Rights Scraper

Scrapes the full text of the US Constitution, Bill of Rights, and all amendments
from the National Archives (archives.gov) - the official authoritative source.

Source: https://www.archives.gov/founding-docs
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
class ConstitutionalDocument:
    """Represents a constitutional document"""
    document_type: str  # 'constitution', 'amendment', 'bill_of_rights'
    article_number: Optional[str] = None
    section_number: Optional[str] = None
    amendment_number: Optional[int] = None
    title: str = ""
    full_text: str = ""
    ratified_date: Optional[str] = None
    source_url: str = ""
    metadata: Dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class ConstitutionScraper(BaseScraper):
    """
    Scraper for US Constitution, Bill of Rights, and Amendments from National Archives
    """

    BASE_URL = "https://www.archives.gov"

    # URLs for different constitutional documents
    URLS = {
        "constitution": "https://www.archives.gov/founding-docs/constitution-transcript",
        "bill_of_rights": "https://www.archives.gov/founding-docs/bill-of-rights-transcript",
        "amendments": "https://www.archives.gov/founding-docs/amendments-11-27"
    }

    # Ratification dates for amendments
    AMENDMENT_DATES = {
        1: "1791-12-15",  # Bill of Rights (1-10)
        2: "1791-12-15",
        3: "1791-12-15",
        4: "1791-12-15",
        5: "1791-12-15",
        6: "1791-12-15",
        7: "1791-12-15",
        8: "1791-12-15",
        9: "1791-12-15",
        10: "1791-12-15",
        11: "1795-02-07",
        12: "1804-06-15",
        13: "1865-12-06",
        14: "1868-07-09",
        15: "1870-02-03",
        16: "1913-02-03",
        17: "1913-04-08",
        18: "1919-01-16",  # Prohibition
        19: "1920-08-18",  # Women's suffrage
        20: "1933-01-23",
        21: "1933-12-05",  # Repeal of Prohibition
        22: "1951-02-27",
        23: "1961-03-29",
        24: "1964-01-23",
        25: "1967-02-10",
        26: "1971-07-01",
        27: "1992-05-07"
    }

    def __init__(self, config: Optional[ScraperConfig] = None):
        """Initialize the Constitution scraper"""
        if config is None:
            config = ScraperConfig(
                rate_limit_delay=1.0,  # Respectful 1 second delay
                timeout=30.0,
                max_retries=3,
                cache_enabled=True
            )
        super().__init__(config)

    async def scrape_all(self) -> List[ConstitutionalDocument]:
        """
        Scrape all constitutional documents

        Returns:
            List of ConstitutionalDocument objects
        """
        documents = []

        self.logger.info("Starting scrape of US constitutional documents")

        # Scrape Constitution (articles)
        self.logger.info("Scraping Constitution articles...")
        constitution_docs = await self.scrape_constitution()
        documents.extend(constitution_docs)

        # Scrape Bill of Rights (first 10 amendments)
        self.logger.info("Scraping Bill of Rights...")
        bill_of_rights_docs = await self.scrape_bill_of_rights()
        documents.extend(bill_of_rights_docs)

        # Scrape remaining amendments (11-27)
        self.logger.info("Scraping Amendments 11-27...")
        amendment_docs = await self.scrape_amendments()
        documents.extend(amendment_docs)

        self.logger.info(f"Successfully scraped {len(documents)} constitutional documents")
        return documents

    async def scrape_constitution(self) -> List[ConstitutionalDocument]:
        """Scrape the main Constitution (articles)"""
        url = self.URLS["constitution"]
        html = await self.fetch(url)

        if not html:
            self.logger.error(f"Failed to fetch Constitution from {url}")
            return []

        soup = BeautifulSoup(html, 'lxml')
        documents = []

        # Find the main content area
        content = soup.find('div', class_='page-content') or soup.find('main')

        if not content:
            self.logger.error("Could not find content area in Constitution page")
            return []

        # Extract preamble
        preamble_text = self._extract_preamble(content)
        if preamble_text:
            documents.append(ConstitutionalDocument(
                document_type="constitution",
                article_number="Preamble",
                title="Preamble to the United States Constitution",
                full_text=preamble_text,
                ratified_date="1788-06-21",  # Constitution ratified
                source_url=url,
                metadata={
                    "scrape_date": datetime.now().isoformat(),
                    "source_name": "National Archives",
                    "document_section": "preamble"
                }
            ))

        # Extract articles (I through VII)
        articles = self._extract_articles(content)
        for article_num, article_data in articles.items():
            documents.append(ConstitutionalDocument(
                document_type="constitution",
                article_number=article_num,
                title=f"Article {article_num} - {article_data['title']}",
                full_text=article_data['text'],
                ratified_date="1788-06-21",
                source_url=url,
                metadata={
                    "scrape_date": datetime.now().isoformat(),
                    "source_name": "National Archives",
                    "document_section": "article",
                    "sections_count": article_data.get('sections_count', 0)
                }
            ))

        return documents

    async def scrape_bill_of_rights(self) -> List[ConstitutionalDocument]:
        """Scrape the Bill of Rights (First 10 Amendments)"""
        url = self.URLS["bill_of_rights"]
        html = await self.fetch(url)

        if not html:
            self.logger.error(f"Failed to fetch Bill of Rights from {url}")
            return []

        soup = BeautifulSoup(html, 'lxml')
        documents = []

        content = soup.find('div', class_='page-content') or soup.find('main')

        if not content:
            self.logger.error("Could not find content area in Bill of Rights page")
            return []

        # Extract each of the first 10 amendments
        amendments = self._extract_amendments_from_content(content, range(1, 11))

        for amendment_num, amendment_data in amendments.items():
            documents.append(ConstitutionalDocument(
                document_type="bill_of_rights",
                amendment_number=amendment_num,
                title=f"Amendment {amendment_num} - {amendment_data['title']}",
                full_text=amendment_data['text'],
                ratified_date=self.AMENDMENT_DATES.get(amendment_num),
                source_url=url,
                metadata={
                    "scrape_date": datetime.now().isoformat(),
                    "source_name": "National Archives",
                    "document_section": "bill_of_rights",
                    "part_of": "First Ten Amendments"
                }
            ))

        return documents

    async def scrape_amendments(self) -> List[ConstitutionalDocument]:
        """Scrape Amendments 11-27"""
        url = self.URLS["amendments"]
        html = await self.fetch(url)

        if not html:
            self.logger.error(f"Failed to fetch Amendments from {url}")
            return []

        soup = BeautifulSoup(html, 'lxml')
        documents = []

        content = soup.find('div', class_='page-content') or soup.find('main')

        if not content:
            self.logger.error("Could not find content area in Amendments page")
            return []

        # Extract amendments 11-27
        amendments = self._extract_amendments_from_content(content, range(11, 28))

        for amendment_num, amendment_data in amendments.items():
            documents.append(ConstitutionalDocument(
                document_type="amendment",
                amendment_number=amendment_num,
                title=f"Amendment {amendment_num} - {amendment_data['title']}",
                full_text=amendment_data['text'],
                ratified_date=self.AMENDMENT_DATES.get(amendment_num),
                source_url=url,
                metadata={
                    "scrape_date": datetime.now().isoformat(),
                    "source_name": "National Archives",
                    "document_section": "amendment",
                    "is_repealed": amendment_num == 18  # Prohibition was repealed
                }
            ))

        return documents

    def _extract_preamble(self, content) -> str:
        """Extract the Preamble text"""
        # Look for text starting with "We the People"
        text = content.get_text()
        match = re.search(r'(We the People.*?establish this Constitution.*?\.)', text, re.DOTALL | re.IGNORECASE)
        if match:
            return self._clean_text(match.group(1))
        return ""

    def _extract_articles(self, content) -> Dict[str, Dict]:
        """Extract all articles from the Constitution"""
        articles = {}

        # Roman numerals for articles I through VII
        roman_numerals = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII']

        text = content.get_text()

        for i, roman in enumerate(roman_numerals):
            # Pattern to find article heading and content
            pattern = rf'Article\.?\s*{roman}[.\s]+(.*?)(?=Article\.?\s*(?:[IV]+|$))'
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)

            if match:
                article_text = self._clean_text(match.group(0))

                # Try to extract title
                title_match = re.search(rf'Article\.?\s*{roman}[.\s]+([\w\s]+)', article_text)
                title = title_match.group(1).strip() if title_match else f"Article {roman}"

                # Count sections
                sections_count = len(re.findall(r'Section\.?\s*\d+', article_text, re.IGNORECASE))

                articles[roman] = {
                    'title': title,
                    'text': article_text,
                    'sections_count': sections_count
                }

        return articles

    def _extract_amendments_from_content(self, content, amendment_range) -> Dict[int, Dict]:
        """Extract amendments from content"""
        amendments = {}
        text = content.get_text()

        for num in amendment_range:
            # Pattern to find amendment
            pattern = rf'Amendment\s*{num}[.\s]+(.*?)(?=Amendment\s*\d+|$)'
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)

            if match:
                amendment_text = self._clean_text(match.group(0))

                # Extract title (first line or notable keywords)
                title = self._get_amendment_title(num, amendment_text)

                amendments[num] = {
                    'title': title,
                    'text': amendment_text
                }

        return amendments

    def _get_amendment_title(self, num: int, text: str) -> str:
        """Get descriptive title for amendment"""
        # Known amendment titles/topics
        titles = {
            1: "Freedom of Religion, Speech, Press, Assembly, and Petition",
            2: "Right to Bear Arms",
            3: "Quartering of Soldiers",
            4: "Search and Seizure",
            5: "Due Process, Self-Incrimination, Double Jeopardy",
            6: "Right to Fair Trial",
            7: "Trial by Jury in Civil Cases",
            8: "Cruel and Unusual Punishment",
            9: "Rights Retained by the People",
            10: "Powers Reserved to the States",
            11: "Judicial Limits",
            12: "Electoral College Procedures",
            13: "Abolition of Slavery",
            14: "Civil Rights, Due Process, Equal Protection",
            15: "Right to Vote - Race",
            16: "Federal Income Tax",
            17: "Direct Election of Senators",
            18: "Prohibition of Alcohol",
            19: "Women's Suffrage",
            20: "Presidential Terms and Succession",
            21: "Repeal of Prohibition",
            22: "Presidential Term Limits",
            23: "Electoral Votes for Washington, D.C.",
            24: "Abolition of Poll Taxes",
            25: "Presidential Succession",
            26: "Voting Age Set to 18",
            27: "Congressional Pay Changes"
        }
        return titles.get(num, f"Amendment {num}")

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
            "total_documents": self.stats.get("total_documents", 0)
        }


async def main():
    """Example usage"""
    scraper = ConstitutionScraper()

    try:
        documents = await scraper.scrape_all()

        print(f"\nScraped {len(documents)} constitutional documents:")
        print("=" * 80)

        for doc in documents:
            print(f"\n{doc.title}")
            print(f"Type: {doc.document_type}")
            if doc.amendment_number:
                print(f"Amendment: {doc.amendment_number}")
            if doc.article_number:
                print(f"Article: {doc.article_number}")
            print(f"Ratified: {doc.ratified_date}")
            print(f"Text length: {len(doc.full_text)} characters")
            print(f"Source: {doc.source_url}")
            print("-" * 80)

        print(f"\nStats: {scraper.get_stats()}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
