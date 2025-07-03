"""Utility functions and data structures for the font scraper."""

import re
import urllib.parse
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from urllib.parse import urljoin, urlparse


@dataclass
class Font:
    """Represents a detected font with all its properties."""
    name: str
    type: str  # 'web', 'system', 'custom'
    source: Optional[str] = None  # URL or file path
    weights: List[str] = field(default_factory=list)
    styles: List[str] = field(default_factory=list)
    format: Optional[str] = None  # Font format (woff2, ttf, etc.)
    provider: Optional[str] = None  # Google, Adobe, Custom, etc.
    selectors: List[str] = field(default_factory=list)  # CSS selectors using this font
    font_face_data: Dict = field(default_factory=dict)  # Raw @font-face data
    unicode_range: Optional[str] = None
    
    def __hash__(self):
        return hash((self.name, self.type, self.source))


@dataclass
class ScrapeResults:
    """Container for all scraping results."""
    url: str
    fonts: List[Font] = field(default_factory=list)
    css_files: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    statistics: Dict[str, int] = field(default_factory=dict)
    
    def add_font(self, font: Font) -> None:
        """Add a font to results, avoiding duplicates."""
        if font not in self.fonts:
            self.fonts.append(font)
    
    def add_error(self, error: str) -> None:
        """Add an error message."""
        self.errors.append(error)
    
    def update_statistics(self) -> None:
        """Update statistics based on current fonts."""
        self.statistics = {
            'total_fonts': len(self.fonts),
            'web_fonts': len([f for f in self.fonts if f.type == 'web']),
            'system_fonts': len([f for f in self.fonts if f.type == 'system']),
            'custom_fonts': len([f for f in self.fonts if f.type == 'custom']),
            'css_files': len(self.css_files),
            'google_fonts': len([f for f in self.fonts if f.provider == 'Google Fonts']),
            'adobe_fonts': len([f for f in self.fonts if f.provider == 'Adobe Fonts']),
        }


def normalize_font_name(font_name: str) -> str:
    """Normalize font family names by removing quotes and extra whitespace."""
    if not font_name:
        return ""
    
    # Remove quotes and normalize whitespace
    normalized = re.sub(r'^["\']|["\']$', '', font_name.strip())
    normalized = re.sub(r'\s+', ' ', normalized)
    return normalized


def is_web_font_url(url: str) -> bool:
    """Check if URL is likely a web font file."""
    font_extensions = {'.woff', '.woff2', '.ttf', '.otf', '.eot', '.svg'}
    parsed = urlparse(url.lower())
    path = parsed.path
    return any(path.endswith(ext) for ext in font_extensions)


def detect_font_provider(url: str) -> Optional[str]:
    """Detect the font provider from a URL."""
    if not url:
        return None
    
    url_lower = url.lower()
    
    if 'fonts.googleapis.com' in url_lower or 'fonts.gstatic.com' in url_lower:
        return 'Google Fonts'
    elif 'use.typekit.net' in url_lower or 'use.typekit.com' in url_lower:
        return 'Adobe Fonts'
    elif 'fontawesome' in url_lower:
        return 'Font Awesome'
    elif 'cdnjs.cloudflare.com' in url_lower and 'font' in url_lower:
        return 'CDNJS'
    elif any(domain in url_lower for domain in ['fonts.com', 'webtype.com', 'typography.com']):
        return 'Commercial Web Fonts'
    
    return 'Custom'


def extract_font_weight_from_name(font_name: str) -> List[str]:
    """Extract font weights from font family names that include weight info."""
    weights = []
    weight_patterns = {
        r'\bthin\b': '100',
        r'\bextra-?light\b': '200',
        r'\blight\b': '300',
        r'\bregular\b': '400',
        r'\bnormal\b': '400',
        r'\bmedium\b': '500',
        r'\bsemi-?bold\b': '600',
        r'\bbold\b': '700',
        r'\bextra-?bold\b': '800',
        r'\bheavy\b': '900',
        r'\bblack\b': '900',
    }
    
    for pattern, weight in weight_patterns.items():
        if re.search(pattern, font_name, re.IGNORECASE):
            weights.append(weight)
    
    return weights or ['400']  # Default to normal weight


def extract_font_style_from_name(font_name: str) -> List[str]:
    """Extract font styles from font family names that include style info."""
    styles = []
    
    if re.search(r'\bitalic\b', font_name, re.IGNORECASE):
        styles.append('italic')
    if re.search(r'\boblique\b', font_name, re.IGNORECASE):
        styles.append('oblique')
    
    return styles or ['normal']


def clean_css_value(value: str) -> str:
    """Clean CSS property values by removing extra whitespace and quotes."""
    if not value:
        return ""
    
    # Remove extra whitespace
    cleaned = re.sub(r'\s+', ' ', value.strip())
    
    # Remove quotes around the entire value if present
    cleaned = re.sub(r'^["\']|["\']$', '', cleaned)
    
    return cleaned


def parse_font_face_src(src_value: str, base_url: str) -> List[Dict[str, str]]:
    """Parse @font-face src property to extract font URLs and formats."""
    sources = []
    
    # Split by comma but respect parentheses
    src_parts = []
    current_part = ""
    paren_depth = 0
    
    for char in src_value:
        if char == '(':
            paren_depth += 1
        elif char == ')':
            paren_depth -= 1
        elif char == ',' and paren_depth == 0:
            src_parts.append(current_part.strip())
            current_part = ""
            continue
        current_part += char
    
    if current_part.strip():
        src_parts.append(current_part.strip())
    
    for part in src_parts:
        # Extract URL from url() function
        url_match = re.search(r'url\s*\(\s*["\']?([^"\']+)["\']?\s*\)', part)
        if url_match:
            url = url_match.group(1)
            # Resolve relative URLs
            if base_url:
                url = urljoin(base_url, url)
            
            # Extract format if specified
            format_match = re.search(r'format\s*\(\s*["\']?([^"\']+)["\']?\s*\)', part)
            format_type = format_match.group(1) if format_match else None
            
            # Infer format from URL if not specified
            if not format_type and is_web_font_url(url):
                if url.endswith('.woff2'):
                    format_type = 'woff2'
                elif url.endswith('.woff'):
                    format_type = 'woff'
                elif url.endswith('.ttf'):
                    format_type = 'truetype'
                elif url.endswith('.otf'):
                    format_type = 'opentype'
                elif url.endswith('.eot'):
                    format_type = 'embedded-opentype'
            
            sources.append({
                'url': url,
                'format': format_type
            })
    
    return sources


def is_system_font(font_name: str) -> bool:
    """Check if a font name refers to a common system font."""
    system_fonts = {
        'arial', 'helvetica', 'times', 'times new roman', 'courier', 'courier new',
        'verdana', 'georgia', 'palatino', 'garamond', 'bookman', 'comic sans ms',
        'trebuchet ms', 'arial black', 'impact', 'lucida sans unicode',
        'tahoma', 'lucida console', 'monaco', 'bradley hand', 'brush script mt',
        'luminari', 'marker felt', 'papyrus', 'system-ui', '-apple-system',
        'blinkmacsystemfont', 'segoe ui', 'roboto', 'helvetica neue',
        'arial unicode ms', 'avenir', 'menlo', 'consolas', 'dejavu sans',
        'liberation sans', 'noto sans', 'droid sans', 'cantarell', 'oxygen',
        'ubuntu', 'franklin gothic medium', 'century gothic', 'calibri',
        'cambria', 'optima', 'gill sans', 'futura', 'avant garde'
    }
    
    return normalize_font_name(font_name).lower() in system_fonts


def validate_url(url: str) -> bool:
    """Validate if a string is a proper URL."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False