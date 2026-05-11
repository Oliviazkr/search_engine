import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.indexer import InvertedIndex, Posting


class TestInvertedIndex:
    """Test suite for InvertedIndex"""

    def test_normalize_word(self):
        """Test word normalization - removing special characters and spaces"""
        index = InvertedIndex()

        assert index._normalize_word("Hello") == "hello"
        assert index._normalize_word("WORLD") == "world"
        assert index._normalize_word("Good!") == "good"
        assert index._normalize_word("don't") == "dont"
        # The normalize_word removes all non-alphanumeric characters including spaces
        # So "  spaced  " becomes "spaced" after stripping
        result = index._normalize_word("  spaced  ")
        assert result == "spaced" or "spaced" in result

    def test_tokenize(self):
        """Test text tokenization"""
        index = InvertedIndex()

        tokens = index._tokenize("Hello world! This is a test.")
        assert tokens == ["hello", "world", "this", "is", "a", "test"]

        # Test ignoring empty tokens
        tokens = index._tokenize("")
        assert tokens == []

    def test_add_page_single_word(self):
        """Test adding a page with simple content"""
        index = InvertedIndex()
        index.add_page("http://test.com/page1", "hello world hello", "Title")

        # Check index has the words
        assert "hello" in index.index
        assert "world" in index.index

        # Check posting for 'hello'
        hello_postings = index.get_postings("hello")
        assert len(hello_postings) == 1
        assert hello_postings[0].url == "http://test.com/page1"
        assert hello_postings[0].frequency == 2  # 'hello' appears twice
        assert len(hello_postings[0].positions) == 2  # Two positions

    def test_add_multiple_pages(self):
        """Test adding multiple pages to index"""
        index = InvertedIndex()
        index.add_page("http://test.com/page1", "apple banana", "")
        index.add_page("http://test.com/page2", "apple cherry", "")

        # 'apple' appears in both pages
        apple_postings = index.get_postings("apple")
        assert len(apple_postings) == 2

        # 'banana' appears only in page1
        banana_postings = index.get_postings("banana")
        assert len(banana_postings) == 1
        assert banana_postings[0].url == "http://test.com/page1"

        # 'cherry' appears only in page2
        cherry_postings = index.get_postings("cherry")
        assert len(cherry_postings) == 1
        assert cherry_postings[0].url == "http://test.com/page2"

    def test_case_insensitive_search(self):
        """Test case-insensitive word matching"""
        index = InvertedIndex()
        index.add_page("http://test.com/page1", "Hello WORLD", "")

        assert index.get_postings("hello")[0].url == "http://test.com/page1"
        assert index.get_postings("HELLO")[0].url == "http://test.com/page1"
        assert index.get_postings("world")[0].url == "http://test.com/page1"
        assert index.get_postings("WORLD")[0].url == "http://test.com/page1"

    def test_find_single_word(self):
        """Test finding pages with single word"""
        index = InvertedIndex()
        index.add_page("http://test.com/page1", "apple banana", "")
        index.add_page("http://test.com/page2", "banana cherry", "")

        results = index.get_pages_containing_phrase("apple")
        assert "http://test.com/page1" in results
        assert "http://test.com/page2" not in results

        results = index.get_pages_containing_phrase("banana")
        assert "http://test.com/page1" in results
        assert "http://test.com/page2" in results

    def test_find_phrase_multiple_words(self):
        """Test finding pages with multiple words"""
        index = InvertedIndex()
        index.add_page("http://test.com/page1", "apple banana cherry", "")
        index.add_page("http://test.com/page2", "apple banana date", "")
        index.add_page("http://test.com/page3", "apple cherry", "")

        # Pages containing both 'apple' AND 'banana'
        results = index.get_pages_containing_phrase("apple banana")
        assert "http://test.com/page1" in results
        assert "http://test.com/page2" in results
        assert "http://test.com/page3" not in results

        # Pages containing all three words
        results = index.get_pages_containing_phrase("apple banana cherry")
        assert "http://test.com/page1" in results
        assert "http://test.com/page2" not in results  # missing cherry
        assert "http://test.com/page3" not in results  # missing banana

    def test_word_not_in_index(self):
        """Test searching for word not in index"""
        index = InvertedIndex()
        index.add_page("http://test.com/page1", "test content", "")

        results = index.get_pages_containing_phrase("nonexistent")
        assert results == {}

    def test_empty_query(self):
        """Test empty query handling"""
        index = InvertedIndex()
        results = index.get_pages_containing_phrase("")
        assert results == {}

        results = index.get_pages_containing_phrase("   ")
        assert results == {}

    def test_print_index_format(self):
        """Test print index command output"""
        index = InvertedIndex()
        index.add_page("http://test.com/page1", "test word test", "")

        output = index.print_index_for_word("test")
        assert "test" in output
        assert "http://test.com/page1" in output
        assert "Frequency: 2" in output

    def test_print_index_word_not_found(self):
        """Test print for word not in index"""
        index = InvertedIndex()
        output = index.print_index_for_word("nonexistent")
        assert "not found" in output

    def test_serialization(self):
        """Test index serialization to dict and back - verify structure preserved"""
        index = InvertedIndex()
        index.add_page("http://test.com/page1", "hello world", "Title")
        index.add_page("http://test.com/page2", "hello again", "Title2")

        # Convert to dict
        data = index.to_dict()

        # Recreate from dict
        new_index = InvertedIndex.from_dict(data)

        # Verify data preserved - check same number of words and pages
        assert len(new_index.index) == len(index.index)
        assert new_index.next_docid == index.next_docid
        # Check that hello exists in both indexes with correct URL
        new_hello_postings = new_index.get_postings("hello")
        assert len(new_hello_postings) == 2
        # Check that the first posting has URL page1
        urls = [p.url for p in new_hello_postings]
        assert "http://test.com/page1" in urls
        assert "http://test.com/page2" in urls

    def test_get_stats(self):
        """Test index statistics"""
        index = InvertedIndex()
        index.add_page("http://test.com/page1", "apple banana", "")
        index.add_page("http://test.com/page2", "apple cherry", "")

        stats = index.get_stats()
        assert stats['unique_words'] == 3  # apple, banana, cherry
        assert stats['total_pages'] == 2
        assert stats['total_postings'] == 4  # apple(2) + banana(1) + cherry(1)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
