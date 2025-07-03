"""Font detection and analysis functionality."""

import re
from typing import List, Dict, Set, Optional
from bs4 import BeautifulSoup

from src.utils import Font, ScrapeResults, normalize_font_name, detect_font_provider, is_system_font
from src.scraper import WebScraper
from src.css_parser import CSSParser


class FontDetector:
    """Main font detection engine that coordinates scraping and parsing."""
    
    def __init__(self, timeout: int = 30, user_agent: str = None, delay: float = 1.0, 
                 include_system: bool = True, skip_external: bool = False):
        self.scraper = WebScraper(timeout=timeout, user_agent=user_agent, delay=delay)
        self.include_system = include_system
        self.skip_external = skip_external
        self.detected_fonts: Set[Font] = set()
    
    def analyze_website(self, url: str) -> ScrapeResults:
        """Perform comprehensive font analysis on a website."""
        # Fetch the page content
        results = self.scraper.fetch_page(url)
        
        if results.errors and not hasattr(results, 'css_content'):
            return results
        
        try:
            # Initialize CSS parser with base URL
            css_parser = CSSParser(base_url=url)
            
            all_fonts = []
            
            # Parse all CSS content
            if hasattr(results, 'css_content'):
                for i, css_content in enumerate(results.css_content):
                    source_url = results.css_sources[i] if hasattr(results, 'css_sources') and i < len(results.css_sources) else None
                    fonts = css_parser.parse_css_content(css_content, source_url)
                    all_fonts.extend(fonts)
            
            # Parse HTML for additional font information
            html_content = self._refetch_html_if_needed(url)
            if html_content:
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Extract fonts from inline styles
                inline_styles = self.scraper.extract_style_attributes(soup)
                for style in inline_styles:
                    inline_fonts = self._parse_inline_style(style)
                    all_fonts.extend(inline_fonts)
                
                # Detect web font services
                web_font_services = self.scraper.detect_web_font_services(soup, url)
                service_fonts = self._analyze_web_font_services(web_font_services)
                all_fonts.extend(service_fonts)
            
            # Process additional CSS imports
            css_imports = css_parser.get_css_imports()
            if css_imports and not self.skip_external:
                import_fonts = self._process_css_imports(css_imports, css_parser)
                all_fonts.extend(import_fonts)
            
            # Merge and deduplicate fonts
            merged_fonts = css_parser.merge_duplicate_fonts(all_fonts)
            
            # Filter fonts based on settings
            filtered_fonts = self._filter_fonts(merged_fonts)
            
            # Add fonts to results
            for font in filtered_fonts:
                results.add_font(font)
            
            # Update statistics
            results.update_statistics()
            
        except Exception as e:
            results.add_error(f"Error during font analysis: {str(e)}")
        
        return results
    
    def _refetch_html_if_needed(self, url: str) -> Optional[str]:
        """Refetch HTML content if needed for additional analysis."""
        try:
            return self.scraper._fetch_html(url)
        except Exception:
            return None
    
    def _parse_inline_style(self, style_content: str) -> List[Font]:
        """Parse inline style attributes for font declarations."""
        fonts = []
        
        # Look for font-family declarations
        font_family_pattern = r'font-family\s*:\s*([^;]+)'
        match = re.search(font_family_pattern, style_content, re.IGNORECASE)
        
        if match:
            font_family_value = match.group(1).strip()
            # Parse the font family value
            css_parser = CSSParser()
            font_families = css_parser._parse_font_family_value(font_family_value)
            
            for font_family in font_families:
                font_name = normalize_font_name(font_family)
                if font_name:
                    font_type = 'system' if is_system_font(font_name) else 'custom'
                    
                    font = Font(
                        name=font_name,
                        type=font_type,
                        selectors=['[inline style]']
                    )
                    
                    # Extract weight and style from the inline style
                    font_weight_match = re.search(r'font-weight\s*:\s*([^;]+)', style_content, re.IGNORECASE)
                    if font_weight_match:
                        font.weights = [font_weight_match.group(1).strip()]
                    
                    font_style_match = re.search(r'font-style\s*:\s*([^;]+)', style_content, re.IGNORECASE)
                    if font_style_match:
                        font.styles = [font_style_match.group(1).strip()]
                    
                    fonts.append(font)
        
        return fonts
    
    def _analyze_web_font_services(self, web_font_services: List[Dict[str, str]]) -> List[Font]:
        """Analyze detected web font services to extract font information."""
        fonts = []
        
        for service in web_font_services:
            provider = service['provider']
            url = service['url']
            
            if provider == 'Google Fonts':
                google_fonts = self._analyze_google_fonts_url(url)
                fonts.extend(google_fonts)
            elif provider == 'Adobe Fonts':
                adobe_fonts = self._analyze_adobe_fonts_url(url)
                fonts.extend(adobe_fonts)
            elif provider == 'Font Awesome':
                fa_fonts = self._analyze_font_awesome_url(url)
                fonts.extend(fa_fonts)
            else:
                # Generic web font
                font = Font(
                    name=f"Web Font ({provider})",
                    type='web',
                    source=url,
                    provider=provider
                )
                fonts.append(font)
        
        return fonts
    
    def _analyze_google_fonts_url(self, url: str) -> List[Font]:
        """Extract font information from Google Fonts URLs."""
        fonts = []
        
        # Parse Google Fonts URL to extract family names and variants
        # Example: https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap
        
        family_pattern = r'family=([^&:]+)'
        matches = re.findall(family_pattern, url)
        
        for match in matches:
            font_name = match.replace('+', ' ')
            font = Font(
                name=font_name,
                type='web',
                source=url,
                provider='Google Fonts'
            )
            
            # Try to extract weights from the URL
            weight_pattern = rf'family={re.escape(match)}:wght@([^&]+)'
            weight_match = re.search(weight_pattern, url)
            if weight_match:
                weights = weight_match.group(1).split(';')
                font.weights = weights
            
            # Try to extract styles
            if 'ital' in url:
                font.styles = ['italic']
            else:
                font.styles = ['normal']
            
            fonts.append(font)
        
        return fonts
    
    def _analyze_adobe_fonts_url(self, url: str) -> List[Font]:
        """Extract font information from Adobe Fonts (Typekit) URLs."""
        fonts = []
        
        # Adobe Fonts URLs typically contain kit IDs
        # We can't easily extract font names without additional API calls
        # So we'll create a placeholder entry
        
        kit_pattern = r'/([a-zA-Z0-9]+)\.js'
        match = re.search(kit_pattern, url)
        kit_id = match.group(1) if match else 'unknown'
        
        font = Font(
            name=f"Adobe Fonts Kit ({kit_id})",
            type='web',
            source=url,
            provider='Adobe Fonts'
        )
        fonts.append(font)
        
        return fonts
    
    def _analyze_font_awesome_url(self, url: str) -> List[Font]:
        """Extract Font Awesome information."""
        fonts = []
        
        # Font Awesome is primarily an icon font
        font = Font(
            name="Font Awesome",
            type='web',
            source=url,
            provider='Font Awesome',
            format='icon'
        )
        fonts.append(font)
        
        return fonts
    
    def _process_css_imports(self, css_imports: List[str], css_parser: CSSParser) -> List[Font]:
        """Process additional CSS imports to find more fonts."""
        fonts = []
        
        for import_url in css_imports:
            try:
                css_content = self.scraper._fetch_css(import_url)
                if css_content:
                    import_fonts = css_parser.parse_css_content(css_content, import_url)
                    fonts.extend(import_fonts)
            except Exception as e:
                print(f"Error processing CSS import {import_url}: {e}")
        
        return fonts
    
    def _filter_fonts(self, fonts: List[Font]) -> List[Font]:
        """Filter fonts based on detection settings."""
        filtered_fonts = []
        
        for font in fonts:
            # Skip system fonts if not included
            if not self.include_system and font.type == 'system':
                continue
            
            # Skip fonts without names
            if not font.name or font.name.strip() == '':
                continue
            
            # Skip generic font families
            generic_families = {
                'serif', 'sans-serif', 'monospace', 'cursive', 'fantasy',
                'system-ui', 'ui-serif', 'ui-sans-serif', 'ui-monospace'
            }
            if font.name.lower() in generic_families:
                continue
            
            filtered_fonts.append(font)
        
        return filtered_fonts
    
    def find_font_face_declarations(self, css_content: str) -> List[Dict]:
        """Find all @font-face declarations in CSS content."""
        css_parser = CSSParser()
        fonts = css_parser._parse_font_face_declarations(css_content)
        return [font.font_face_data for font in fonts]
    
    def extract_font_families(self, css_content: str) -> List[str]:
        """Extract all font-family declarations from CSS content."""
        css_parser = CSSParser()
        fonts = css_parser._parse_font_family_declarations(css_content)
        return [font.name for font in fonts]
    
    def detect_web_fonts(self, url: str) -> List[Font]:
        """Detect web fonts specifically (excluding system fonts)."""
        results = self.analyze_website(url)
        return [font for font in results.fonts if font.type == 'web']
    
    def categorize_fonts(self, fonts: List[Font]) -> Dict[str, List[Font]]:
        """Categorize fonts by type."""
        categories = {
            'web': [],
            'system': [],
            'custom': []
        }
        
        for font in fonts:
            if font.type in categories:
                categories[font.type].append(font)
        
        return categories
    
    def close(self):
        """Clean up resources."""
        self.scraper.close()