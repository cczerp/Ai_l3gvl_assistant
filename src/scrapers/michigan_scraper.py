"""
Scraper for Michigan Legislature official site (michiganlegislature.org).
"""

from __future__ import annotations

import logging
import re
from typing import List, Optional, Dict
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .base_scraper import BaseScraper, ScrapedStatute

logger = logging.getLogger(__name__)


class MichiganLegislatureScraper(BaseScraper):
    """
    Scrapes Michigan Compiled Laws directly from https://www.legislature.mi.gov.

    The hierarchy on the site is:
        Chapter Index -> Chapter -> Act/Grouping -> Individual Section
    We traverse this tree recursively until we reach statute pages (no table present).
    """

    STATE_CODE = "MI"
    BASE_URL = "https://www.legislature.mi.gov"
    CHAPTER_INDEX_PATH = "/Laws/ChapterIndex"

    async def scrape_state(
        self,
        state_code: str,
        max_statutes: Optional[int] = None,
        sample_mode: bool = False,
        max_statutes_per_chapter: Optional[int] = None,
    ) -> List[ScrapedStatute]:
        state_code = state_code.upper()
        if state_code != self.STATE_CODE:
            raise ValueError(
                f"{self.__class__.__name__} can only scrape {self.STATE_CODE}, "
                f"got {state_code}"
            )

        self._visited_urls: set[str] = set()
        statutes: List[ScrapedStatute] = []

        index_url = urljoin(self.BASE_URL, self.CHAPTER_INDEX_PATH)
        logger.info("Fetching Michigan chapter index: %s", index_url)
        html = await self.fetch_page(index_url)
        chapters = self._parse_listing_table(html)
        logger.info("Found %d Michigan chapters", len(chapters))

        per_chapter_limit = max_statutes_per_chapter
        for chapter in chapters:
            if self._limit_reached(statutes, max_statutes):
                break

            chapter_limit = None
            if per_chapter_limit:
                chapter_limit = min(
                    per_chapter_limit,
                    (max_statutes - len(statutes)) if max_statutes else per_chapter_limit,
                )

            logger.debug("Scraping chapter %s (%s)", chapter["title"], chapter["url"])
            await self._scrape_listing(
                chapter["url"],
                statutes,
                max_statutes=max_statutes,
                sample_mode=sample_mode,
                per_listing_limit=chapter_limit,
            )

        self.stats["items_scraped"] = len(statutes)
        return statutes

    async def _scrape_listing(
        self,
        url: str,
        results: List[ScrapedStatute],
        *,
        max_statutes: Optional[int],
        sample_mode: bool,
        per_listing_limit: Optional[int] = None,
    ) -> None:
        if self._limit_reached(results, max_statutes):
            return

        if url in self._visited_urls:
            return
        self._visited_urls.add(url)

        html = await self.fetch_page(url)
        soup = BeautifulSoup(html, "lxml")
        table = soup.select_one("table.table")

        if table:
            entries = self._parse_listing_table(soup)
            if sample_mode and entries:
                # keep traversal manageable during sample runs
                entries = entries[: min(3, len(entries))]

            if per_listing_limit:
                entries = entries[:per_listing_limit]

            for entry in entries:
                if self._limit_reached(results, max_statutes):
                    break
                await self._scrape_listing(
                    entry["url"],
                    results,
                    max_statutes=max_statutes,
                    sample_mode=sample_mode,
                )
            return

        statute = self._parse_statute_page(soup, url)
        if statute:
            results.append(statute)

    def _parse_listing_table(self, html_or_soup) -> List[Dict[str, str]]:
        if isinstance(html_or_soup, str):
            soup = BeautifulSoup(html_or_soup, "lxml")
        else:
            soup = html_or_soup

        table = soup.select_one("table.table")
        if not table:
            return []

        entries: List[Dict[str, str]] = []
        for row in table.select("tbody tr"):
            anchor = row.find("a")
            if not anchor or not anchor.get("href"):
                continue
            href = urljoin(self.BASE_URL, anchor["href"])
            title = anchor.get_text(" ", strip=True)
            entries.append({"title": title, "url": href})
        return entries

    def _parse_statute_page(self, soup: BeautifulSoup, url: str) -> Optional[ScrapedStatute]:
        main = soup.find("main")
        if not main:
            logger.warning("Missing <main> element when parsing %s", url)
            return None

        heading_text = ""
        heading = main.find("h1")
        if heading:
            heading_text = heading.get_text(strip=True)

        number_from_heading = self._extract_number_from_heading(heading_text)

        container = main.find("center")
        if container:
            container = container.parent
        else:
            # fallback to first substantial column
            container = main.find("div", class_="col-12") or main

        title_block = self._extract_title_block(container)
        statute_number = number_from_heading or title_block.get("number") or heading_text
        statute_title = title_block.get("title") or heading_text

        full_text = self._extract_body_text(container)
        if not full_text:
            logger.debug("Empty body for %s, skipping", url)
            return None

        return ScrapedStatute(
            state=self.STATE_CODE,
            statute_number=statute_number.strip() if statute_number else "",
            title=statute_title.strip() if statute_title else "",
            full_text=full_text.strip(),
            source_url=url,
            metadata={
                "source": "michigan_legislature",
                "heading": heading_text,
            },
        )

    @staticmethod
    def _extract_number_from_heading(heading: str) -> Optional[str]:
        if not heading:
            return None
        section_match = re.search(r"Section\s+([A-Za-z0-9.\-]+)", heading)
        if section_match:
            return section_match.group(1)

        article_match = re.search(
            r"Article\s+([IVXLC]+)\s+§\s*([A-Za-z0-9.\-]+)",
            heading,
            flags=re.IGNORECASE,
        )
        if article_match:
            numeral = article_match.group(1).upper()
            sec = article_match.group(2)
            return f"Article {numeral} § {sec}"

        return None

    @staticmethod
    def _extract_title_block(container) -> Dict[str, Optional[str]]:
        result: Dict[str, Optional[str]] = {"number": None, "title": None}
        if not container:
            return result

        for bold in container.find_all("b"):
            text = bold.get_text(" ", strip=True)
            if text and text[0].isdigit():
                parts = text.split(" ", 1)
                result["number"] = parts[0]
                result["title"] = parts[1] if len(parts) > 1 else ""
                break
        return result

    @staticmethod
    def _extract_body_text(container) -> str:
        if not container:
            return ""

        skip_prefixes = {
            "Download Section",
            "Previous Section",
            "Next Section",
            "Download Chapter",
        }

        lines: List[str] = []
        raw_lines = container.get_text("\n", strip=True).splitlines()
        for line in raw_lines:
            line = line.strip()
            if not line:
                continue
            if any(line.startswith(prefix) for prefix in skip_prefixes):
                continue
            lines.append(line)

        # collapse duplicate whitespace-only markers
        cleaned: List[str] = []
        seen_empty = False
        for line in lines:
            if not line:
                if seen_empty:
                    continue
                seen_empty = True
            else:
                seen_empty = False
            cleaned.append(line)

        return "\n".join(cleaned)

    @staticmethod
    def _limit_reached(results: List[ScrapedStatute], max_statutes: Optional[int]) -> bool:
        return bool(max_statutes and len(results) >= max_statutes)

    async def scrape_statute(self, url: str) -> Optional[ScrapedStatute]:
        """
        Convenience method to fetch a single statute by URL/objectName.
        """
        html = await self.fetch_page(url)
        soup = BeautifulSoup(html, "lxml")
        return self._parse_statute_page(soup, url)
