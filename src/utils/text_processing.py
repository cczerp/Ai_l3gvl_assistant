"""
Text processing utilities for legal documents.
"""

import re
from typing import List, Dict, Any


class TextProcessor:
    """Utilities for processing legal text."""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean and normalize legal text.
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep legal punctuation
        text = text.strip()
        
        return text
    
    @staticmethod
    def extract_sections(text: str) -> List[Dict[str, str]]:
        """
        Extract sections from legal documents.
        
        Args:
            text: Legal document text
            
        Returns:
            List of sections with titles and content
        """
        # Stub implementation
        # In production: use regex patterns to identify sections
        sections = []
        
        # Example pattern for numbered sections
        section_pattern = r'§\s*(\d+\.?\d*)'
        matches = re.finditer(section_pattern, text)
        
        for match in matches:
            sections.append({
                "section_number": match.group(1),
                "content": ""  # Would extract actual content
            })
        
        return sections
    
    @staticmethod
    def tokenize(text: str, method: str = "simple") -> List[str]:
        """
        Tokenize text for processing.
        
        Args:
            text: Text to tokenize
            method: Tokenization method ('simple', 'legal')
            
        Returns:
            List of tokens
        """
        if method == "simple":
            return text.split()
        elif method == "legal":
            # Preserve legal abbreviations and citations
            tokens = re.findall(r'\b[\w.]+\b', text)
            return tokens
        else:
            return text.split()
    
    @staticmethod
    def estimate_tokens(text: str) -> int:
        """
        Estimate token count for LLM context.
        
        Args:
            text: Input text
            
        Returns:
            Estimated token count
        """
        # Rough approximation: ~4 characters per token
        return len(text) // 4
    
    @staticmethod
    def truncate_to_tokens(text: str, max_tokens: int) -> str:
        """
        Truncate text to maximum token count.
        
        Args:
            text: Text to truncate
            max_tokens: Maximum tokens
            
        Returns:
            Truncated text
        """
        # Rough approximation
        max_chars = max_tokens * 4
        if len(text) <= max_chars:
            return text
        
        return text[:max_chars] + "..."
