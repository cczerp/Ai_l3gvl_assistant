"""
Scraper for the Wisconsin Legislature statutes site (docs.legis.wisconsin.gov).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
import re
from typing import List, Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .base_scraper import BaseScraper, ScrapedStatute

logger = logging.getLogger(__name__)


@dataclass
class _WisconsinSectionLink:
    url: str
    statute_number: str
    title: str


class WisconsinLegislatureScraper(BaseScraper):
    """
    Scrapes Wisconsin statutes from https://docs.legis.wisconsin.gov.

    Site structure:
        - https://docs.legis.wisconsin.gov/statutes/statutes lists every chapter.
        - Each chapter page contains entries with data-path attributes describing the sections.
        - Individual sections live under /statutes/statutes/{chapter}/{sectionSlug}.
    """

    STATE_CODE = "WI"
    BASE_URL = "https://docs.legis.wisconsin.gov"
    CHAPTER_INDEX_PATH = "/statutes/statutes"

    async def scrape_state(
        self,
        state_code: str,
        max_statutes: Optional[int] = None,
        sample_mode: bool = False,
        max_chapters: Optional[int] = None,
    ) -> List[ScrapedStatute]:
        state_code = state_code.upper()
        if state_code != self.STATE_CODE:
            raise ValueError(
                f"{self.__class__.__name__} can only scrape {self.STATE_CODE}, got {state_code}"
            )

        statutes: List[ScrapedStatute] = []
        chapter_slugs = await self._get_chapter_slugs()

        if sample_mode:
            chapter_slugs = chapter_slugs[: min(5, len(chapter_slugs))]
        elif max_chapters:
            chapter_slugs = chapter_slugs[:max_chapters]

        for chapter_slug in chapter_slugs:
            if self._limit_reached(statutes, max_statutes):
                break

            await self._scrape_chapter(
                chapter_slug,
                statutes,
                max_statutes=max_statutes,
                sample_mode=sample_mode,
            )

        self.stats["items_scraped"] = len(statutes)
        return statutes

    async def _get_chapter_slugs(self) -> List[str]:
        if hasattr(self, "_chapter_slugs"):
            return self._chapter_slugs  # type: ignore[attr-defined]

        index_url = urljoin(self.BASE_URL, self.CHAPTER_INDEX_PATH)
        logger.info("Fetching Wisconsin chapter index: %s", index_url)
        html = await self.fetch_page(index_url)
        soup = BeautifulSoup(html, "lxml")

        slugs: List[str] = []
        for span in soup.select("ul.docLinks span.hasPdfLink"):
            anchor = span.find("a")
            if not anchor or not anchor.get("href"):
                continue

            href = anchor["href"]
            # Example href: /document/statutes/66.pdf
            slug = href.rsplit("/", 1)[-1].split(".", 1)[0]
            if slug:
                slugs.append(slug)

        if not slugs:
            raise RuntimeError("Failed to detect Wisconsin chapter slugs from index page.")

        self._chapter_slugs = slugs  # cache
        return slugs

    async def _scrape_chapter(
        self,
        chapter_slug: str,
        results: List[ScrapedStatute],
        *,
        max_statutes: Optional[int],
        sample_mode: bool,
    ) -> None:
        chapter_url = urljoin(self.BASE_URL, f"/statutes/statutes/{chapter_slug}")
        logger.debug("Scraping Wisconsin chapter %s (%s)", chapter_slug, chapter_url)

        try:
            html = await self.fetch_page(chapter_url)
        except Exception as exc:
            logger.error("Failed to fetch chapter %s: %s", chapter_slug, exc)
            return

        section_links = self._extract_section_links_from_chapter(html)
        if not section_links:
            logger.warning("No sections discovered for Wisconsin chapter %s", chapter_slug)
            return

        if sample_mode:
            section_links = section_links[: min(5, len(section_links))]

        for link in section_links:
            if self._limit_reached(results, max_statutes):
                break

            try:
                statute = await self._scrape_section(link)
            except Exception as exc:
                logger.error("Failed to scrape section %s (%s): %s", link.statute_number, link.url, exc)
                continue

            if statute:
                results.append(statute)

    def _extract_section_links_from_chapter(self, html: str) -> List[_WisconsinSectionLink]:
        soup = BeautifulSoup(html, "lxml")
        entries = []
        seen_ids = set()

        for div in soup.select("div[data-section]"):
            section_id = div.get("data-section")
            if not section_id:
                continue

            # Skip nested subsections (e.g., 1.02(1)) — we want top-level sections only.
            if "(" in section_id:
                continue
            if "." not in section_id:
                continue
            if section_id in seen_ids:
                continue
            seen_ids.add(section_id)

            anchor = div.find("a", class_="reference")
            href = anchor["href"] if anchor and anchor.get("href") else None

            title_span = div.find("span", class_="qstitle_sect")
            title_text = ""
            if title_span:
                title_text = title_span.get_text(" ", strip=True)

            entries.append(
                _WisconsinSectionLink(
                    url=self._canonical_section_url_for_number(section_id, href),
                    statute_number=section_id.strip(),
                    title=title_text or section_id.strip(),
                )
            )

        return entries

    async def _scrape_section(self, link: _WisconsinSectionLink) -> Optional[ScrapedStatute]:
        html = await self.fetch_page(link.url)
        soup = BeautifulSoup(html, "lxml")
        section_div = self._locate_section_div(soup, link.statute_number)
        if not section_div:
            logger.warning("Could not find Wisconsin section div for %s (%s)", link.statute_number, link.url)
            return None

        statute_number = section_div.get("data-section") or link.statute_number
        title_span = section_div.find("span", class_="qstitle_sect")
        title_text = title_span.get_text(" ", strip=True) if title_span else link.title

        full_text = self._extract_section_text(section_div, statute_number, title_text)
        if not full_text:
            logger.debug("Empty Wisconsin section text for %s", statute_number)
            return None

        return ScrapedStatute(
            state=self.STATE_CODE,
            statute_number=statute_number,
            title=title_text,
            full_text=full_text,
            source_url=self._canonical_section_url_for_number(statute_number, None),
            metadata={"source": "wisconsin_legislature"},
        )

    def _locate_section_div(self, soup: BeautifulSoup, statute_number: str):
        return soup.select_one(f"div[data-section='{statute_number}']")

    @staticmethod
    def _extract_section_text(section_div, statute_number: str, title: str) -> str:
        body_parts: List[str] = []

        for span in section_div.find_all("span"):
            classes = span.get("class") or []
            text = span.get_text(" ", strip=True)
            if not text:
                continue
            if "qsnum_sect" in classes or "qstitle_sect" in classes:
                continue
            if text == statute_number or text == title:
                continue
            body_parts.append(text)

        if not body_parts:
            # If nothing collected, fall back to entire div text.
            fallback = section_div.get_text("\n", strip=True)
            return fallback

        return "\n".join(body_parts)

    @staticmethod
    def _limit_reached(results: List[ScrapedStatute], max_statutes: Optional[int]) -> bool:
        return bool(max_statutes and len(results) >= max_statutes)

    async def scrape_statute(self, url: str) -> Optional[ScrapedStatute]:
        """
        Fetch and parse a single statute by URL (utility hook).
        """
        statute_number = self._statute_number_from_url(url) or ""
        dummy_link = _WisconsinSectionLink(url=url, statute_number=statute_number, title="")
        return await self._scrape_section(dummy_link)

    def _canonical_section_url_for_number(self, statute_number: str, fallback_href: Optional[str]) -> str:
        if fallback_href:
            if "/document/statutes/" not in fallback_href:
                return urljoin(self.BASE_URL, fallback_href)
            # fall through to compute canonical path from statute number

        parts = statute_number.split(".", 1)
        if len(parts) != 2:
            if fallback_href:
                return urljoin(self.BASE_URL, fallback_href)
            return urljoin(self.BASE_URL, f"/statutes/statutes/{statute_number}".rstrip("/"))

        chapter_slug, section_slug = parts
        section_slug = section_slug.replace(".", "")
        return urljoin(self.BASE_URL, f"/statutes/statutes/{chapter_slug}/{section_slug}")

    @staticmethod
    def _statute_number_from_url(url: str) -> Optional[str]:
        match = re.search(r"/statutes/statutes/([0-9A-Za-z]+)/([0-9A-Za-z]+)", url)
        if not match:
            return None
        chapter = match.group(1)
        slug = match.group(2)
        slug_no_leading = slug.lstrip("0") or "0"
        return f"{chapter}.{slug_no_leading}"
