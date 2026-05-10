"""
Storage handler for saving/loading inverted index to/from disk
"""
import json
import os
from typing import Optional


class IndexStorage:
    """Handles saving and loading the inverted index to/from filesystem"""

    DEFAULT_INDEX_FILE = "data/index.json"

    @staticmethod
    def save(index, filepath: str = DEFAULT_INDEX_FILE) -> bool:
        """
        Save inverted index to file

        Args:
            index: InvertedIndex object
            filepath: Path to save index file

        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure directory exists
            directory = os.path.dirname(filepath)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)

            # Convert index to serializable dict
            index_data = index.to_dict()

            # Save to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, indent=2, ensure_ascii=False)

            print(f"Index saved to {filepath}")
            return True

        except Exception as e:
            print(f"Error saving index: {e}")
            return False

    @staticmethod
    def load(filepath: str = DEFAULT_INDEX_FILE) -> Optional[object]:
        """
        Load inverted index from file

        Args:
            filepath: Path to index file

        Returns:
            InvertedIndex object or None if load fails
        """
        try:
            if not os.path.exists(filepath):
                print(f"Index file not found: {filepath}")
                return None

            with open(filepath, 'r', encoding='utf-8') as f:
                index_data = json.load(f)

            # Import here to avoid circular import
            from indexer import InvertedIndex
            index = InvertedIndex.from_dict(index_data)

            print(f"Index loaded from {filepath}")
            return index

        except Exception as e:
            print(f"Error loading index: {e}")
            return None

    @staticmethod
    def index_exists(filepath: str = DEFAULT_INDEX_FILE) -> bool:
        """Check if index file exists"""
        return os.path.exists(filepath)