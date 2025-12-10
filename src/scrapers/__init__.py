"""
Web scrapers for legal data sources.
"""

from .base_scraper import BaseScraper, ScraperConfig
from .justia_scraper import JustiaScraper
from .michigan_scraper import MichiganLegislatureScraper
from .state_codes_scraper import StateCodesScraperFactory

__all__ = [
    'BaseScraper',
    'ScraperConfig',
    'JustiaScraper',
    'MichiganLegislatureScraper',
    'StateCodesScraperFactory'
]
