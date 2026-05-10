"""
Inverted index builder with word statistics
Stores frequency and position information for each word
"""
import re
import json
from typing import Dict, List, Set, Tuple
from collections import defaultdict
from dataclasses import dataclass, asdict


@dataclass
class WordStats:
    """Statistics for a word occurrence in a page"""
    frequency: int
    positions: List[int]


@dataclass
class Posting:
    """Posting list entry for a word"""
    url: str
    frequency: int
    positions: List[int]

    def to_dict(self):
        return {'url': self.url, 'frequency': self.frequency, 'positions': self.positions}

    @classmethod
    def from_dict(cls, data):
        return cls(data['url'], data['frequency'], data['positions'])


class InvertedIndex:
    """
    Inverted index mapping words to posting lists
    Supports case-insensitive word matching
    """

    def __init__(self):
        # word -> list of Posting objects
        self.index: Dict[str, List[Posting]] = defaultdict(list)
        # url -> document ID mapping
        self.url_to_docid: Dict[str, int] = {}
        self.docid_to_url: Dict[int, str] = {}
        self.next_docid: int = 0

    def _normalize_word(self, word: str) -> str:
        """
        Normalize word: lowercase, remove special characters
        """
        # Convert to lowercase
        word = word.lower()
        # Remove non-alphanumeric characters (keep spaces for phrases)
        word = re.sub(r'[^\w\s]', '', word)
        return word

    def _tokenize(self, text: str) -> List[str]:
        """
        Split text into tokens (words)
        """
        # Split on whitespace
        words = text.split()
        # Normalize each word
        return [self._normalize_word(w) for w in words if self._normalize_word(w)]

    def add_page(self, url: str, content: str, title: str = ""):
        """
        Add a page to the inverted index

        Args:
            url: Page URL
            content: Page text content
            title: Page title
        """
        # Combine title and content for indexing (title words get higher weight implicitly)
        full_text = f"{title} {content}"
        tokens = self._tokenize(full_text)

        # Get document ID
        if url not in self.url_to_docid:
            self.url_to_docid[url] = self.next_docid
            self.docid_to_url[self.next_docid] = url
            self.next_docid += 1

        # Count word frequencies and positions
        word_positions: Dict[str, List[int]] = defaultdict(list)

        for pos, token in enumerate(tokens):
            if token:  # Skip empty tokens
                word_positions[token].append(pos)

        # Update index
        for word, positions in word_positions.items():
            posting = Posting(
                url=url,
                frequency=len(positions),
                positions=positions
            )
            self.index[word].append(posting)

    def get_postings(self, word: str) -> List[Posting]:
        """
        Get posting list for a word

        Args:
            word: Search word (case-insensitive)

        Returns:
            List of Posting objects
        """
        normalized = self._normalize_word(word)
        return self.index.get(normalized, [])

    def get_all_pages_containing_word(self, word: str) -> List[str]:
        """
        Get all URLs containing a specific word

        Args:
            word: Search word

        Returns:
            List of URLs
        """
        postings = self.get_postings(word)
        return [p.url for p in postings]

    def get_pages_containing_phrase(self, phrase: str) -> Dict[str, int]:
        """
        Find pages containing all words in a phrase

        Args:
            phrase: Search phrase (multiple words)

        Returns:
            Dictionary mapping URL to relevance score (frequency sum)
        """
        if not phrase.strip():
            return {}

        words = phrase.strip().split()
        normalized_words = [self._normalize_word(w) for w in words]

        # Remove empty words
        normalized_words = [w for w in normalized_words if w]

        if not normalized_words:
            return {}

        if len(normalized_words) == 1:
            # Single word query
            postings = self.get_postings(normalized_words[0])
            return {p.url: p.frequency for p in postings}

        # Multi-word query: find pages containing ALL words
        # Get posting lists for each word
        posting_lists = [self.get_postings(word) for word in normalized_words]

        # Check if any word not found
        if any(len(postings) == 0 for postings in posting_lists):
            return {}

        # Build URL to frequency map
        url_to_total_freq: Dict[str, int] = defaultdict(int)

        # For each posting list, add frequency to the URL map
        for postings in posting_lists:
            for posting in postings:
                url_to_total_freq[posting.url] += posting.frequency

        # Filter to URLs that appear in ALL posting lists
        # (have all words)
        all_urls_set = [set(p.url for p in postings) for postings in posting_lists]
        intersection = set.intersection(*all_urls_set)

        # Return only URLs in intersection
        return {url: url_to_total_freq[url] for url in intersection}

    def print_index_for_word(self, word: str) -> str:
        """
        Get formatted string of inverted index for a word

        Args:
            word: Word to look up

        Returns:
            Formatted string representation
        """
        normalized = self._normalize_word(word)
        postings = self.index.get(normalized, [])

        if not postings:
            return f"Word '{word}' not found in index."

        result = [f"Inverted index for '{word}':"]
        for posting in postings:
            result.append(f"  {posting.url}")
            result.append(f"    Frequency: {posting.frequency}")
            result.append(f"    Positions: {posting.positions[:10]}" +
                          ("..." if len(posting.positions) > 10 else ""))
        return "\n".join(result)

    def get_stats(self) -> Dict:
        """Get index statistics"""
        total_words = len(self.index)
        total_postings = sum(len(postings) for postings in self.index.values())

        return {
            'unique_words': total_words,
            'total_postings': total_postings,
            'total_pages': self.next_docid
        }

    def to_dict(self) -> Dict:
        """Convert index to serializable dictionary"""
        return {
            'index': {
                word: [p.to_dict() for p in postings]
                for word, postings in self.index.items()
            },
            'url_to_docid': self.url_to_docid,
            'docid_to_url': self.docid_to_url,
            'next_docid': self.next_docid
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'InvertedIndex':
        """Load index from dictionary"""
        index = cls()
        index.url_to_docid = data['url_to_docid']
        index.docid_to_url = {int(k): v for k, v in data['docid_to_url'].items()}
        index.next_docid = data['next_docid']

        for word, postings_data in data['index'].items():
            index.index[word] = [Posting.from_dict(p) for p in postings_data]

        return index