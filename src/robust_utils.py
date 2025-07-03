"""Enhanced utilities for robust font scraping operations."""

import time
import logging
from typing import Callable, Any, Optional, List, Dict
from functools import wraps
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


def retry_with_backoff(max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 60.0, 
                      exponential_base: float = 2.0, exceptions: tuple = (Exception,)):
    """
    Decorator for retrying functions with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        exponential_base: Base for exponential backoff calculation
        exceptions: Tuple of exception types to catch and retry
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_retries:
                        logger.error(f"Function {func.__name__} failed after {max_retries} retries: {e}")
                        raise
                    
                    delay = min(base_delay * (exponential_base ** attempt), max_delay)
                    logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}. Retrying in {delay:.2f}s...")
                    time.sleep(delay)
            
            return None  # Should never reach here
        return wrapper
    return decorator


class RobustHTTPSession:
    """Enhanced HTTP session with retry logic and robust error handling."""
    
    def __init__(self, timeout: int = 30, max_retries: int = 3):
        self.session = requests.Session()
        self.timeout = timeout
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set default headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 FontScraper/2.0'
        })
    
    @retry_with_backoff(max_retries=2, exceptions=(requests.RequestException,))
    def get(self, url: str, **kwargs) -> requests.Response:
        """Enhanced GET request with automatic retries."""
        try:
            response = self.session.get(url, timeout=self.timeout, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout while fetching {url}")
            raise
        except requests.exceptions.ConnectionError:
            logger.warning(f"Connection error while fetching {url}")
            raise
        except requests.exceptions.HTTPError as e:
            logger.warning(f"HTTP error {e.response.status_code} while fetching {url}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error while fetching {url}: {e}")
            raise
    
    def close(self):
        """Close the session."""
        self.session.close()


class ValidationManager:
    """Enhanced validation for URLs, content, and font data."""
    
    @staticmethod
    def validate_url_comprehensive(url: str) -> Dict[str, Any]:
        """
        Comprehensive URL validation with detailed feedback.
        
        Returns:
            Dict with validation results, suggestions, and normalized URL
        """
        result = {
            'is_valid': False,
            'normalized_url': url,
            'issues': [],
            'suggestions': [],
            'domain_info': {}
        }
        
        try:
            # Basic URL validation
            if not url or not isinstance(url, str):
                result['issues'].append("URL is empty or not a string")
                return result
            
            # Remove whitespace
            url = url.strip()
            result['normalized_url'] = url
            
            # Check for protocol
            if not url.startswith(('http://', 'https://')):
                if '://' in url:
                    result['issues'].append("Unsupported protocol")
                    result['suggestions'].append("Use http:// or https://")
                else:
                    result['normalized_url'] = 'https://' + url
                    result['suggestions'].append("Added https:// protocol")
            
            # Parse URL components
            from urllib.parse import urlparse
            parsed = urlparse(result['normalized_url'])
            
            if not parsed.netloc:
                result['issues'].append("No domain found in URL")
                return result
            
            # Check domain format
            domain_parts = parsed.netloc.split('.')
            if len(domain_parts) < 2:
                result['issues'].append("Invalid domain format")
                return result
            
            # Store domain info
            result['domain_info'] = {
                'domain': parsed.netloc,
                'scheme': parsed.scheme,
                'path': parsed.path,
                'has_www': parsed.netloc.startswith('www.'),
                'tld': domain_parts[-1] if domain_parts else None
            }
            
            # Additional checks
            if len(parsed.netloc) > 253:  # Maximum domain length
                result['issues'].append("Domain name too long")
            
            if any(char in parsed.netloc for char in ' \t\n\r'):
                result['issues'].append("Domain contains invalid characters")
            
            # If no issues found, mark as valid
            if not result['issues']:
                result['is_valid'] = True
            
        except Exception as e:
            result['issues'].append(f"URL parsing error: {e}")
        
        return result
    
    @staticmethod
    def validate_css_content(css_content: str) -> Dict[str, Any]:
        """
        Validate CSS content and provide quality metrics.
        
        Returns:
            Dict with validation results and content metrics
        """
        result = {
            'is_valid': False,
            'issues': [],
            'metrics': {
                'size_bytes': len(css_content.encode('utf-8')),
                'line_count': css_content.count('\n') + 1,
                'font_face_count': css_content.count('@font-face'),
                'import_count': css_content.count('@import'),
                'font_family_count': css_content.count('font-family')
            },
            'warnings': []
        }
        
        try:
            # Basic content checks
            if not css_content or not css_content.strip():
                result['issues'].append("CSS content is empty")
                return result
            
            # Size checks
            if result['metrics']['size_bytes'] > 1024 * 1024:  # 1MB
                result['warnings'].append("CSS file is very large (>1MB)")
            
            # Encoding checks
            try:
                css_content.encode('utf-8')
            except UnicodeEncodeError:
                result['issues'].append("CSS contains invalid UTF-8 characters")
            
            # Basic syntax checks
            open_braces = css_content.count('{')
            close_braces = css_content.count('}')
            if open_braces != close_braces:
                result['issues'].append(f"Mismatched braces: {open_braces} open, {close_braces} close")
            
            # Check for suspicious content
            if '<html' in css_content.lower() or '<body' in css_content.lower():
                result['warnings'].append("CSS content appears to contain HTML")
            
            if result['metrics']['font_face_count'] == 0 and result['metrics']['font_family_count'] == 0:
                result['warnings'].append("No font-related CSS rules found")
            
            # If no critical issues, mark as valid
            if not result['issues']:
                result['is_valid'] = True
            
        except Exception as e:
            result['issues'].append(f"CSS validation error: {e}")
        
        return result
    
    @staticmethod
    def sanitize_filename(filename: str, max_length: int = 255) -> str:
        """
        Sanitize a filename for safe filesystem use.
        
        Args:
            filename: Original filename
            max_length: Maximum allowed length
            
        Returns:
            Sanitized filename
        """
        import re
        
        # Remove or replace invalid characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        # Remove control characters
        sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', sanitized)
        
        # Replace multiple spaces/underscores with single underscore
        sanitized = re.sub(r'[_\s]+', '_', sanitized)
        
        # Trim whitespace and underscores
        sanitized = sanitized.strip('_. ')
        
        # Ensure it's not empty
        if not sanitized:
            sanitized = 'unnamed_file'
        
        # Truncate if too long
        if len(sanitized) > max_length:
            name, ext = os.path.splitext(sanitized)
            max_name_length = max_length - len(ext)
            sanitized = name[:max_name_length] + ext
        
        return sanitized


class PerformanceMonitor:
    """Monitor and track performance metrics during font analysis."""
    
    def __init__(self):
        self.metrics = {
            'start_time': None,
            'end_time': None,
            'duration': None,
            'requests_made': 0,
            'bytes_downloaded': 0,
            'errors_encountered': 0,
            'css_files_processed': 0,
            'fonts_detected': 0,
            'screenshots_captured': 0,
            'memory_usage_mb': 0
        }
    
    def start_monitoring(self):
        """Start performance monitoring."""
        import psutil
        import os
        
        self.metrics['start_time'] = time.time()
        process = psutil.Process(os.getpid())
        self.metrics['memory_usage_mb'] = process.memory_info().rss / 1024 / 1024
    
    def record_request(self, response_size: int = 0):
        """Record a network request."""
        self.metrics['requests_made'] += 1
        self.metrics['bytes_downloaded'] += response_size
    
    def record_error(self):
        """Record an error occurrence."""
        self.metrics['errors_encountered'] += 1
    
    def record_css_processed(self):
        """Record CSS file processing."""
        self.metrics['css_files_processed'] += 1
    
    def record_font_detected(self):
        """Record font detection."""
        self.metrics['fonts_detected'] += 1
    
    def record_screenshot(self):
        """Record screenshot capture."""
        self.metrics['screenshots_captured'] += 1
    
    def end_monitoring(self):
        """End performance monitoring and calculate final metrics."""
        import psutil
        import os
        
        self.metrics['end_time'] = time.time()
        self.metrics['duration'] = self.metrics['end_time'] - self.metrics['start_time']
        
        # Update memory usage
        try:
            process = psutil.Process(os.getpid())
            current_memory = process.memory_info().rss / 1024 / 1024
            self.metrics['memory_usage_mb'] = current_memory
        except:
            pass
    
    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary."""
        if self.metrics['duration']:
            requests_per_second = self.metrics['requests_made'] / self.metrics['duration']
            mb_per_second = (self.metrics['bytes_downloaded'] / 1024 / 1024) / self.metrics['duration']
        else:
            requests_per_second = 0
            mb_per_second = 0
        
        return {
            'duration_seconds': round(self.metrics['duration'] or 0, 2),
            'requests_made': self.metrics['requests_made'],
            'bytes_downloaded': self.metrics['bytes_downloaded'],
            'mb_downloaded': round(self.metrics['bytes_downloaded'] / 1024 / 1024, 2),
            'errors_encountered': self.metrics['errors_encountered'],
            'css_files_processed': self.metrics['css_files_processed'],
            'fonts_detected': self.metrics['fonts_detected'],
            'screenshots_captured': self.metrics['screenshots_captured'],
            'memory_usage_mb': round(self.metrics['memory_usage_mb'], 2),
            'requests_per_second': round(requests_per_second, 2),
            'mb_per_second': round(mb_per_second, 2),
            'success_rate': round((1 - (self.metrics['errors_encountered'] / max(1, self.metrics['requests_made']))) * 100, 2)
        }


def create_progress_bar(description: str, total: int = None):
    """Create a standardized progress bar."""
    from tqdm import tqdm
    
    return tqdm(
        total=total,
        desc=description,
        unit='item',
        bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]'
    )