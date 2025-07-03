"""Tests for the CSS parser functionality."""

import unittest
import sys
import os

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from css_parser import CSSParser
from utils import Font


class TestCSSParser(unittest.TestCase):
    """Test cases for CSSParser class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parser = CSSParser(base_url='https://example.com')
    
    def test_parse_font_face_declaration(self):
        """Test parsing of @font-face declarations."""
        css_content = '''
        @font-face {
            font-family: 'CustomFont';
            src: url('custom-font.woff2') format('woff2'),
                 url('custom-font.woff') format('woff');
            font-weight: 400;
            font-style: normal;
        }
        '''
        
        fonts = self.parser._parse_font_face_declarations(css_content)
        
        self.assertEqual(len(fonts), 1)
        font = fonts[0]
        self.assertEqual(font.name, 'CustomFont')
        self.assertEqual(font.type, 'web')
        self.assertIn('woff2', font.source)
    
    def test_parse_font_family_declarations(self):
        """Test parsing of font-family declarations."""
        css_content = '''
        body {
            font-family: 'Roboto', Arial, sans-serif;
            font-weight: 400;
        }
        
        .header {
            font-family: "Georgia", serif;
            font-style: italic;
        }
        '''
        
        fonts = self.parser._parse_font_family_declarations(css_content)
        
        font_names = [font.name for font in fonts]
        self.assertIn('Roboto', font_names)
        self.assertIn('Arial', font_names)
        self.assertIn('Georgia', font_names)
    
    def test_parse_font_family_value(self):
        """Test parsing of font-family property values."""
        test_cases = [
            ('Arial, sans-serif', ['Arial', 'sans-serif']),
            ('"Times New Roman", Times, serif', ['Times New Roman', 'Times', 'serif']),
            ("'Courier New', Courier, monospace", ['Courier New', 'Courier', 'monospace']),
        ]
        
        for input_value, expected in test_cases:
            with self.subTest(input_value=input_value):
                result = self.parser._parse_font_family_value(input_value)
                self.assertEqual(result, expected)
    
    def test_extract_css_properties(self):
        """Test extraction of CSS properties from blocks."""
        css_block = '''
            font-family: 'Roboto';
            font-weight: 700;
            font-style: italic;
            src: url('font.woff') format('woff');
        '''
        
        properties = self.parser._extract_css_properties(css_block)
        
        self.assertEqual(properties['font-family'], 'Roboto')
        self.assertEqual(properties['font-weight'], '700')
        self.assertEqual(properties['font-style'], 'italic')
        self.assertIn('font.woff', properties['src'])
    
    def test_merge_duplicate_fonts(self):
        """Test merging of duplicate fonts."""
        fonts = [
            Font(name='Arial', type='system', weights=['400'], selectors=['.body']),
            Font(name='Arial', type='system', weights=['700'], selectors=['.header']),
            Font(name='Roboto', type='web', weights=['300'], selectors=['.nav'])
        ]
        
        merged = self.parser.merge_duplicate_fonts(fonts)
        
        self.assertEqual(len(merged), 2)
        
        arial_font = next(f for f in merged if f.name == 'Arial')
        self.assertIn('400', arial_font.weights)
        self.assertIn('700', arial_font.weights)
        self.assertIn('.body', arial_font.selectors)
        self.assertIn('.header', arial_font.selectors)


if __name__ == '__main__':
    unittest.main()