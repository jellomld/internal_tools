"""Output formatting for font scraping results."""

import json
import csv
from datetime import datetime
from typing import List, Dict, Any, TextIO
from io import StringIO
from colorama import init, Fore, Style

from font_scraper.utils import ScrapeResults, Font

# Initialize colorama for cross-platform colored output
init()


class OutputFormatter:
    """Formatter for font scraping results in various formats."""
    
    def __init__(self, use_colors: bool = True):
        self.use_colors = use_colors
    
    def format_text_output(self, results: ScrapeResults, verbose: bool = False) -> str:
        """Format results as human-readable text."""
        output = StringIO()
        
        # Header
        self._write_colored(output, f"Font Analysis Results for {results.url}", Fore.CYAN, style=Style.BRIGHT)
        output.write("\n" + "=" * 50 + "\n\n")
        
        # Summary statistics
        stats = results.statistics
        if stats:
            self._write_colored(output, "Summary:", Fore.GREEN, style=Style.BRIGHT)
            output.write(f"\n- Total fonts found: {stats.get('total_fonts', 0)}\n")
            output.write(f"- Web fonts: {stats.get('web_fonts', 0)}\n")
            output.write(f"- System fonts: {stats.get('system_fonts', 0)}\n")
            output.write(f"- Custom fonts: {stats.get('custom_fonts', 0)}\n")
            output.write(f"- CSS files analyzed: {stats.get('css_files', 0)}\n")
            if stats.get('google_fonts', 0) > 0:
                output.write(f"- Google Fonts: {stats.get('google_fonts', 0)}\n")
            if stats.get('adobe_fonts', 0) > 0:
                output.write(f"- Adobe Fonts: {stats.get('adobe_fonts', 0)}\n")
            output.write("\n")
        
        # Group fonts by type
        font_groups = self._group_fonts_by_type(results.fonts)
        
        # Web fonts
        if font_groups.get('web'):
            self._write_colored(output, f"Web Fonts ({len(font_groups['web'])}):", Fore.BLUE, style=Style.BRIGHT)
            output.write("\n")
            for font in font_groups['web']:
                self._format_font_text(output, font, verbose)
            output.write("\n")
        
        # System fonts
        if font_groups.get('system'):
            self._write_colored(output, f"System Fonts ({len(font_groups['system'])}):", Fore.YELLOW, style=Style.BRIGHT)
            output.write("\n")
            for font in font_groups['system']:
                self._format_font_text(output, font, verbose)
            output.write("\n")
        
        # Custom fonts
        if font_groups.get('custom'):
            self._write_colored(output, f"Custom Fonts ({len(font_groups['custom'])}):", Fore.MAGENTA, style=Style.BRIGHT)
            output.write("\n")
            for font in font_groups['custom']:
                self._format_font_text(output, font, verbose)
            output.write("\n")
        
        # CSS files analyzed
        if results.css_files and verbose:
            self._write_colored(output, "CSS Files Analyzed:", Fore.GREEN, style=Style.BRIGHT)
            output.write("\n")
            for css_file in results.css_files:
                output.write(f"  - {css_file}\n")
            output.write("\n")
        
        # Errors
        if results.errors:
            self._write_colored(output, "Errors:", Fore.RED, style=Style.BRIGHT)
            output.write("\n")
            for error in results.errors:
                self._write_colored(output, f"  ⚠ {error}", Fore.RED)
                output.write("\n")
            output.write("\n")
        
        # Timestamp
        if verbose:
            output.write(f"Analysis completed at: {results.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        return output.getvalue()
    
    def format_json_output(self, results: ScrapeResults, pretty: bool = True) -> str:
        """Format results as JSON."""
        data = {
            "url": results.url,
            "timestamp": results.timestamp.isoformat(),
            "fonts": [self._font_to_dict(font) for font in results.fonts],
            "statistics": results.statistics,
            "css_files": results.css_files,
            "errors": results.errors
        }
        
        if pretty:
            return json.dumps(data, indent=2, ensure_ascii=False)
        else:
            return json.dumps(data, ensure_ascii=False)
    
    def format_csv_output(self, results: ScrapeResults) -> str:
        """Format results as CSV."""
        output = StringIO()
        
        fieldnames = [
            'name', 'type', 'provider', 'source', 'weights', 'styles', 
            'format', 'selectors', 'unicode_range'
        ]
        
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        for font in results.fonts:
            writer.writerow({
                'name': font.name,
                'type': font.type,
                'provider': font.provider or '',
                'source': font.source or '',
                'weights': ';'.join(font.weights) if font.weights else '',
                'styles': ';'.join(font.styles) if font.styles else '',
                'format': font.format or '',
                'selectors': ';'.join(font.selectors) if font.selectors else '',
                'unicode_range': font.unicode_range or ''
            })
        
        return output.getvalue()
    
    def save_to_file(self, content: str, filename: str) -> bool:
        """Save formatted content to a file."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error saving to file {filename}: {e}")
            return False
    
    def _write_colored(self, output: TextIO, text: str, color: str = '', style: str = ''):
        """Write colored text to output if colors are enabled."""
        if self.use_colors:
            output.write(f"{color}{style}{text}{Style.RESET_ALL}")
        else:
            output.write(text)
    
    def _format_font_text(self, output: TextIO, font: Font, verbose: bool = False):
        """Format a single font for text output."""
        # Font name with checkmark
        self._write_colored(output, "  ✓ ", Fore.GREEN)
        self._write_colored(output, font.name, style=Style.BRIGHT)
        
        if font.provider:
            self._write_colored(output, f" ({font.provider})", Fore.CYAN)
        
        output.write("\n")
        
        # Font details
        if font.weights and font.weights != ['400']:
            output.write(f"    - Weights: {', '.join(font.weights)}\n")
        
        if font.styles and font.styles != ['normal']:
            output.write(f"    - Styles: {', '.join(font.styles)}\n")
        
        if font.format:
            output.write(f"    - Format: {font.format}\n")
        
        if font.source and verbose:
            output.write(f"    - Source: {font.source}\n")
        
        if font.selectors and verbose:
            selectors_str = ', '.join(font.selectors[:3])  # Show first 3 selectors
            if len(font.selectors) > 3:
                selectors_str += f" (and {len(font.selectors) - 3} more)"
            output.write(f"    - Used in: {selectors_str}\n")
        
        if font.unicode_range and verbose:
            output.write(f"    - Unicode range: {font.unicode_range}\n")
        
        output.write("\n")
    
    def _group_fonts_by_type(self, fonts: List[Font]) -> Dict[str, List[Font]]:
        """Group fonts by their type."""
        groups = {
            'web': [],
            'system': [],
            'custom': []
        }
        
        for font in fonts:
            if font.type in groups:
                groups[font.type].append(font)
        
        return groups
    
    def _font_to_dict(self, font: Font) -> Dict[str, Any]:
        """Convert a Font object to a dictionary."""
        return {
            "name": font.name,
            "type": font.type,
            "source": font.source,
            "weights": font.weights,
            "styles": font.styles,
            "format": font.format,
            "provider": font.provider,
            "selectors": font.selectors,
            "unicode_range": font.unicode_range,
            "font_face_data": font.font_face_data
        }
    
    def generate_summary(self, results: ScrapeResults) -> Dict[str, Any]:
        """Generate a statistical summary of the results."""
        fonts = results.fonts
        
        # Basic counts
        summary = {
            "total_fonts": len(fonts),
            "web_fonts": len([f for f in fonts if f.type == 'web']),
            "system_fonts": len([f for f in fonts if f.type == 'system']),
            "custom_fonts": len([f for f in fonts if f.type == 'custom']),
            "css_files_analyzed": len(results.css_files),
            "errors_encountered": len(results.errors)
        }
        
        # Provider breakdown
        providers = {}
        for font in fonts:
            if font.provider:
                providers[font.provider] = providers.get(font.provider, 0) + 1
        summary["providers"] = providers
        
        # Format breakdown
        formats = {}
        for font in fonts:
            if font.format:
                formats[font.format] = formats.get(font.format, 0) + 1
        summary["formats"] = formats
        
        # Weight breakdown
        weights = {}
        for font in fonts:
            for weight in font.weights:
                weights[weight] = weights.get(weight, 0) + 1
        summary["weights"] = weights
        
        # Style breakdown
        styles = {}
        for font in fonts:
            for style in font.styles:
                styles[style] = styles.get(style, 0) + 1
        summary["styles"] = styles
        
        return summary
    
    def colorize_output(self, text: str, color: str) -> str:
        """Add color to text output."""
        if not self.use_colors:
            return text
        
        color_map = {
            'red': Fore.RED,
            'green': Fore.GREEN,
            'blue': Fore.BLUE,
            'yellow': Fore.YELLOW,
            'magenta': Fore.MAGENTA,
            'cyan': Fore.CYAN,
            'white': Fore.WHITE
        }
        
        color_code = color_map.get(color.lower(), '')
        return f"{color_code}{text}{Style.RESET_ALL}"