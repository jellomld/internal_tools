"""CSS parsing functionality for extracting font information."""

import re
import cssutils
import tinycss2
from typing import List, Dict, Tuple, Optional, Set
from urllib.parse import urljoin

from src.utils import (
    Font, normalize_font_name, clean_css_value, parse_font_face_src,
    detect_font_provider, is_system_font, extract_font_weight_from_name,
    extract_font_style_from_name
)


class CSSParser:
    """Parser for CSS content to extract font information."""
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url
        self.parsed_fonts: Set[Font] = set()
        self.css_imports: List[str] = []
        
        # Configure cssutils to suppress warnings
        cssutils.log.setLevel('ERROR')
    
    def parse_css_content(self, css_content: str, source_url: str = None) -> List[Font]:
        """Parse CSS content and extract all font information."""
        fonts = []
        
        try:
            # Parse @font-face declarations
            fonts.extend(self._parse_font_face_declarations(css_content, source_url))
            
            # Parse font-family declarations
            fonts.extend(self._parse_font_family_declarations(css_content))
            
            # Extract CSS imports for later processing
            self.css_imports.extend(self._extract_css_imports(css_content))
            
        except Exception as e:
            print(f"Error parsing CSS: {e}")
        
        return fonts
    
    def _parse_font_face_declarations(self, css_content: str, source_url: str = None) -> List[Font]:
        """Extract fonts from @font-face declarations."""
        fonts = []
        
        # Find all @font-face blocks
        font_face_pattern = r'@font-face\s*\{([^}]+)\}'
        matches = re.finditer(font_face_pattern, css_content, re.IGNORECASE | re.DOTALL)
        
        for match in matches:
            font_face_block = match.group(1)
            font = self._parse_single_font_face(font_face_block, source_url)
            if font:
                fonts.append(font)
        
        return fonts
    
    def _parse_single_font_face(self, font_face_block: str, source_url: str = None) -> Optional[Font]:
        """Parse a single @font-face declaration."""
        font_data = {}
        
        # Extract properties from the font-face block
        properties = self._extract_css_properties(font_face_block)
        
        font_family = properties.get('font-family')
        if not font_family:
            return None
        
        font_family = normalize_font_name(font_family)
        
        # Extract src URLs
        src_value = properties.get('src', '')
        sources = parse_font_face_src(src_value, self.base_url or source_url)
        
        if not sources:
            return None
        
        # Use the first source as primary
        primary_source = sources[0]
        
        font = Font(
            name=font_family,
            type='web',
            source=primary_source['url'],
            format=primary_source['format'],
            provider=detect_font_provider(primary_source['url']),
            font_face_data=properties
        )
        
        # Extract weight and style from properties
        if 'font-weight' in properties:
            weight_value = clean_css_value(properties['font-weight'])
            if weight_value and weight_value != 'normal':
                font.weights = [weight_value]
            else:
                font.weights = ['400']
        
        if 'font-style' in properties:
            style_value = clean_css_value(properties['font-style'])
            if style_value and style_value != 'normal':
                font.styles = [style_value]
            else:
                font.styles = ['normal']
        
        # Extract unicode-range if present
        if 'unicode-range' in properties:
            font.unicode_range = properties['unicode-range']
        
        return font
    
    def _parse_font_family_declarations(self, css_content: str) -> List[Font]:
        """Extract fonts from font-family declarations in CSS rules."""
        fonts = []
        
        try:
            # Use cssutils for more robust CSS parsing
            stylesheet = cssutils.parseString(css_content)
            
            for rule in stylesheet:
                if rule.type == rule.STYLE_RULE:
                    fonts.extend(self._extract_fonts_from_style_rule(rule))
                elif rule.type == rule.MEDIA_RULE:
                    # Handle media queries
                    for media_rule in rule:
                        if hasattr(media_rule, 'style'):
                            fonts.extend(self._extract_fonts_from_style_rule(media_rule))
        except Exception:
            # Fallback to regex parsing if cssutils fails
            fonts.extend(self._regex_parse_font_families(css_content))
        
        return fonts
    
    def _extract_fonts_from_style_rule(self, rule) -> List[Font]:
        """Extract fonts from a CSS style rule."""
        fonts = []
        
        if not hasattr(rule, 'style'):
            return fonts
        
        selector_text = rule.selectorText if hasattr(rule, 'selectorText') else ''
        
        # Check for font-family property
        font_family_value = rule.style.getPropertyValue('font-family')
        if font_family_value:
            font_families = self._parse_font_family_value(font_family_value)
            
            for font_family in font_families:
                font_name = normalize_font_name(font_family)
                if font_name:
                    font_type = 'system' if is_system_font(font_name) else 'custom'
                    
                    font = Font(
                        name=font_name,
                        type=font_type,
                        selectors=[selector_text]
                    )
                    
                    # Extract additional font properties
                    font_weight = rule.style.getPropertyValue('font-weight')
                    if font_weight:
                        font.weights = [clean_css_value(font_weight)]
                    
                    font_style = rule.style.getPropertyValue('font-style')
                    if font_style:
                        font.styles = [clean_css_value(font_style)]
                    
                    fonts.append(font)
        
        # Check for font shorthand property
        font_value = rule.style.getPropertyValue('font')
        if font_value:
            fonts.extend(self._parse_font_shorthand(font_value, selector_text))
        
        return fonts
    
    def _regex_parse_font_families(self, css_content: str) -> List[Font]:
        """Fallback regex-based parsing for font-family declarations."""
        fonts = []
        
        # Pattern to match font-family declarations
        font_family_pattern = r'font-family\s*:\s*([^;}]+)'
        matches = re.finditer(font_family_pattern, css_content, re.IGNORECASE)
        
        for match in matches:
            font_family_value = match.group(1).strip()
            font_families = self._parse_font_family_value(font_family_value)
            
            for font_family in font_families:
                font_name = normalize_font_name(font_family)
                if font_name:
                    font_type = 'system' if is_system_font(font_name) else 'custom'
                    
                    font = Font(
                        name=font_name,
                        type=font_type
                    )
                    fonts.append(font)
        
        return fonts
    
    def _parse_font_family_value(self, font_family_value: str) -> List[str]:
        """Parse a font-family CSS value to extract individual font names."""
        if not font_family_value:
            return []
        
        # Split by comma, but respect quoted strings
        font_families = []
        current_font = ""
        in_quotes = False
        quote_char = None
        
        for char in font_family_value:
            if char in ['"', "'"] and not in_quotes:
                in_quotes = True
                quote_char = char
            elif char == quote_char and in_quotes:
                in_quotes = False
                quote_char = None
            elif char == ',' and not in_quotes:
                if current_font.strip():
                    font_families.append(current_font.strip())
                current_font = ""
                continue
            
            current_font += char
        
        # Add the last font
        if current_font.strip():
            font_families.append(current_font.strip())
        
        return [normalize_font_name(font) for font in font_families if font.strip()]
    
    def _parse_font_shorthand(self, font_value: str, selector: str) -> List[Font]:
        """Parse the font shorthand property."""
        fonts = []
        
        # The font shorthand is complex, but we can extract the font-family at the end
        # Format: font-style font-variant font-weight font-size/line-height font-family
        
        # Split by whitespace and find the font-family part (after size)
        parts = font_value.split()
        
        # Look for font-family at the end (after potential size/line-height)
        font_family_part = ""
        found_size = False
        
        for i, part in enumerate(parts):
            # If we find something that looks like a size, everything after is font-family
            if re.match(r'\d+(\.\d+)?(px|em|rem|%|pt|pc|in|cm|mm|ex|ch|vw|vh|vmin|vmax)', part):
                found_size = True
                # Join everything after the size as font-family
                if i + 1 < len(parts):
                    font_family_part = ' '.join(parts[i + 1:])
                break
        
        if font_family_part:
            font_families = self._parse_font_family_value(font_family_part)
            for font_family in font_families:
                font_name = normalize_font_name(font_family)
                if font_name:
                    font_type = 'system' if is_system_font(font_name) else 'custom'
                    
                    font = Font(
                        name=font_name,
                        type=font_type,
                        selectors=[selector]
                    )
                    fonts.append(font)
        
        return fonts
    
    def _extract_css_properties(self, css_block: str) -> Dict[str, str]:
        """Extract CSS properties from a CSS block."""
        properties = {}
        
        # Split by semicolon and parse each property
        declarations = css_block.split(';')
        
        for declaration in declarations:
            if ':' in declaration:
                key, value = declaration.split(':', 1)
                key = key.strip().lower()
                value = clean_css_value(value)
                if key and value:
                    properties[key] = value
        
        return properties
    
    def _extract_css_imports(self, css_content: str) -> List[str]:
        """Extract @import statements from CSS."""
        imports = []
        
        # Pattern to match @import statements
        import_pattern = r'@import\s+(?:url\()?["\']?([^"\';\)]+)["\']?\)?[^;]*;'
        matches = re.finditer(import_pattern, css_content, re.IGNORECASE)
        
        for match in matches:
            import_url = match.group(1).strip()
            if self.base_url:
                import_url = urljoin(self.base_url, import_url)
            imports.append(import_url)
        
        return imports
    
    def get_css_imports(self) -> List[str]:
        """Get all CSS imports found during parsing."""
        return self.css_imports
    
    def merge_duplicate_fonts(self, fonts: List[Font]) -> List[Font]:
        """Merge fonts with the same name but different properties."""
        font_map = {}
        
        for font in fonts:
            key = (font.name, font.type, font.source)
            
            if key in font_map:
                existing_font = font_map[key]
                
                # Merge weights
                existing_font.weights.extend(font.weights)
                existing_font.weights = list(set(existing_font.weights))
                
                # Merge styles
                existing_font.styles.extend(font.styles)
                existing_font.styles = list(set(existing_font.styles))
                
                # Merge selectors
                existing_font.selectors.extend(font.selectors)
                existing_font.selectors = list(set(existing_font.selectors))
                
                # Update font face data
                existing_font.font_face_data.update(font.font_face_data)
                
            else:
                font_map[key] = font
        
        return list(font_map.values())