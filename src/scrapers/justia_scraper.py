"""
Scraper for Justia.com legal database.
Justia provides free access to state statutes for all 50 US states.
"""

import re
from typing import List, Optional, Dict, Any
from urllib.parse import urljoin, urlparse
import logging

from .base_scraper import BaseScraper, ScrapedStatute, ScraperConfig, US_STATES

logger = logging.getLogger(__name__)


class JustiaScraper(BaseScraper):
    """
    Scraper for Justia.com state codes.

    Base URL structure:
    - State codes index: https://law.justia.com/codes/{state_name}/
    - Individual statutes: https://law.justia.com/codes/{state_name}/{code}/{section}/

    Example:
    - California: https://law.justia.com/codes/california/
    - CA Penal Code: https://law.justia.com/codes/california/2022/code-pen/
    """

    BASE_URL = "https://law.justia.com"

    def __init__(self, config: Optional[ScraperConfig] = None):
        """Initialize Justia scraper."""
        super().__init__(config)
        self.state_url_map = self._build_state_url_map()

    def _build_state_url_map(self) -> Dict[str, str]:
        """
        Build mapping of state codes to Justia URLs.

        Returns:
            Dictionary mapping state code to Justia URL
        """
        url_map = {}
        for code, name in US_STATES.items():
            # Justia uses lowercase state names with hyphens
            state_slug = name.lower().replace(' ', '-')
            url_map[code] = f"{self.BASE_URL}/codes/{state_slug}/"
        return url_map

    async def scrape_state(
        self,
        state_code: str,
        max_statutes: Optional[int] = None,
        sample_mode: bool = False
    ) -> List[ScrapedStatute]:
        """
        Scrape all statutes for a given state from Justia.

        Args:
            state_code: Two-letter state code (e.g., 'CA', 'NY')
            max_statutes: Maximum number of statutes to scrape (for testing)
            sample_mode: If True, only scrape first statute from each code section

        Returns:
            List of scraped statutes
        """
        state_code = state_code.upper()
        if state_code not in self.state_url_map:
            raise ValueError(f"Invalid state code: {state_code}")

        state_url = self.state_url_map[state_code]
        logger.info(f"Scraping {US_STATES[state_code]} from {state_url}")

        try:
            # Get the main state codes page
            html = await self.fetch_page(state_url)
            soup = self.parse_html(html)

            # Find all code sections (e.g., Penal Code, Civil Code, etc.)
            code_links = self._extract_code_links(soup, state_url)
            logger.info(f"Found {len(code_links)} code sections for {state_code}")

            statutes = []

            for code_name, code_url in code_links.items():
                logger.info(f"Scraping {code_name} from {code_url}")

                if sample_mode:
                    # Just get one statute from this code section
                    sample_statutes = await self._scrape_code_section_sample(
                        state_code, code_name, code_url
                    )
                    statutes.extend(sample_statutes[:1])
                else:
                    # Get all statutes from this code section
                    code_statutes = await self._scrape_code_section(
                        state_code, code_name, code_url
                    )
                    statutes.extend(code_statutes)

                # Check max statutes limit
                if max_statutes and len(statutes) >= max_statutes:
                    logger.info(f"Reached max_statutes limit: {max_statutes}")
                    statutes = statutes[:max_statutes]
                    break

            self.stats["items_scraped"] = len(statutes)
            logger.info(f"Scraped {len(statutes)} total statutes for {state_code}")

            return statutes

        except Exception as e:
            logger.error(f"Failed to scrape state {state_code}: {str(e)}")
            raise

    def _extract_code_links(self, soup, base_url: str) -> Dict[str, str]:
        """
        Extract links to different code sections (e.g., Penal, Civil, etc.).

        Args:
            soup: BeautifulSoup object of the state codes index page
            base_url: Base URL for resolving relative links

        Returns:
            Dictionary mapping code names to URLs
        """
        code_links = {}

        # Justia typically lists codes in a specific div or list structure
        # Look for links that contain '/codes/' in the path
        for link in soup.find_all('a', href=True):
            href = link['href']

            # Skip if not a code link
            if '/codes/' not in href:
                continue

            # Get absolute URL
            full_url = urljoin(base_url, href)

            # Extract code name from link text
            code_name = self.clean_text(link.get_text())

            if code_name and full_url not in code_links.values():
                # Avoid duplicate URLs
                code_links[code_name] = full_url

        return code_links

    async def _scrape_code_section_sample(
        self,
        state_code: str,
        code_name: str,
        code_url: str
    ) -> List[ScrapedStatute]:
        """
        Scrape just a sample statute from a code section (for testing).

        Args:
            state_code: State code
            code_name: Name of the code section
            code_url: URL of the code section

        Returns:
            List with one sample statute
        """
        try:
            html = await self.fetch_page(code_url)
            soup = self.parse_html(html)

            # Find first statute link
            statute_links = self._extract_statute_links(soup, code_url)

            if statute_links:
                first_url = list(statute_links.values())[0]
                statute = await self.scrape_statute(first_url, state_code, code_name)
                return [statute] if statute else []

            return []

        except Exception as e:
            logger.error(f"Failed to scrape sample from {code_name}: {str(e)}")
            return []

    async def _scrape_code_section(
        self,
        state_code: str,
        code_name: str,
        code_url: str
    ) -> List[ScrapedStatute]:
        """
        Scrape all statutes from a specific code section.

        Args:
            state_code: State code
            code_name: Name of the code section (e.g., "Penal Code")
            code_url: URL of the code section

        Returns:
            List of scraped statutes
        """
        statutes = []

        try:
            html = await self.fetch_page(code_url)
            soup = self.parse_html(html)

            # Extract all statute links from this code section
            statute_links = self._extract_statute_links(soup, code_url)
            logger.info(f"Found {len(statute_links)} statutes in {code_name}")

            # Scrape each statute
            for section_name, statute_url in statute_links.items():
                try:
                    statute = await self.scrape_statute(
                        statute_url,
                        state_code,
                        code_name,
                        section_name
                    )
                    if statute:
                        statutes.append(statute)

                except Exception as e:
                    logger.warning(f"Failed to scrape {statute_url}: {str(e)}")
                    continue

        except Exception as e:
            logger.error(f"Failed to scrape code section {code_name}: {str(e)}")

        return statutes

    def _extract_statute_links(self, soup, base_url: str) -> Dict[str, str]:
        """
        Extract individual statute links from a code section page.

        Args:
            soup: BeautifulSoup object
            base_url: Base URL for resolving relative links

        Returns:
            Dictionary mapping section names to URLs
        """
        statute_links = {}

        # Look for statute/section links
        # Justia typically has these in ordered lists or tables
        for link in soup.find_all('a', href=True):
            href = link['href']

            # Skip navigation and non-statute links
            if any(skip in href for skip in ['#', 'javascript:', 'mailto:']):
                continue

            # Look for section patterns (varies by state)
            # Common patterns: "Section 123", "§ 123", "123.45", etc.
            link_text = self.clean_text(link.get_text())

            if link_text and len(link_text) > 0:
                full_url = urljoin(base_url, href)

                # Avoid duplicate URLs
                if full_url not in statute_links.values():
                    statute_links[link_text] = full_url

        return statute_links

    async def scrape_statute(
        self,
        url: str,
        state_code: Optional[str] = None,
        code_name: Optional[str] = None,
        section_name: Optional[str] = None
    ) -> Optional[ScrapedStatute]:
        """
        Scrape a single statute from Justia.

        Args:
            url: URL of the statute page
            state_code: State code (extracted from URL if not provided)
            code_name: Name of the code section
            section_name: Section identifier

        Returns:
            ScrapedStatute or None if failed
        """
        try:
            html = await self.fetch_page(url)
            soup = self.parse_html(html)

            # Extract state from URL if not provided
            if not state_code:
                state_code = self._extract_state_from_url(url)

            # Extract statute metadata and content
            statute_data = self._parse_statute_page(soup, url)

            # Build statute object
            statute = ScrapedStatute(
                state=state_code or "UNKNOWN",
                statute_number=statute_data.get("number", section_name or "UNKNOWN"),
                title=statute_data.get("title", section_name or "Untitled"),
                full_text=statute_data.get("text", ""),
                chapter=code_name,
                section=section_name,
                effective_date=statute_data.get("effective_date"),
                last_amended=statute_data.get("last_amended"),
                source_url=url,
                jurisdiction="state",
                metadata={
                    "source": "justia",
                    "code_name": code_name,
                    "section_name": section_name,
                    **statute_data.get("extra_metadata", {})
                }
            )

            # Validate before returning
            errors = self.validate_statute(statute)
            if errors:
                logger.warning(f"Validation errors for {url}: {errors}")
                # Return anyway, but log the issues
                # In production, you might want to skip invalid statutes

            return statute

        except Exception as e:
            logger.error(f"Failed to scrape statute {url}: {str(e)}")
            return None

    def _extract_state_from_url(self, url: str) -> str:
        """
        Extract state code from Justia URL.

        Args:
            url: Justia URL

        Returns:
            Two-letter state code
        """
        # URL format: https://law.justia.com/codes/{state-name}/...
        parsed = urlparse(url)
        path_parts = parsed.path.strip('/').split('/')

        if len(path_parts) >= 2 and path_parts[0] == 'codes':
            state_name = path_parts[1].replace('-', ' ').title()

            # Reverse lookup in US_STATES
            for code, name in US_STATES.items():
                if name.lower() == state_name.lower():
                    return code

        return "UNKNOWN"

    def _parse_statute_page(self, soup, url: str) -> Dict[str, Any]:
        """
        Parse a statute page and extract all relevant information.

        Args:
            soup: BeautifulSoup object of statute page
            url: URL of the page

        Returns:
            Dictionary with statute data
        """
        data = {
            "number": "",
            "title": "",
            "text": "",
            "effective_date": None,
            "last_amended": None,
            "extra_metadata": {}
        }

        # Extract title - usually in <h1> or <h2>
        title_tag = soup.find(['h1', 'h2'])
        if title_tag:
            data["title"] = self.clean_text(title_tag.get_text())

        # Extract statute number from title or URL
        # Common patterns: "Section 123", "§ 123", "123.45"
        number_match = re.search(r'(?:Section|§)\s*([\d.-]+)', data["title"])
        if number_match:
            data["number"] = number_match.group(1)
        else:
            # Try to extract from URL
            url_match = re.search(r'/(\d+(?:-\d+)*(?:\.\d+)?)/?$', url)
            if url_match:
                data["number"] = url_match.group(1)

        # Extract main statute text
        # Justia typically puts statute text in specific div classes
        text_container = soup.find('div', class_=re.compile(r'statute|law-text|content'))
        if not text_container:
            # Fallback: get all paragraphs
            text_container = soup.find('body')

        if text_container:
            # Get text from paragraphs
            paragraphs = text_container.find_all(['p', 'div'], recursive=True)
            text_parts = []

            for p in paragraphs:
                # Skip navigation and metadata
                if p.find_parent(['nav', 'header', 'footer']):
                    continue

                text = self.clean_text(p.get_text())
                if text and len(text) > 10:  # Skip very short fragments
                    text_parts.append(text)

            data["text"] = "\n\n".join(text_parts)

        # Look for effective date or last amended info
        # Often in metadata sections
        date_patterns = [
            r'(?:Effective|Amended)\s+(?:Date)?:?\s*(\w+\s+\d+,\s+\d{4})',
            r'(?:Last\s+)?(?:Amended|Modified):\s*(\d{4})',
        ]

        page_text = soup.get_text()
        for pattern in date_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                data["last_amended"] = match.group(1)
                break

        return data

    async def test_scrape_single_state(self, state_code: str, max_statutes: int = 5):
        """
        Test scraping a single state with limited statutes.
        Useful for debugging and testing.

        Args:
            state_code: State to test
            max_statutes: Maximum statutes to scrape

        Returns:
            List of scraped statutes
        """
        logger.info(f"TEST MODE: Scraping {state_code} (max {max_statutes} statutes)")

        async with self:
            statutes = await self.scrape_state(
                state_code,
                max_statutes=max_statutes,
                sample_mode=True
            )

            logger.info(f"Test complete: {len(statutes)} statutes scraped")

            # Print sample
            if statutes:
                sample = statutes[0]
                logger.info(f"\nSample statute:")
                logger.info(f"  State: {sample.state}")
                logger.info(f"  Number: {sample.statute_number}")
                logger.info(f"  Title: {sample.title[:100]}...")
                logger.info(f"  Text length: {len(sample.full_text)} chars")
                logger.info(f"  URL: {sample.source_url}")

            return statutes
