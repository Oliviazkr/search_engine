"""
Search functionality for the search engine
"""
from typing import List, Dict, Optional
from indexer import InvertedIndex


class SearchEngine:
    """Search engine wrapper around inverted index"""

    def __init__(self, index: Optional[InvertedIndex] = None):
        """
        Initialize search engine with an index

        Args:
            index: InvertedIndex object (can be None initially)
        """
        self.index = index

    def set_index(self, index: InvertedIndex):
        """Set or replace the index"""
        self.index = index

    def has_index(self) -> bool:
        """Check if an index is loaded"""
        return self.index is not None

    def find(self, query: str) -> List[str]:
        """
        Find pages containing the query phrase

        Args:
            query: Search query (single word or phrase)

        Returns:
            List of URLs sorted by relevance (frequency)
        """
        if not self.has_index():
            return ["Error: No index loaded. Use 'load' command first."]

        if not query or not query.strip():
            return ["Please provide a search query."]

        # Get results with relevance scores
        results = self.index.get_pages_containing_phrase(query.strip())

        if not results:
            return [f"No pages found containing '{query}'."]

        # Sort by relevance score (frequency) descending
        sorted_results = sorted(results.items(), key=lambda x: x[1], reverse=True)

        output = [f"Found {len(sorted_results)} page(s) containing '{query}':"]
        for url, score in sorted_results:
            output.append(f"  {url} (relevance: {score})")

        return output

    def print_index(self, word: str) -> str:
        """
        Print inverted index for a specific word

        Args:
            word: Word to look up

        Returns:
            Formatted index entry
        """
        if not self.has_index():
            return "Error: No index loaded. Use 'load' command first."

        return self.index.print_index_for_word(word)

    def get_index_stats(self) -> Dict:
        """Get statistics about the current index"""
        if not self.has_index():
            return {'error': 'No index loaded'}
        return self.index.get_stats()