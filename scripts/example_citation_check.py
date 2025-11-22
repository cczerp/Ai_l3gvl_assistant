#!/usr/bin/env python3
"""
Example script for checking legal citations.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.citation import CitationChecker


def main():
    """Run example citation check."""
    text = """
    As established in Brown v. Board of Education, 347 U.S. 483 (1954),
    separate educational facilities are inherently unequal. This principle
    was further reinforced in Heart of Atlanta Motel v. United States,
    379 U.S. 241 (1964), which upheld the Civil Rights Act of 1964.
    See also 42 U.S.C. § 2000a for the relevant statutory provisions.
    """
    
    print("Checking citations in text...\n")
    
    # Initialize citation checker
    checker = CitationChecker()
    
    # Check citations
    results = checker.check_text(text)
    
    print(f"Total citations found: {results['total_citations']}")
    print(f"Valid citations: {results['valid_citations']}")
    print(f"Invalid citations: {results['invalid_citations']}\n")
    
    print("Citation details:")
    for i, citation in enumerate(results['citations'], 1):
        print(f"\n{i}. {citation['text']}")
        print(f"   Type: {citation['type']}")
        print(f"   Valid: {citation['is_valid']}")
        if citation['errors']:
            print(f"   Errors: {', '.join(citation['errors'])}")


if __name__ == "__main__":
    main()
