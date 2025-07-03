"""Web scraping functionality for fetching HTML and CSS content."""

import re
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Tuple, Optional
from urllib.parse import urljoin, urlparse
import time

from font_scraper.utils import ScrapeResults, validate_url


class WebScraper:
    """Web scraper for fetching HTML and CSS content from websites."""
    
    def __init__(self, timeout: int = 30, user_agent: str = None, delay: float = 1.0):
        self.timeout = timeout
        self.delay = delay
        self.session = requests.Session()
        
        # Set user agent
        if user_agent:
            self.session.headers.update({'User-Agent': user_agent})
        else:
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Font-Scraper/1.0'
            })
        
        # Track fetched URLs to avoid duplicates
        self.fetched_urls = set()
    
    def fetch_page(self, url: str) -> ScrapeResults:
        """Fetch a web page and extract all font-related content."""
        results = ScrapeResults(url=url)
        
        if not validate_url(url):
            results.add_error(f"Invalid URL: {url}")
            return results
        
        try:
            # Fetch the main HTML page
            html_content = self._fetch_html(url)
            if not html_content:
                results.add_error(f"Failed to fetch HTML content from {url}")
                return results
            
            # Parse HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract inline CSS
            inline_css = self._extract_inline_css(soup)
            
            # Extract external CSS files
            css_files = self._extract_css_links(soup, url)
            results.css_files = css_files
            
            # Fetch external CSS content
            css_contents = []
            for css_url in css_files:
                css_content = self._fetch_css(css_url)
                if css_content:
                    css_contents.append((css_content, css_url))
                else:
                    results.add_error(f"Failed to fetch CSS from {css_url}")
            
            # Store all CSS content
            results.css_content = inline_css + [content for content, _ in css_contents]
            results.css_sources = ['inline'] + [url for _, url in css_contents]
            
        except Exception as e:
            results.add_error(f"Error fetching page {url}: {str(e)}")
        
        return results
    
    def _fetch_html(self, url: str) -> Optional[str]:
        """Fetch HTML content from a URL."""
        try:
            if url in self.fetched_urls:
                return None
            
            self.fetched_urls.add(url)
            
            # Add delay to be respectful
            if len(self.fetched_urls) > 1:
                time.sleep(self.delay)
            
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            # Try to detect encoding
            if response.encoding == 'ISO-8859-1':
                # requests guessed wrong, try to detect from content
                response.encoding = response.apparent_encoding
            
            return response.text
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching HTML from {url}: {e}")
            return None
    
    def _fetch_css(self, css_url: str) -> Optional[str]:
        """Fetch CSS content from a URL."""
        try:
            if css_url in self.fetched_urls:
                return None
            
            self.fetched_urls.add(css_url)
            
            # Add delay to be respectful
            time.sleep(self.delay)
            
            response = self.session.get(css_url, timeout=self.timeout)
            response.raise_for_status()
            
            # CSS should be text
            if 'text/css' not in response.headers.get('content-type', '').lower():
                # Check if it looks like CSS anyway
                content = response.text
                if not any(marker in content.lower() for marker in ['@', '{', '}', 'font-family']):
                    return None
            
            return response.text
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching CSS from {css_url}: {e}")
            return None
    
    def _extract_inline_css(self, soup: BeautifulSoup) -> List[str]:
        """Extract inline CSS from <style> tags."""
        inline_css = []
        
        # Find all <style> tags
        style_tags = soup.find_all('style')
        
        for style_tag in style_tags:
            if style_tag.string:
                inline_css.append(style_tag.string)
            elif style_tag.get_text():
                inline_css.append(style_tag.get_text())
        
        return inline_css
    
    def _extract_css_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract external CSS file URLs from <link> tags."""
        css_urls = []
        
        # Find all <link> tags with CSS
        link_tags = soup.find_all('link', rel=lambda x: x and 'stylesheet' in x)
        
        for link_tag in link_tags:
            href = link_tag.get('href')
            if href:
                # Resolve relative URLs
                css_url = urljoin(base_url, href)
                css_urls.append(css_url)
        
        # Also check for @import in style tags (basic check)
        style_tags = soup.find_all('style')
        for style_tag in style_tags:
            if style_tag.string or style_tag.get_text():
                content = style_tag.string or style_tag.get_text()
                imports = self._extract_css_imports_from_text(content, base_url)
                css_urls.extend(imports)
        
        return css_urls
    
    def _extract_css_imports_from_text(self, css_content: str, base_url: str) -> List[str]:
        """Extract @import URLs from CSS content."""
        imports = []
        
        # Pattern to match @import statements
        import_pattern = r'@import\s+(?:url\()?["\']?([^"\';\)]+)["\']?\)?[^;]*;'
        matches = re.finditer(import_pattern, css_content, re.IGNORECASE)
        
        for match in matches:
            import_url = match.group(1).strip()
            # Resolve relative URLs
            full_url = urljoin(base_url, import_url)
            imports.append(full_url)
        
        return imports
    
    def fetch_css_files(self, css_urls: List[str]) -> Dict[str, str]:
        """Fetch multiple CSS files and return their content."""
        css_contents = {}
        
        for css_url in css_urls:
            content = self._fetch_css(css_url)
            if content:
                css_contents[css_url] = content
        
        return css_contents
    
    def handle_redirects(self, url: str) -> str:
        """Follow redirects and return the final URL."""
        try:
            response = self.session.head(url, timeout=self.timeout, allow_redirects=True)
            return response.url
        except requests.exceptions.RequestException:
            return url
    
    def detect_web_font_services(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Detect common web font services from HTML."""
        web_fonts = []
        
        # Check for Google Fonts
        google_font_links = soup.find_all('link', href=lambda x: x and 'fonts.googleapis.com' in x)
        for link in google_font_links:
            web_fonts.append({
                'provider': 'Google Fonts',
                'url': urljoin(base_url, link.get('href')),
                'type': 'link'
            })
        
        # Check for Adobe Fonts (Typekit)
        adobe_scripts = soup.find_all('script', src=lambda x: x and ('use.typekit.net' in x or 'use.typekit.com' in x))
        for script in adobe_scripts:
            web_fonts.append({
                'provider': 'Adobe Fonts',
                'url': urljoin(base_url, script.get('src')),
                'type': 'script'
            })
        
        # Check for Font Awesome
        fa_links = soup.find_all('link', href=lambda x: x and ('fontawesome' in x or 'font-awesome' in x))
        for link in fa_links:
            web_fonts.append({
                'provider': 'Font Awesome',
                'url': urljoin(base_url, link.get('href')),
                'type': 'link'
            })
        
        # Check for other CDN fonts
        cdn_patterns = [
            (r'cdnjs\.cloudflare\.com.*font', 'CDNJS'),
            (r'fonts\.com', 'Fonts.com'),
            (r'webtype\.com', 'Webtype'),
            (r'typography\.com', 'Typography.com')
        ]
        
        for pattern, provider in cdn_patterns:
            links = soup.find_all('link', href=lambda x: x and re.search(pattern, x, re.IGNORECASE))
            for link in links:
                web_fonts.append({
                    'provider': provider,
                    'url': urljoin(base_url, link.get('href')),
                    'type': 'link'
                })
        
        return web_fonts
    
    def extract_style_attributes(self, soup: BeautifulSoup) -> List[str]:
        """Extract inline style attributes that might contain font declarations."""
        inline_styles = []
        
        # Find all elements with style attributes
        elements_with_style = soup.find_all(attrs={'style': True})
        
        for element in elements_with_style:
            style_content = element.get('style', '')
            if 'font' in style_content.lower():
                inline_styles.append(style_content)
        
        return inline_styles
    
    def close(self):
        """Close the session."""
        self.session.close()