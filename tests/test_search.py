"""
Unit tests for SearchEngine
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.indexer import InvertedIndex
from src.search import SearchEngine


class TestSearchEngine:
    """Test suite for SearchEngine"""

    def test_no_index_loaded(self):
        """Test search with no index"""
        engine = SearchEngine()

        results = engine.find("test")
        assert "No index loaded" in results[0]

    def test_find_single_word(self):
        """Test finding pages with single word"""
        index = InvertedIndex()
        index.add_page("http://test.com/page1", "apple banana", "")
        index.add_page("http://test.com/page2", "banana cherry", "")

        engine = SearchEngine(index)
        results = engine.find("apple")

        assert "Found 1 page(s)" in results[0]
        assert "http://test.com/page1" in "".join(results)

    def test_find_phrase(self):
        """Test finding pages with phrase"""
        index = InvertedIndex()
        index.add_page("http://test.com/page1", "apple banana cherry", "")
        index.add_page("http://test.com/page2", "apple banana date", "")
        index.add_page("http://test.com/page3", "apple cherry", "")

        engine = SearchEngine(index)
        results = engine.find("apple banana")

        assert "Found 2 page(s)" in results[0]
        assert "http://test.com/page3" not in "".join(results)

    def test_find_no_results(self):
        """Test search with no matching results"""
        index = InvertedIndex()
        index.add_page("http://test.com/page1", "test content", "")

        engine = SearchEngine(index)
        results = engine.find("nonexistent")

        assert "No pages found" in results[0]

    def test_empty_query(self):
        """Test empty query handling"""
        index = InvertedIndex()
        engine = SearchEngine(index)

        results = engine.find("")
        assert "provide a search query" in results[0]

        results = engine.find("   ")
        assert "provide a search query" in results[0]

    def test_print_index(self):
        """Test print index command"""
        index = InvertedIndex()
        index.add_page("http://test.com/page1", "test word", "")

        engine = SearchEngine(index)
        output = engine.print_index("test")

        assert "test" in output
        assert "http://test.com/page1" in output

    def test_print_index_no_index(self):
        """Test print with no index loaded"""
        engine = SearchEngine()
        output = engine.print_index("test")
        assert "No index loaded" in output

    def test_has_index(self):
        """Test has_index method"""
        engine = SearchEngine()
        assert not engine.has_index()

        index = InvertedIndex()
        engine.set_index(index)
        assert engine.has_index()

    def test_set_index(self):
        """Test setting index after creation"""
        engine = SearchEngine()
        index = InvertedIndex()
        index.add_page("http://test.com/page1", "hello", "")

        engine.set_index(index)
        assert engine.has_index()

        results = engine.find("hello")
        assert "Found 1 page(s)" in results[0]

    def test_get_index_stats(self):
        """Test getting index statistics"""
        index = InvertedIndex()
        index.add_page("http://test.com/page1", "apple banana", "")

        engine = SearchEngine(index)
        stats = engine.get_index_stats()

        assert stats['unique_words'] == 2
        assert stats['total_pages'] == 1

    def test_get_index_stats_no_index(self):
        """Test stats with no index"""
        engine = SearchEngine()
        stats = engine.get_index_stats()
        assert 'error' in stats

    def test_relevance_sorting(self):
        """Test results are sorted by relevance"""
        index = InvertedIndex()
        # Page1: 'apple' appears 3 times
        # Page2: 'apple' appears 1 time
        index.add_page("http://test.com/page1", "apple apple apple", "")
        index.add_page("http://test.com/page2", "apple", "")

        engine = SearchEngine(index)
        results = engine.find("apple")

        # Page1 should come first due to higher frequency
        combined = "".join(results)
        page1_pos = combined.find("http://test.com/page1")
        page2_pos = combined.find("http://test.com/page2")
        assert page1_pos < page2_pos


if __name__ == "__main__":
    pytest.main([__file__, "-v"])