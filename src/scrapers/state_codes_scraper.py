"""
Factory for state-specific code scrapers.
Some states have better official sources than Justia - this module handles those.
"""

from typing import Optional, Type
import logging

from .base_scraper import BaseScraper, ScraperConfig
from .justia_scraper import JustiaScraper
from .michigan_scraper import MichiganLegislatureScraper
from .wisconsin_scraper import WisconsinLegislatureScraper

logger = logging.getLogger(__name__)


class StateCodesScraperFactory:
    """
    Factory for creating appropriate scrapers for different states.

    Some states have official, well-structured statute sites that are
    better than third-party aggregators. This factory returns the best
    scraper for each state.
    """

    # Map of state codes to specialized scraper classes
    # Add state-specific scrapers here as they're developed
    SPECIALIZED_SCRAPERS = {
        'MI': MichiganLegislatureScraper,
        'WI': WisconsinLegislatureScraper,
    }

    # Default scraper for states without specialized scrapers
    DEFAULT_SCRAPER = JustiaScraper

    @classmethod
    def get_scraper(
        cls,
        state_code: str,
        config: Optional[ScraperConfig] = None,
        force_default: bool = False
    ) -> BaseScraper:
        """
        Get the appropriate scraper for a state.

        Args:
            state_code: Two-letter state code
            config: Scraper configuration
            force_default: If True, use default scraper even if specialized exists

        Returns:
            Configured scraper instance
        """
        state_code = state_code.upper()

        if force_default or state_code not in cls.SPECIALIZED_SCRAPERS:
            logger.info(f"Using default scraper (Justia) for {state_code}")
            return cls.DEFAULT_SCRAPER(config)

        scraper_class = cls.SPECIALIZED_SCRAPERS[state_code]
        logger.info(f"Using specialized scraper for {state_code}: {scraper_class.__name__}")
        return scraper_class(config)

    @classmethod
    def has_specialized_scraper(cls, state_code: str) -> bool:
        """
        Check if a state has a specialized scraper.

        Args:
            state_code: Two-letter state code

        Returns:
            True if specialized scraper exists
        """
        return state_code.upper() in cls.SPECIALIZED_SCRAPERS

    @classmethod
    def list_specialized_states(cls) -> list:
        """
        List all states with specialized scrapers.

        Returns:
            List of state codes
        """
        return list(cls.SPECIALIZED_SCRAPERS.keys())


# Example template for state-specific scraper
# Uncomment and modify to create scrapers for specific states

"""
class CaliforniaOfficialScraper(BaseScraper):
    '''
    Scraper for California Legislative Information website.
    URL: https://leginfo.legislature.ca.gov/
    '''

    BASE_URL = "https://leginfo.legislature.ca.gov"

    async def scrape_state(self, state_code: str) -> List[ScrapedStatute]:
        '''Scrape California statutes from official source.'''
        # Implementation specific to California's site structure
        pass

    async def scrape_statute(self, url: str) -> Optional[ScrapedStatute]:
        '''Scrape individual California statute.'''
        # Implementation specific to California's statute pages
        pass
"""
