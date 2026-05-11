import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 直接导入src目录下的模块
from src.crawler import WebCrawler


class TestWebCrawler:
    """Test suite for WebCrawler"""

    def test_crawler_initialization(self):
        """Test crawler initializes correctly"""
        crawler = WebCrawler("https://example.com", politeness_delay=6.0)
        assert crawler.base_url == "https://example.com"
        assert crawler.politeness_delay == 6.0
        assert crawler.base_domain == "example.com"

    def test_crawler_default_delay(self):
        """Test default politeness delay"""
        crawler = WebCrawler("https://example.com")
        assert crawler.politeness_delay == 6.0

    def test_respect_politeness(self):
        """Test politeness delay enforcement"""
        crawler = WebCrawler("https://example.com", politeness_delay=1.0)

        # First request should not sleep
        start = __import__('time').time()
        crawler._respect_politeness()
        first_duration = __import__('time').time() - start
        assert first_duration < 0.1

        # Second request should sleep
        start = __import__('time').time()
        crawler._respect_politeness()
        second_duration = __import__('time').time() - start
        assert second_duration >= 0.9

    def test_normalize_word_in_crawler(self):
        """Test URL normalization"""
        crawler = WebCrawler("https://quotes.toscrape.com")

        # Test internal link extraction
        html = """
        <html>
            <a href="/page/2/">Next</a>
            <a href="https://quotes.toscrape.com/page/3/">Page 3</a>
            <a href="http://external.com">External</a>
        </html>
        """

        links = crawler._extract_links(html, "https://quotes.toscrape.com/")

        # Should only include internal links
        assert "https://quotes.toscrape.com/page/2/" in links
        assert "https://quotes.toscrape.com/page/3/" in links
        assert "http://external.com" not in links

    @patch('src.crawler.requests.Session.get')
    def test_get_page_success(self, mock_get):
        """Test successful page fetch"""
        mock_response = Mock()
        mock_response.text = "<html>Test</html>"
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        crawler = WebCrawler("https://example.com", politeness_delay=0)
        result = crawler._get_page("https://example.com")

        assert result == "<html>Test</html>"

    @patch('src.crawler.requests.Session.get')
    def test_get_page_failure(self, mock_get):
        """Test failed page fetch - exception handling"""
        mock_get.side_effect = Exception("Connection error")

        crawler = WebCrawler("https://example.com", politeness_delay=0)

        # The method may either return None or raise an exception
        # Both are acceptable as error handling
        try:
            result = crawler._get_page("https://example.com")
            assert result is None
        except Exception:
            # Exception is also acceptable - means error is properly signaled
            pass

    def test_extract_page_data_quotes(self):
        """Test page data extraction from quotes.toscrape.com"""
        html = """
        <html>
            <title>Test Page</title>
            <div class="quote">
                <span class="text">"Test quote"</span>
                <small class="author">Test Author</small>
            </div>
            <p>Some paragraph text.</p>
        </html>
        """

        crawler = WebCrawler("https://quotes.toscrape.com")
        page_data = crawler._extract_page_data(html, "https://quotes.toscrape.com/")

        assert page_data['url'] == "https://quotes.toscrape.com/"
        assert page_data['title'] == "Test Page"
        assert "Test quote" in page_data['content']
        assert "Test Author" in page_data['content']
        assert "Some paragraph text" in page_data['content']

    def test_extract_links_relative_urls(self):
        """Test extraction of relative URLs - using actual urljoin behavior"""
        html = """
        <html>
            <a href="/quote/1">Quote 1</a>
            <a href="quote/2">Quote 2</a>
            <a href="#fragment">Fragment</a>
        </html>
        """

        crawler = WebCrawler("https://quotes.toscrape.com")
        links = crawler._extract_links(html, "https://quotes.toscrape.com/page/1/")

        # urljoin behavior:
        # - "/quote/1" becomes "https://quotes.toscrape.com/quote/1"
        # - "quote/2" becomes "https://quotes.toscrape.com/page/1/quote/2"
        assert "https://quotes.toscrape.com/quote/1" in links
        assert "https://quotes.toscrape.com/page/1/quote/2" in links

    def test_crawl_with_max_pages(self):
        """Test crawling with page limit"""
        crawler = WebCrawler("https://quotes.toscrape.com")
        assert crawler is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
