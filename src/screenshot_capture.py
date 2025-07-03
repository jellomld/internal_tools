"""Screenshot capture and visual font analysis functionality."""

import asyncio
import base64
import tempfile
import os
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from datetime import datetime

from playwright.async_api import async_playwright, Browser, Page
from PIL import Image, ImageDraw, ImageFont
import logging

from src.utils import Font, ScrapeResults

logger = logging.getLogger(__name__)


class ScreenshotCapture:
    """Handles screenshot capture and visual font analysis using Playwright."""
    
    def __init__(self, headless: bool = True, timeout: int = 30000):
        self.headless = headless
        self.timeout = timeout
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
    
    async def initialize(self):
        """Initialize the browser and page."""
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=self.headless,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            self.page = await self.browser.new_page()
            await self.page.set_viewport_size({"width": 1920, "height": 1080})
        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")
            raise
    
    async def capture_website_screenshots(self, url: str, output_dir: str) -> Dict[str, str]:
        """Capture multiple screenshots of the website for font analysis."""
        if not self.page:
            await self.initialize()
        
        screenshots = {}
        
        try:
            # Navigate to the page
            await self.page.goto(url, timeout=self.timeout, wait_until='networkidle')
            
            # Full page screenshot
            full_screenshot = os.path.join(output_dir, 'full_page.png')
            await self.page.screenshot(path=full_screenshot, full_page=True)
            screenshots['full_page'] = full_screenshot
            
            # Above the fold screenshot
            viewport_screenshot = os.path.join(output_dir, 'viewport.png')
            await self.page.screenshot(path=viewport_screenshot)
            screenshots['viewport'] = viewport_screenshot
            
            # Font-specific screenshots
            font_elements = await self._find_text_elements()
            for i, element in enumerate(font_elements[:5]):  # Limit to 5 elements
                element_screenshot = os.path.join(output_dir, f'text_element_{i+1}.png')
                await element.screenshot(path=element_screenshot)
                screenshots[f'text_element_{i+1}'] = element_screenshot
            
        except Exception as e:
            logger.error(f"Error capturing screenshots: {e}")
        
        return screenshots
    
    async def _find_text_elements(self) -> List:
        """Find significant text elements on the page for font analysis."""
        try:
            # Common selectors for text elements with different fonts
            selectors = [
                'h1, h2, h3, h4, h5, h6',
                'p:first-of-type',
                '.header, .navbar, .nav',
                '.title, .headline',
                '.content, .body, .text',
                'button, .btn',
                '.menu, .navigation'
            ]
            
            elements = []
            for selector in selectors:
                try:
                    found_elements = await self.page.query_selector_all(selector)
                    elements.extend(found_elements[:2])  # Limit per selector
                except:
                    continue
            
            return elements[:10]  # Maximum 10 elements
        except Exception as e:
            logger.error(f"Error finding text elements: {e}")
            return []
    
    async def capture_font_samples(self, fonts: List[Font], output_dir: str) -> Dict[str, str]:
        """Generate visual samples for detected fonts."""
        samples = {}
        
        try:
            # Create a test page with font samples
            font_sample_html = self._generate_font_sample_html(fonts)
            
            # Create temporary HTML file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
                f.write(font_sample_html)
                temp_html_path = f.name
            
            try:
                await self.page.goto(f'file://{temp_html_path}', timeout=self.timeout)
                
                # Wait for fonts to load
                await asyncio.sleep(2)
                
                # Capture font samples
                font_sample_screenshot = os.path.join(output_dir, 'font_samples.png')
                await self.page.screenshot(path=font_sample_screenshot, full_page=True)
                samples['font_samples'] = font_sample_screenshot
                
                # Capture individual font samples
                for i, font in enumerate(fonts[:10]):  # Limit to 10 fonts
                    try:
                        font_element = await self.page.query_selector(f'#font-{i}')
                        if font_element:
                            individual_sample = os.path.join(output_dir, f'font_{font.name.replace(" ", "_")}.png')
                            await font_element.screenshot(path=individual_sample)
                            samples[f'font_{font.name}'] = individual_sample
                    except:
                        continue
            
            finally:
                # Clean up temp file
                os.unlink(temp_html_path)
        
        except Exception as e:
            logger.error(f"Error capturing font samples: {e}")
        
        return samples
    
    def _generate_font_sample_html(self, fonts: List[Font]) -> str:
        """Generate HTML page for font samples."""
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Font Samples</title>
            <style>
        """
        
        # Add font imports
        for font in fonts:
            if font.source and 'fonts.googleapis.com' in font.source:
                html += f'        @import url("{font.source}");\n'
            elif font.font_face_data:
                # Add @font-face declarations
                html += f'        {font.font_face_data}\n'
        
        html += """
            body {
                margin: 20px;
                background: white;
                line-height: 1.6;
            }
            .font-sample {
                margin: 20px 0;
                padding: 15px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background: #f9f9f9;
            }
            .font-name {
                font-weight: bold;
                color: #333;
                margin-bottom: 10px;
            }
            .sample-text {
                font-size: 24px;
                margin: 10px 0;
            }
            .font-info {
                font-size: 12px;
                color: #666;
                margin-top: 10px;
            }
            </style>
        </head>
        <body>
            <h1>Font Samples</h1>
        """
        
        sample_texts = [
            "The quick brown fox jumps over the lazy dog",
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
            "abcdefghijklmnopqrstuvwxyz",
            "1234567890 !@#$%^&*()"
        ]
        
        for i, font in enumerate(fonts[:10]):
            html += f'<div class="font-sample" id="font-{i}">\n'
            html += f'  <div class="font-name">{font.name}</div>\n'
            
            for text in sample_texts:
                font_family = f'"{font.name}"'
                if font.type == 'system':
                    font_family += ', sans-serif'
                
                html += f'  <div class="sample-text" style="font-family: {font_family};">{text}</div>\n'
            
            html += f'  <div class="font-info">Type: {font.type}'
            if font.provider:
                html += f' | Provider: {font.provider}'
            if font.weights:
                html += f' | Weights: {", ".join(font.weights)}'
            html += '</div>\n'
            html += '</div>\n'
        
        html += """
        </body>
        </html>
        """
        
        return html
    
    async def analyze_font_usage(self, url: str) -> Dict[str, any]:
        """Analyze how fonts are actually used on the page."""
        if not self.page:
            await self.initialize()
        
        analysis = {}
        
        try:
            await self.page.goto(url, timeout=self.timeout, wait_until='networkidle')
            
            # Get computed styles for text elements
            font_usage = await self.page.evaluate("""
                () => {
                    const elements = document.querySelectorAll('h1, h2, h3, h4, h5, h6, p, span, div, a, button');
                    const usage = [];
                    
                    elements.forEach((el, index) => {
                        if (el.offsetWidth > 0 && el.offsetHeight > 0 && el.textContent.trim()) {
                            const style = window.getComputedStyle(el);
                            usage.push({
                                index: index,
                                tagName: el.tagName,
                                textContent: el.textContent.trim().substring(0, 100),
                                fontFamily: style.fontFamily,
                                fontSize: style.fontSize,
                                fontWeight: style.fontWeight,
                                fontStyle: style.fontStyle,
                                color: style.color,
                                selector: el.className ? `.${el.className.split(' ')[0]}` : el.tagName.toLowerCase()
                            });
                        }
                    });
                    
                    return usage.slice(0, 20); // Limit to 20 elements
                }
            """)
            
            analysis['font_usage'] = font_usage
            
        except Exception as e:
            logger.error(f"Error analyzing font usage: {e}")
        
        return analysis
    
    async def close(self):
        """Clean up browser resources."""
        try:
            if self.page:
                await self.page.close()
            if self.browser:
                await self.browser.close()
            if hasattr(self, 'playwright'):
                await self.playwright.stop()
        except Exception as e:
            logger.error(f"Error closing browser: {e}")