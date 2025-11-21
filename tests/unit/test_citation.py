"""Tests for citation checker."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.citation import CitationChecker, CitationType


def test_citation_checker_initialization():
    """Test citation checker can be initialized."""
    checker = CitationChecker()
    assert checker is not None


def test_extract_case_citations():
    """Test extracting case citations."""
    checker = CitationChecker()
    text = "See Brown v. Board, 347 U.S. 483 (1954)"
    
    citations = checker.extract_citations(text)
    assert len(citations) > 0
    assert citations[0].citation_type == CitationType.CASE


def test_extract_statute_citations():
    """Test extracting statute citations."""
    checker = CitationChecker()
    text = "According to 42 U.S.C. § 2000a"
    
    citations = checker.extract_citations(text)
    assert len(citations) > 0
    assert citations[0].citation_type == CitationType.STATUTE


def test_check_text():
    """Test checking citations in text."""
    checker = CitationChecker()
    text = "347 U.S. 483 and 42 U.S.C. 2000a"
    
    results = checker.check_text(text)
    assert "total_citations" in results
    assert "citations" in results
    assert results["total_citations"] > 0
