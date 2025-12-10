"""
Ingestion pipeline for processing and indexing legal documents.
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
from config import get_config


class DocumentType(Enum):
    """Types of legal documents."""
    STATE_LAW = "state_law"
    FEDERAL_LAW = "federal_law"
    CASE = "case"
    REGULATION = "regulation"
    LEGAL_DICTIONARY = "legal_dictionary"


@dataclass
class Document:
    """Represents a legal document."""
    doc_id: str
    doc_type: DocumentType
    title: str
    content: str
    metadata: Dict[str, Any]
    source: str
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


class DocumentProcessor:
    """
    Processes raw legal documents into structured format.
    """
    
    def __init__(self):
        """Initialize document processor."""
        self.config = get_config()
    
    def process_case(self, raw_data: Dict[str, Any]) -> Document:
        """
        Process a legal case document.
        
        Args:
            raw_data: Raw case data
            
        Returns:
            Processed document
        """
        # Extract case metadata
        metadata = {
            "case_name": raw_data.get("name", ""),
            "citation": raw_data.get("citation", ""),
            "court": raw_data.get("court", ""),
            "date_decided": raw_data.get("date_decided", ""),
            "jurisdiction": raw_data.get("jurisdiction", ""),
            "judges": raw_data.get("judges", []),
            "docket_number": raw_data.get("docket_number", "")
        }
        
        return Document(
            doc_id=raw_data.get("id", ""),
            doc_type=DocumentType.CASE,
            title=raw_data.get("name", ""),
            content=raw_data.get("opinion_text", ""),
            metadata=metadata,
            source=raw_data.get("source", "")
        )
    
    def process_statute(self, raw_data: Dict[str, Any]) -> Document:
        """
        Process a statute document.
        
        Args:
            raw_data: Raw statute data
            
        Returns:
            Processed document
        """
        doc_type = (DocumentType.FEDERAL_LAW if raw_data.get("is_federal") 
                   else DocumentType.STATE_LAW)
        
        metadata = {
            "statute_number": raw_data.get("statute_number", ""),
            "chapter": raw_data.get("chapter", ""),
            "section": raw_data.get("section", ""),
            "effective_date": raw_data.get("effective_date", ""),
            "jurisdiction": raw_data.get("jurisdiction", ""),
            "state": raw_data.get("state", "") if not raw_data.get("is_federal") else None
        }
        
        return Document(
            doc_id=raw_data.get("id", ""),
            doc_type=doc_type,
            title=raw_data.get("title", ""),
            content=raw_data.get("text", ""),
            metadata=metadata,
            source=raw_data.get("source", "")
        )
    
    def process_dictionary_entry(self, raw_data: Dict[str, Any]) -> Document:
        """
        Process a legal dictionary entry.
        
        Args:
            raw_data: Raw dictionary data
            
        Returns:
            Processed document
        """
        metadata = {
            "term": raw_data.get("term", ""),
            "source": raw_data.get("source", ""),
            "jurisdiction": raw_data.get("jurisdiction", "general")
        }
        
        return Document(
            doc_id=raw_data.get("id", ""),
            doc_type=DocumentType.LEGAL_DICTIONARY,
            title=raw_data.get("term", ""),
            content=raw_data.get("definition", ""),
            metadata=metadata,
            source=raw_data.get("source", "")
        )
    
    def chunk_document(
        self, 
        document: Document,
        chunk_size: int = 1000,
        overlap: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Split document into chunks for embedding.
        
        Args:
            document: Document to chunk
            chunk_size: Size of each chunk in characters
            overlap: Overlap between chunks
            
        Returns:
            List of document chunks with metadata
        """
        content = document.content
        chunks = []
        
        start = 0
        chunk_id = 0
        
        while start < len(content):
            end = start + chunk_size
            chunk_text = content[start:end]
            
            chunk = {
                "chunk_id": f"{document.doc_id}_chunk_{chunk_id}",
                "doc_id": document.doc_id,
                "content": chunk_text,
                "metadata": {
                    **document.metadata,
                    "chunk_index": chunk_id,
                    "doc_type": document.doc_type.value,
                    "title": document.title
                }
            }
            chunks.append(chunk)
            
            start = end - overlap
            chunk_id += 1
        
        return chunks


class IngestionPipeline:
    """
    Pipeline for ingesting legal documents into the system.
    """
    
    def __init__(self):
        """Initialize ingestion pipeline."""
        self.config = get_config()
        self.data_sources = self.config.get_rag_config('data_sources')
        self.processor = DocumentProcessor()
    
    def ingest_directory(
        self, 
        directory: Path,
        doc_type: DocumentType
    ) -> Dict[str, Any]:
        """
        Ingest all documents from a directory.
        
        Args:
            directory: Path to directory containing documents
            doc_type: Type of documents to ingest
            
        Returns:
            Ingestion statistics
        """
        # Stub implementation
        # In production: iterate through files, parse, and ingest
        stats = {
            "total_documents": 0,
            "total_chunks": 0,
            "errors": 0,
            "doc_type": doc_type.value
        }
        
        print(f"Ingesting documents from {directory} as {doc_type.value}")
        
        return stats
    
    def ingest_state_laws(self, state: Optional[str] = None) -> Dict[str, Any]:
        """
        Ingest state law documents.
        
        Args:
            state: Specific state to ingest, or None for all states
            
        Returns:
            Ingestion statistics
        """
        config = self.data_sources.get('state_laws', {})
        base_path = Path(config.get('path', 'data/state_laws'))
        
        if state:
            state_path = base_path / state
            return self.ingest_directory(state_path, DocumentType.STATE_LAW)
        else:
            # Ingest all 50 states
            total_stats = {
                "total_documents": 0,
                "total_chunks": 0,
                "errors": 0,
                "states_processed": 0
            }
            
            # Stub: would iterate through state directories
            print(f"Ingesting all state laws from {base_path}")
            
            return total_stats
    
    def ingest_federal_laws(self) -> Dict[str, Any]:
        """
        Ingest federal law documents.
        
        Returns:
            Ingestion statistics
        """
        config = self.data_sources.get('federal_laws', {})
        base_path = Path(config.get('path', 'data/federal_laws'))
        
        return self.ingest_directory(base_path, DocumentType.FEDERAL_LAW)
    
    def ingest_cases(
        self, 
        start_year: Optional[int] = None,
        end_year: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Ingest case law documents.
        
        Args:
            start_year: Start year for cases (default: 50 years ago)
            end_year: End year for cases (default: current year)
            
        Returns:
            Ingestion statistics
        """
        config = self.data_sources.get('cases', {})
        base_path = Path(config.get('path', 'data/cases'))
        years_coverage = config.get('years_coverage', 50)
        
        if start_year is None:
            start_year = datetime.now().year - years_coverage
        if end_year is None:
            end_year = datetime.now().year
        
        print(f"Ingesting cases from {start_year} to {end_year}")
        
        return self.ingest_directory(base_path, DocumentType.CASE)
    
    def ingest_legal_dictionaries(self) -> Dict[str, Any]:
        """
        Ingest legal dictionary entries.
        
        Returns:
            Ingestion statistics
        """
        config = self.data_sources.get('legal_dictionaries', {})
        base_path = Path(config.get('path', 'data/legal_dictionaries'))
        
        return self.ingest_directory(base_path, DocumentType.LEGAL_DICTIONARY)
    
    def ingest_all(self) -> Dict[str, Any]:
        """
        Ingest all legal data sources.
        
        Returns:
            Combined ingestion statistics
        """
        print("Starting full ingestion pipeline...")
        
        stats = {
            "state_laws": self.ingest_state_laws(),
            "federal_laws": self.ingest_federal_laws(),
            "cases": self.ingest_cases(),
            "legal_dictionaries": self.ingest_legal_dictionaries(),
            "start_time": datetime.now().isoformat()
        }
        
        print("Full ingestion pipeline completed")
        
        return stats
    
    def validate_document(self, document: Document) -> List[str]:
        """
        Validate a document before ingestion.
        
        Args:
            document: Document to validate
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        if not document.doc_id:
            errors.append("Missing document ID")
        
        if not document.content or len(document.content) < 10:
            errors.append("Document content too short or empty")
        
        if not document.title:
            errors.append("Missing document title")
        
        return errors
