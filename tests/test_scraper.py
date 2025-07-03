"""Tests for the web scraper functionality."""

import unittest
from unittest.mock import patch, Mock
import sys
import os

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from scraper import WebScraper
from utils import ScrapeResults


class TestWebScraper(unittest.TestCase):
    """Test cases for WebScraper class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.scraper = WebScraper(timeout=10, delay=0.1)
    
    def tearDown(self):
        """Clean up after tests."""
        self.scraper.close()
    
    def test_scraper_initialization(self):
        """Test scraper initialization."""
        self.assertEqual(self.scraper.timeout, 10)
        self.assertEqual(self.scraper.delay, 0.1)
        self.assertIsNotNone(self.scraper.session)
    
    @patch('requests.Session.get')
    def test_fetch_html_success(self, mock_get):
        """Test successful HTML fetching."""
        mock_response = Mock()
        mock_response.text = '<html><body>Test</body></html>'
        mock_response.encoding = 'utf-8'
        mock_get.return_value = mock_response
        
        result = self.scraper._fetch_html('https://example.com')
        self.assertEqual(result, '<html><body>Test</body></html>')
    
    @patch('requests.Session.get')
    def test_fetch_html_failure(self, mock_get):
        """Test HTML fetching failure."""
        mock_get.side_effect = Exception("Network error")
        
        result = self.scraper._fetch_html('https://example.com')
        self.assertIsNone(result)
    
    def test_extract_inline_css(self):
        """Test extraction of inline CSS."""
        from bs4 import BeautifulSoup
        
        html = '''
        <html>
            <head>
                <style>
                    body { font-family: Arial; }
                    .header { font-family: "Roboto"; }
                </style>
            </head>
            <body>
                <style>
                    .footer { font-family: Georgia; }
                </style>
            </body>
        </html>
        '''
        
        soup = BeautifulSoup(html, 'html.parser')
        css_content = self.scraper._extract_inline_css(soup)
        
        self.assertEqual(len(css_content), 2)
        self.assertIn('font-family: Arial', css_content[0])
        self.assertIn('font-family: Georgia', css_content[1])
    
    def test_extract_css_links(self):
        """Test extraction of CSS links."""
        from bs4 import BeautifulSoup
        
        html = '''
        <html>
            <head>
                <link rel="stylesheet" href="/styles.css">
                <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Roboto">
                <link rel="icon" href="/favicon.ico">
            </head>
        </html>
        '''
        
        soup = BeautifulSoup(html, 'html.parser')
        css_urls = self.scraper._extract_css_links(soup, 'https://example.com')
        
        self.assertEqual(len(css_urls), 2)
        self.assertIn('https://example.com/styles.css', css_urls)
        self.assertIn('https://fonts.googleapis.com/css?family=Roboto', css_urls)


if __name__ == '__main__':
    unittest.main()