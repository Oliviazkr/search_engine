#!/usr/bin/env python3
"""
Search Engine Tool - Command Line Interface
Provides commands: build, load, print, find
"""
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crawler import WebCrawler
from indexer import InvertedIndex
from storage import IndexStorage
from search import SearchEngine


class SearchShell:
    """Command-line interface for the search engine"""

    def __init__(self):
        self.search_engine = SearchEngine()
        self.index_storage = IndexStorage()
        self.is_running = True
        self.target_url = "https://quotes.toscrape.com/"
        self.politeness_delay = 6.0

    def display_welcome(self):
        """Display welcome message and help"""
        print("\n" + "=" * 60)
        print("Search Engine Tool - XJCO3011 Coursework 2")
        print("=" * 60)
        print("\nAvailable commands:")
        print("  build                     - Crawl website and build inverted index")
        print("  load                      - Load previously saved index from disk")
        print("  print <word>              - Print inverted index for a word")
        print("  find <word/phrase>        - Find pages containing search terms")
        print("  stats                     - Show index statistics")
        print("  help                      - Show this help message")
        print("  exit / quit               - Exit the program")
        print()

    def do_build(self) -> bool:
        """
        Execute build command: crawl website and build index

        Returns:
            True if successful, False otherwise
        """
        print("\n[BUILD] Starting index build process...")
        print(f"Target URL: {self.target_url}")
        print(f"Politeness delay: {self.politeness_delay} seconds")
        print("Note: This may take several minutes due to politeness delay.")

        # Initialize crawler
        crawler = WebCrawler(self.target_url, self.politeness_delay)

        try:
            # Crawl all pages
            pages = crawler.crawl()

            if not pages:
                print("Error: No pages were crawled. Check your internet connection.")
                return False

            # Build inverted index
            print(f"\nBuilding inverted index from {len(pages)} pages...")
            index = InvertedIndex()

            for url, page_data in pages.items():
                index.add_page(
                    url=url,
                    content=page_data['content'],
                    title=page_data['title']
                )

            # Save index to disk
            print("Saving index to disk...")
            if self.index_storage.save(index):
                self.search_engine.set_index(index)
                stats = index.get_stats()
                print(f"\nBuild complete!")
                print(f"  - Pages indexed: {stats['total_pages']}")
                print(f"  - Unique words: {stats['unique_words']}")
                print(f"  - Total postings: {stats['total_postings']}")
                return True
            else:
                print("Error: Failed to save index.")
                return False

        except Exception as e:
            print(f"Error during build: {e}")
            return False
        finally:
            crawler.close()

    def do_load(self) -> bool:
        """
        Execute load command: load index from disk

        Returns:
            True if successful, False otherwise
        """
        print("\n[LOAD] Loading index from disk...")

        index = self.index_storage.load()

        if index:
            self.search_engine.set_index(index)
            stats = index.get_stats()
            print(f"Load successful!")
            print(f"  - Pages indexed: {stats['total_pages']}")
            print(f"  - Unique words: {stats['unique_words']}")
            print(f"  - Total postings: {stats['total_postings']}")
            return True
        else:
            print("Load failed. Use 'build' command first to create an index.")
            return False

    def do_print(self, word: str) -> bool:
        """
        Execute print command: print inverted index for a word

        Args:
            word: Word to look up

        Returns:
            True if successful, False otherwise
        """
        if not word:
            print("Usage: print <word>")
            return False

        print(f"\n[PRINT] Looking up word: '{word}'")
        result = self.search_engine.print_index(word)
        print(result)
        return True

    def do_find(self, query: str) -> bool:
        """
        Execute find command: search for pages containing query

        Args:
            query: Search query (single word or phrase)

        Returns:
            True if successful, False otherwise
        """
        if not query:
            print("Usage: find <word or phrase>")
            print("Examples:")
            print("  find love")
            print("  find good friends")
            return False

        print(f"\n[FIND] Searching for: '{query}'")
        results = self.search_engine.find(query)
        for line in results:
            print(line)
        return True

    def do_stats(self):
        """Display index statistics"""
        print("\n[STATS] Index Statistics:")
        if self.search_engine.has_index():
            stats = self.search_engine.get_index_stats()
            print(f"  Total pages indexed: {stats['total_pages']}")
            print(f"  Unique words in index: {stats['unique_words']}")
            print(f"  Total word occurrences (postings): {stats['total_postings']}")
        else:
            print("  No index loaded. Use 'build' or 'load' first.")

    def process_command(self, command_line: str) -> bool:
        """
        Parse and execute a command

        Args:
            command_line: Raw input from user

        Returns:
            False if should exit, True otherwise
        """
        if not command_line.strip():
            return True

        parts = command_line.strip().split()
        command = parts[0].lower()

        if command in ['exit', 'quit']:
            print("\nGoodbye!")
            return False

        elif command == 'help':
            self.display_welcome()

        elif command == 'build':
            self.do_build()

        elif command == 'load':
            self.do_load()

        elif command == 'print':
            word = ' '.join(parts[1:]) if len(parts) > 1 else ''
            self.do_print(word)

        elif command == 'find':
            query = ' '.join(parts[1:]) if len(parts) > 1 else ''
            self.do_find(query)

        elif command == 'stats':
            self.do_stats()

        else:
            print(f"Unknown command: '{command}'")
            print("Type 'help' for available commands.")

        return True

    def run(self):
        """Main shell loop"""
        self.display_welcome()

        while self.is_running:
            try:
                user_input = input("\n> ")
                self.is_running = self.process_command(user_input)
            except KeyboardInterrupt:
                print("\n\nInterrupted. Goodbye!")
                break
            except EOFError:
                print("\nGoodbye!")
                break


def main():
    """Entry point"""
    shell = SearchShell()
    shell.run()


if __name__ == "__main__":
    main()