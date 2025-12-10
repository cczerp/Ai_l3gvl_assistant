"""
Base scraper class with common functionality for all legal data scrapers.
"""

import asyncio
import os
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
from pathlib import Path

import httpx
from bs4 import BeautifulSoup
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

logger = logging.getLogger(__name__)


def _default_user_agent() -> str:
    """
    Resolve the user agent string for outbound HTTP requests.

    Prefer the USER_AGENT environment variable (populated via .env) so users
    can tweak scraper identity without code changes, but fall back to a
    mainstream Chromium signature to reduce the chance of being blocked.
    """
    return os.environ.get(
        "USER_AGENT",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/121.0.0.0 Safari/537.36"
    )


@dataclass
class ScraperConfig:
    """Configuration for scrapers."""
    max_retries: int = 3
    timeout: int = 30
    rate_limit_delay: float = 1.0  # seconds between requests
    max_concurrent_requests: int = 5
    user_agent: str = field(default_factory=_default_user_agent)
    cache_dir: Optional[Path] = None
    respect_robots_txt: bool = True
    default_headers: Dict[str, str] = field(default_factory=dict)
    enable_playwright: bool = False
    playwright_storage_state: Optional[Path] = None

    def __post_init__(self):
        if self.cache_dir:
            self.cache_dir = Path(self.cache_dir)
            self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Allow overriding via environment variables
        env_timeout = os.environ.get("REQUEST_TIMEOUT")
        if env_timeout:
            try:
                self.timeout = int(env_timeout)
            except ValueError:
                logger.warning("Invalid REQUEST_TIMEOUT=%s; using default", env_timeout)

        env_retries = os.environ.get("MAX_RETRIES")
        if env_retries:
            try:
                self.max_retries = int(env_retries)
            except ValueError:
                logger.warning("Invalid MAX_RETRIES=%s; using default", env_retries)

        env_delay = os.environ.get("SCRAPING_DELAY")
        if env_delay:
            try:
                self.rate_limit_delay = float(env_delay)
            except ValueError:
                logger.warning("Invalid SCRAPING_DELAY=%s; using default", env_delay)

        env_playwright = os.environ.get("ENABLE_PLAYWRIGHT")
        if env_playwright:
            self.enable_playwright = env_playwright.strip().lower() in {"1", "true", "yes"}

        env_storage = os.environ.get("PLAYWRIGHT_STORAGE_STATE")
        if env_storage:
            self.playwright_storage_state = Path(env_storage).expanduser()


@dataclass
class ScrapedStatute:
    """Represents a scraped statute."""
    state: str
    statute_number: str
    title: str
    full_text: str
    chapter: Optional[str] = None
    section: Optional[str] = None
    effective_date: Optional[str] = None
    last_amended: Optional[str] = None
    source_url: str = ""
    jurisdiction: str = "state"
    metadata: Dict[str, Any] = field(default_factory=dict)
    scraped_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database insertion."""
        return {
            "state": self.state,
            "statute_number": self.statute_number,
            "title": self.title,
            "full_text": self.full_text,
            "chapter": self.chapter,
            "section": self.section,
            "effective_date": self.effective_date,
            "last_amended": self.last_amended,
            "source_url": self.source_url,
            "jurisdiction": self.jurisdiction,
            "metadata": self.metadata,
            "scraped_at": self.scraped_at.isoformat()
        }


class BaseScraper(ABC):
    """
    Base class for all legal data scrapers.
    Provides common functionality like rate limiting, retries, and caching.
    """

    def __init__(self, config: Optional[ScraperConfig] = None):
        """
        Initialize the scraper.

        Args:
            config: Scraper configuration
        """
        self.config = config or ScraperConfig()
        self.session: Optional[httpx.AsyncClient] = None
        self._playwright = None
        self._playwright_browser = None
        self._playwright_context = None
        self.request_times: List[float] = []
        self.stats = {
            "requests_made": 0,
            "requests_failed": 0,
            "items_scraped": 0,
            "start_time": None,
            "end_time": None
        }

    async def __aenter__(self):
        """Async context manager entry."""
        await self.start_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close_session()

    async def start_session(self):
        """Start HTTP session."""
        if self.session is None:
            headers = {
                "User-Agent": self.config.user_agent,
                "Accept": (
                    "text/html,application/xhtml+xml,application/xml;q=0.9,"
                    "image/avif,image/webp,image/apng,*/*;q=0.8"
                ),
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
                "Sec-Ch-Ua": '"Not.A/Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": '"Windows"',
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-User": "?1",
                "Sec-Fetch-Dest": "document",
            }
            headers.update(self.config.default_headers)

            self.session = httpx.AsyncClient(
                timeout=self.config.timeout,
                headers=headers,
                follow_redirects=True,
                http2=True
            )
            self.stats["start_time"] = datetime.now()
            logger.info(f"Started scraper session: {self.__class__.__name__}")

    async def close_session(self):
        """Close HTTP session."""
        if self.session:
            await self.session.aclose()
            self.session = None
            self.stats["end_time"] = datetime.now()
            logger.info(f"Closed scraper session: {self.__class__.__name__}")
            self._log_stats()
        await self._close_playwright()

    def _log_stats(self):
        """Log scraping statistics."""
        duration = (self.stats["end_time"] - self.stats["start_time"]).total_seconds()
        logger.info(
            f"Scraping stats - "
            f"Requests: {self.stats['requests_made']}, "
            f"Failed: {self.stats['requests_failed']}, "
            f"Items: {self.stats['items_scraped']}, "
            f"Duration: {duration:.2f}s"
        )

    async def _rate_limit(self):
        """Implement rate limiting between requests."""
        now = time.time()

        # Remove old request times (older than 60 seconds)
        self.request_times = [t for t in self.request_times if now - t < 60]

        # Check if we need to wait
        if self.request_times:
            time_since_last = now - self.request_times[-1]
            if time_since_last < self.config.rate_limit_delay:
                wait_time = self.config.rate_limit_delay - time_since_last
                logger.debug(f"Rate limiting: waiting {wait_time:.2f}s")
                await asyncio.sleep(wait_time)

        self.request_times.append(time.time())

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError))
    )
    async def fetch_page(self, url: str, **kwargs) -> str:
        """
        Fetch a web page with rate limiting and retries.

        Args:
            url: URL to fetch
            **kwargs: Additional arguments for httpx.get()

        Returns:
            Page HTML content
        """
        if not self.session:
            await self.start_session()

        await self._rate_limit()

        try:
            logger.debug(f"Fetching: {url}")
            response = await self.session.get(url, **kwargs)
            response.raise_for_status()
            self.stats["requests_made"] += 1

            # Cache if configured
            if self.config.cache_dir:
                self._cache_page(url, response.text)

            return response.text

        except httpx.HTTPStatusError as e:
            self.stats["requests_failed"] += 1
            status = e.response.status_code if e.response is not None else None
            logger.error(f"Failed to fetch {url}: HTTP {status} - {e}")

            if (
                self.config.enable_playwright
                and status in {403, 429, 503}
            ):
                logger.warning(
                    "Falling back to Playwright for %s due to HTTP %s",
                    url,
                    status
                )
                return await self._fetch_with_playwright(url)

            raise

        except Exception as e:
            self.stats["requests_failed"] += 1
            logger.error(f"Failed to fetch {url}: {str(e)}")
            raise

    def _cache_page(self, url: str, content: str):
        """Cache a page to disk."""
        if not self.config.cache_dir:
            return

        # Create safe filename from URL
        filename = url.replace("https://", "").replace("http://", "")
        filename = "".join(c if c.isalnum() or c in "._-" else "_" for c in filename)
        cache_file = self.config.cache_dir / f"{filename}.html"

        try:
            cache_file.write_text(content, encoding="utf-8")
            logger.debug(f"Cached page: {cache_file}")
        except Exception as e:
            logger.warning(f"Failed to cache page: {str(e)}")

    def parse_html(self, html: str) -> BeautifulSoup:
        """
        Parse HTML content with BeautifulSoup.

        Args:
            html: HTML content

        Returns:
            BeautifulSoup object
        """
        return BeautifulSoup(html, 'lxml')

    async def _ensure_playwright(self):
        """Start a Playwright browser context if enabled."""
        if self._playwright_context or not self.config.enable_playwright:
            return

        try:
            from playwright.async_api import async_playwright  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                "Playwright support requested but playwright is not installed. "
                "Install it with `pip install playwright` and execute `playwright install`."
            ) from exc

        self._playwright = await async_playwright().start()
        self._playwright_browser = await self._playwright.chromium.launch(headless=True)
        storage_state = None
        if self.playwright_storage_state:
            storage_path = self.playwright_storage_state
            if storage_path.exists():
                storage_state = str(storage_path)
            else:
                logger.warning("Playwright storage state not found at %s", storage_path)

        self._playwright_context = await self._playwright_browser.new_context(
            user_agent=self.config.user_agent,
            viewport={"width": 1366, "height": 768},
            locale="en-US",
            storage_state=storage_state,
        )
        logger.info("Playwright context initialized")

    async def _close_playwright(self):
        """Clean up Playwright resources."""
        if self._playwright_context:
            await self._playwright_context.close()
            self._playwright_context = None
        if self._playwright_browser:
            await self._playwright_browser.close()
            self._playwright_browser = None
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None

    async def _fetch_with_playwright(self, url: str) -> str:
        """Fetch a page using Playwright when HTTP requests are blocked."""
        await self._ensure_playwright()

        page = await self._playwright_context.new_page()
        try:
            await page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=self.config.timeout * 1000,
            )
            try:
                await page.wait_for_load_state("networkidle", timeout=self.config.timeout * 1000)
            except Exception:
                # ignore if network idle never fires
                pass

            # Cloudflare / CDN challenge page detection
            page_title = await page.title()
            if "Just a moment" in page_title:
                logger.debug("Detected challenge page, waiting for completion...")
                await page.wait_for_timeout(6000)
                try:
                    await page.wait_for_load_state("load", timeout=5000)
                except Exception:
                    pass

            content = await page.content()
            self.stats["requests_made"] += 1

            if self.config.cache_dir:
                self._cache_page(url, content)

            return content
        finally:
            await page.close()

    @abstractmethod
    async def scrape_state(self, state_code: str) -> List[ScrapedStatute]:
        """
        Scrape all statutes for a given state.
        Must be implemented by subclasses.

        Args:
            state_code: Two-letter state code (e.g., 'CA', 'NY')

        Returns:
            List of scraped statutes
        """
        pass

    @abstractmethod
    async def scrape_statute(self, url: str) -> Optional[ScrapedStatute]:
        """
        Scrape a single statute from a URL.
        Must be implemented by subclasses.

        Args:
            url: URL of the statute

        Returns:
            Scraped statute or None if failed
        """
        pass

    async def scrape_multiple_states(
        self,
        state_codes: List[str],
        max_concurrent: Optional[int] = None
    ) -> Dict[str, List[ScrapedStatute]]:
        """
        Scrape multiple states concurrently.

        Args:
            state_codes: List of state codes to scrape
            max_concurrent: Maximum concurrent scraping tasks

        Returns:
            Dictionary mapping state codes to lists of statutes
        """
        max_concurrent = max_concurrent or self.config.max_concurrent_requests
        semaphore = asyncio.Semaphore(max_concurrent)

        async def scrape_with_semaphore(state_code: str):
            async with semaphore:
                logger.info(f"Starting scrape for state: {state_code}")
                try:
                    statutes = await self.scrape_state(state_code)
                    logger.info(f"Completed {state_code}: {len(statutes)} statutes")
                    return state_code, statutes
                except Exception as e:
                    logger.error(f"Failed to scrape {state_code}: {str(e)}")
                    return state_code, []

        results = await asyncio.gather(*[
            scrape_with_semaphore(state_code)
            for state_code in state_codes
        ])

        return dict(results)

    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text content.

        Args:
            text: Raw text

        Returns:
            Cleaned text
        """
        if not text:
            return ""

        # Remove excessive whitespace
        text = " ".join(text.split())

        # Remove common HTML entities that might slip through
        replacements = {
            "&nbsp;": " ",
            "&amp;": "&",
            "&lt;": "<",
            "&gt;": ">",
            "&quot;": '"',
            "&#39;": "'",
        }
        for old, new in replacements.items():
            text = text.replace(old, new)

        return text.strip()

    def validate_statute(self, statute: ScrapedStatute) -> List[str]:
        """
        Validate a scraped statute.

        Args:
            statute: Statute to validate

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        if not statute.state or len(statute.state) != 2:
            errors.append("Invalid or missing state code")

        if not statute.statute_number:
            errors.append("Missing statute number")

        if not statute.title:
            errors.append("Missing statute title")

        if not statute.full_text or len(statute.full_text) < 50:
            errors.append("Statute text too short or missing")

        if not statute.source_url:
            errors.append("Missing source URL")

        return errors


# US State codes for reference
US_STATES = {
    'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas',
    'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware',
    'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho',
    'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas',
    'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
    'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi',
    'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada',
    'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York',
    'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma',
    'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
    'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah',
    'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia',
    'WI': 'Wisconsin', 'WY': 'Wyoming', 'DC': 'District of Columbia'
}
