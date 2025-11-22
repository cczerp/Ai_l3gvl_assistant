"""
Supabase client for legal data storage.
"""

import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from supabase import create_client, Client
from postgrest.exceptions import APIError

logger = logging.getLogger(__name__)


class SupabaseClient:
    """
    Client for interacting with Supabase database.
    Handles CRUD operations for legal data.
    """

    def __init__(self, url: Optional[str] = None, key: Optional[str] = None):
        """
        Initialize Supabase client.

        Args:
            url: Supabase project URL (defaults to SUPABASE_URL env var)
            key: Supabase anon/service key (defaults to SUPABASE_KEY env var)
        """
        self.url = url or os.getenv('SUPABASE_URL')
        self.key = key or os.getenv('SUPABASE_KEY')

        if not self.url or not self.key:
            raise ValueError(
                "Supabase URL and KEY must be provided or set in environment variables "
                "(SUPABASE_URL and SUPABASE_KEY)"
            )

        self.client: Client = create_client(self.url, self.key)
        logger.info("Supabase client initialized")

    # ============================================
    # STATE LAWS
    # ============================================

    async def insert_state_law(self, statute: Dict[str, Any]) -> Dict[str, Any]:
        """
        Insert a single state law into the database.

        Args:
            statute: Dictionary with statute data (from ScrapedStatute.to_dict())

        Returns:
            Inserted record with ID
        """
        try:
            # Prepare data for insertion
            data = {
                "state": statute.get("state"),
                "statute_number": statute.get("statute_number"),
                "title": statute.get("title"),
                "chapter": statute.get("chapter"),
                "section": statute.get("section"),
                "full_text": statute.get("full_text"),
                "effective_date": statute.get("effective_date"),
                "last_amended": statute.get("last_amended"),
                "jurisdiction": statute.get("jurisdiction", "state"),
                "source_url": statute.get("source_url"),
                "metadata": statute.get("metadata", {}),
            }

            response = self.client.table('state_laws').insert(data).execute()

            logger.debug(f"Inserted statute: {statute.get('statute_number')}")
            return response.data[0] if response.data else {}

        except APIError as e:
            logger.error(f"Failed to insert statute: {str(e)}")
            raise

    async def insert_state_laws_batch(
        self,
        statutes: List[Dict[str, Any]],
        batch_size: int = 100
    ) -> int:
        """
        Insert multiple state laws in batches.

        Args:
            statutes: List of statute dictionaries
            batch_size: Number of records per batch

        Returns:
            Number of successfully inserted records
        """
        total_inserted = 0

        for i in range(0, len(statutes), batch_size):
            batch = statutes[i:i + batch_size]

            try:
                data_batch = [
                    {
                        "state": s.get("state"),
                        "statute_number": s.get("statute_number"),
                        "title": s.get("title"),
                        "chapter": s.get("chapter"),
                        "section": s.get("section"),
                        "full_text": s.get("full_text"),
                        "effective_date": s.get("effective_date"),
                        "last_amended": s.get("last_amended"),
                        "jurisdiction": s.get("jurisdiction", "state"),
                        "source_url": s.get("source_url"),
                        "metadata": s.get("metadata", {}),
                    }
                    for s in batch
                ]

                response = self.client.table('state_laws').insert(data_batch).execute()
                inserted = len(response.data) if response.data else 0
                total_inserted += inserted

                logger.info(
                    f"Batch {i // batch_size + 1}: "
                    f"Inserted {inserted}/{len(batch)} statutes"
                )

            except APIError as e:
                logger.error(f"Failed to insert batch: {str(e)}")
                continue

        logger.info(f"Total inserted: {total_inserted}/{len(statutes)} statutes")
        return total_inserted

    async def get_state_laws(
        self,
        state: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Retrieve state laws from database.

        Args:
            state: Filter by state code (e.g., 'CA')
            limit: Maximum number of records
            offset: Offset for pagination

        Returns:
            List of state law records
        """
        try:
            query = self.client.table('state_laws').select('*')

            if state:
                query = query.eq('state', state)

            query = query.range(offset, offset + limit - 1)
            response = query.execute()

            return response.data or []

        except APIError as e:
            logger.error(f"Failed to retrieve state laws: {str(e)}")
            return []

    async def search_state_laws(
        self,
        query_text: str,
        state: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search state laws by text (uses PostgreSQL full-text search).

        Args:
            query_text: Text to search for
            state: Optional state filter
            limit: Maximum results

        Returns:
            List of matching statutes
        """
        try:
            # Note: This requires full-text search to be set up in Supabase
            query = self.client.table('state_laws').select('*')

            if state:
                query = query.eq('state', state)

            # Use text search (requires tsvector column in database)
            query = query.text_search('full_text', query_text)
            query = query.limit(limit)

            response = query.execute()
            return response.data or []

        except APIError as e:
            logger.error(f"Search failed: {str(e)}")
            return []

    # ============================================
    # FEDERAL LAWS
    # ============================================

    async def insert_federal_law(self, law: Dict[str, Any]) -> Dict[str, Any]:
        """Insert a federal law into the database."""
        try:
            data = {
                "usc_title": law.get("usc_title"),
                "section": law.get("section"),
                "title": law.get("title"),
                "full_text": law.get("full_text"),
                "effective_date": law.get("effective_date"),
                "agency": law.get("agency"),
                "cfr_reference": law.get("cfr_reference"),
                "source_url": law.get("source_url"),
                "metadata": law.get("metadata", {}),
            }

            response = self.client.table('federal_laws').insert(data).execute()
            return response.data[0] if response.data else {}

        except APIError as e:
            logger.error(f"Failed to insert federal law: {str(e)}")
            raise

    # ============================================
    # CASES
    # ============================================

    async def insert_case(self, case: Dict[str, Any]) -> Dict[str, Any]:
        """Insert a legal case into the database."""
        try:
            data = {
                "case_name": case.get("case_name"),
                "citation": case.get("citation"),
                "court": case.get("court"),
                "jurisdiction": case.get("jurisdiction"),
                "date_decided": case.get("date_decided"),
                "judges": case.get("judges", []),
                "docket_number": case.get("docket_number"),
                "opinion_text": case.get("opinion_text"),
                "opinion_type": case.get("opinion_type"),
                "metadata": case.get("metadata", {}),
            }

            response = self.client.table('cases').insert(data).execute()
            return response.data[0] if response.data else {}

        except APIError as e:
            logger.error(f"Failed to insert case: {str(e)}")
            raise

    # ============================================
    # LEGAL TERMS
    # ============================================

    async def insert_legal_term(self, term: Dict[str, Any]) -> Dict[str, Any]:
        """Insert a legal term into the dictionary."""
        try:
            data = {
                "term": term.get("term"),
                "definition": term.get("definition"),
                "jurisdiction": term.get("jurisdiction", "general"),
                "source": term.get("source"),
                "metadata": term.get("metadata", {}),
            }

            response = self.client.table('legal_terms').insert(data).execute()
            return response.data[0] if response.data else {}

        except APIError as e:
            logger.error(f"Failed to insert legal term: {str(e)}")
            raise

    # ============================================
    # UTILITY METHODS
    # ============================================

    async def get_stats(self) -> Dict[str, int]:
        """
        Get database statistics.

        Returns:
            Dictionary with counts for each table
        """
        stats = {}

        tables = ['state_laws', 'federal_laws', 'cases', 'legal_terms']

        for table in tables:
            try:
                response = self.client.table(table).select('id', count='exact').execute()
                stats[table] = response.count or 0
            except APIError:
                stats[table] = 0

        return stats

    async def check_duplicate_statute(
        self,
        state: str,
        statute_number: str
    ) -> bool:
        """
        Check if a statute already exists in the database.

        Args:
            state: State code
            statute_number: Statute number

        Returns:
            True if duplicate exists
        """
        try:
            response = self.client.table('state_laws') \
                .select('id') \
                .eq('state', state) \
                .eq('statute_number', statute_number) \
                .limit(1) \
                .execute()

            return len(response.data) > 0

        except APIError:
            return False


# Singleton instance
_supabase_client: Optional[SupabaseClient] = None


def get_supabase_client() -> SupabaseClient:
    """
    Get or create singleton Supabase client.

    Returns:
        SupabaseClient instance
    """
    global _supabase_client

    if _supabase_client is None:
        _supabase_client = SupabaseClient()

    return _supabase_client
