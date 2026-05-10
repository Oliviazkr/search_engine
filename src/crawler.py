"""
Web crawler for quotes.toscrape.com
Respects politeness window of 6 seconds between requests
"""
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import Set, List, Dict, Optional
from collections import deque


class WebCrawler:
    """Crawler that respects politeness window and extracts page content"""

    def __init__(self, base_url: str, politeness_delay: float = 6.0):
        """
        Initialize crawler with base URL and politeness delay

        Args:
            base_url: Starting URL for crawling
            politeness_delay: Minimum seconds between requests (default 6)
        """
        self.base_url = base_url
        self.base_domain = urlparse(base_url).netloc
        self.politeness_delay = politeness_delay
        self.last_request_time = 0
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'XJCO3011-SearchEngine/1.0 (Educational Project)'
        })

    def _respect_politeness(self):
        """Ensure minimum time between requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.politeness_delay:
            sleep_time = self.politeness_delay - time_since_last
            time.sleep(sleep_time)
        self.last_request_time = time.time()

    def _get_page(self, url: str) -> Optional[str]:
        """
        Fetch a page and return its HTML content

        Returns:
            HTML string or None if request fails
        """
        self._respect_politeness()

        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def _extract_links(self, html: str, current_url: str) -> Set[str]:
        """
        Extract all internal links from HTML page

        Returns:
            Set of absolute URLs to pages within the same domain
        """
        soup = BeautifulSoup(html, 'html.parser')
        links = set()

        for anchor in soup.find_all('a', href=True):
            href = anchor['href']
            # Convert relative URL to absolute
            absolute_url = urljoin(current_url, href)

            # Only include links to same domain
            if urlparse(absolute_url).netloc == self.base_domain:
                # Clean the URL (remove fragments)
                parsed = urlparse(absolute_url)
                clean_url = parsed._replace(fragment='').geturl()
                links.add(clean_url)

        return links

    def _extract_page_data(self, html: str, url: str) -> Dict:
        """
        Extract title and main content from page

        Returns:
            Dictionary with url, title, and content text
        """
        soup = BeautifulSoup(html, 'html.parser')

        # Extract title
        title_tag = soup.find('title')
        title = title_tag.get_text(strip=True) if title_tag else url

        # Extract main content - for quotes.toscrape.com
        # Get all quote text and author names
        content_parts = []

        # Get quotes
        for quote in soup.find_all('div', class_='quote'):
            text = quote.find('span', class_='text')
            if text:
                content_parts.append(text.get_text(strip=True))

            author = quote.find('small', class_='author')
            if author:
                content_parts.append(author.get_text(strip=True))

        # Also get any paragraph text
        for paragraph in soup.find_all('p'):
            content_parts.append(paragraph.get_text(strip=True))

        # Get heading text
        for heading in soup.find_all(['h1', 'h2', 'h3']):
            content_parts.append(heading.get_text(strip=True))

        content = ' '.join(content_parts)

        return {
            'url': url,
            'title': title,
            'content': content
        }

    def crawl(self, max_pages: Optional[int] = None) -> Dict[str, Dict]:
        """
        Crawl the website starting from base_url

        Args:
            max_pages: Maximum number of pages to crawl (None for all)

        Returns:
            Dictionary mapping URL to page data
        """
        pages = {}
        to_visit = deque([self.base_url])
        visited = set()

        print(f"Starting crawl from {self.base_url}")
        print(f"Politeness delay: {self.politeness_delay} seconds")

        while to_visit:
            # Check max pages limit
            if max_pages and len(pages) >= max_pages:
                print(f"Reached max pages limit: {max_pages}")
                break

            url = to_visit.popleft()

            if url in visited:
                continue

            visited.add(url)
            print(f"Crawling: {url} (Page {len(pages) + 1})")

            # Fetch page
            html = self._get_page(url)
            if html is None:
                continue

            # Extract page data
            page_data = self._extract_page_data(html, url)
            pages[url] = page_data

            # Extract and queue new links
            new_links = self._extract_links(html, url)
            for link in new_links:
                if link not in visited and link not in to_visit:
                    to_visit.append(link)

        print(f"Crawl complete. {len(pages)} pages indexed.")
        return pages

    def close(self):
        """Close the session"""
        self.session.close()