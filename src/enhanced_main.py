#!/usr/bin/env python3
"""
Enhanced Font Scraper - Advanced command-line tool for comprehensive font analysis with screenshots and reporting.
"""

import sys
import os
import asyncio
import tempfile
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional
import click
from tqdm import tqdm

# Add src directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.font_detector import FontDetector
from src.output_formatter import OutputFormatter
from src.utils import validate_url
from src.screenshot_capture import ScreenshotCapture
from src.report_generator import ReportGenerator

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('font_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def setup_output_directory(url: str, base_dir: str = None) -> Path:
    """Create organized output directory for results."""
    if base_dir is None:
        base_dir = "font_analysis_results"
    
    # Create safe directory name from URL
    safe_url = url.replace('://', '_').replace('/', '_').replace('?', '_').replace('&', '_')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    output_dir = Path(base_dir) / f"{safe_url}_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    return output_dir


async def perform_comprehensive_analysis(url: str, options: dict) -> dict:
    """Perform comprehensive font analysis with screenshots and enhanced reporting."""
    
    # Set up output directory
    output_dir = setup_output_directory(url, options.get('output_dir'))
    screenshots_dir = output_dir / 'screenshots'
    screenshots_dir.mkdir(exist_ok=True)
    
    logger.info(f"Starting comprehensive analysis of {url}")
    logger.info(f"Output directory: {output_dir}")
    
    results = {}
    
    # Initialize components
    detector = FontDetector(
        timeout=options.get('timeout', 30),
        user_agent=options.get('user_agent'),
        delay=options.get('delay', 1.0),
        include_system=options.get('include_system', True),
        skip_external=options.get('no_external', False)
    )
    
    screenshot_capture = None
    
    try:
        # Step 1: Font Detection
        with tqdm(desc="Analyzing fonts", total=3) as pbar:
            pbar.set_description("Detecting fonts...")
            font_results = detector.analyze_website(url)
            pbar.update(1)
            
            # Step 2: Screenshot Capture
            if options.get('screenshots', True):
                pbar.set_description("Capturing screenshots...")
                screenshot_capture = ScreenshotCapture(
                    headless=options.get('headless', True),
                    timeout=options.get('timeout', 30) * 1000
                )
                
                await screenshot_capture.initialize()
                
                # Capture website screenshots
                screenshots = await screenshot_capture.capture_website_screenshots(
                    url, str(screenshots_dir)
                )
                
                # Capture font samples
                font_samples = await screenshot_capture.capture_font_samples(
                    font_results.fonts, str(screenshots_dir)
                )
                
                # Analyze font usage
                font_usage_analysis = await screenshot_capture.analyze_font_usage(url)
                
                pbar.update(1)
            else:
                screenshots = {}
                font_samples = {}
                font_usage_analysis = {}
            
            # Step 3: Generate Report
            if options.get('generate_report', True):
                pbar.set_description("Generating comprehensive report...")
                report_generator = ReportGenerator(str(output_dir))
                
                report_path = report_generator.generate_report(
                    font_results,
                    screenshots,
                    font_samples,
                    font_usage_analysis
                )
                
                pbar.update(1)
                
                results['report_path'] = report_path
            
            results.update({
                'font_results': font_results,
                'screenshots': screenshots,
                'font_samples': font_samples,
                'font_usage_analysis': font_usage_analysis,
                'output_dir': str(output_dir)
            })
            
    except Exception as e:
        logger.error(f"Error during analysis: {e}")
        results['error'] = str(e)
    
    finally:
        # Clean up
        detector.close()
        if screenshot_capture:
            await screenshot_capture.close()
    
    return results


@click.command()
@click.argument('url', required=True)
@click.option('--output-dir', '-d',
              type=click.Path(),
              help='Output directory for results (default: auto-generated)')
@click.option('--format', '-f',
              type=click.Choice(['text', 'json', 'csv', 'html'], case_sensitive=False),
              default='html',
              help='Output format (default: html)')
@click.option('--no-screenshots',
              is_flag=True,
              help='Skip screenshot capture (faster but less comprehensive)')
@click.option('--no-report',
              is_flag=True,
              help='Skip HTML report generation')
@click.option('--verbose', '-v',
              is_flag=True,
              help='Show detailed information and progress')
@click.option('--timeout', '-t',
              type=int,
              default=30,
              help='Request timeout in seconds (default: 30)')
@click.option('--user-agent', '-u',
              type=str,
              help='Custom user agent string')
@click.option('--no-external',
              is_flag=True,
              help='Skip external CSS files')
@click.option('--include-system',
              is_flag=True,
              default=True,
              help='Include system font fallbacks (default: true)')
@click.option('--delay',
              type=float,
              default=1.0,
              help='Delay between requests in seconds (default: 1.0)')
@click.option('--headless/--no-headless',
              default=True,
              help='Run browser in headless mode (default: true)')
@click.option('--filter-type',
              type=click.Choice(['web', 'system', 'custom'], case_sensitive=False),
              help='Filter results by font type')
def main(url: str, output_dir: Optional[str], format: str, no_screenshots: bool,
         no_report: bool, verbose: bool, timeout: int, user_agent: Optional[str],
         no_external: bool, include_system: bool, delay: float, headless: bool,
         filter_type: Optional[str]):
    """
    Enhanced Font Scraper - Comprehensive font analysis with screenshots and reporting.
    
    URL: The website URL to analyze (required)
    
    This enhanced version provides:
    - Comprehensive font detection
    - Website and font sample screenshots
    - Beautiful HTML reports with visual analysis
    - Performance recommendations
    - Detailed font categorization
    
    Examples:
    
        # Basic comprehensive analysis
        enhanced-font-scraper https://example.com
        
        # Quick analysis without screenshots
        enhanced-font-scraper https://example.com --no-screenshots
        
        # Custom output directory
        enhanced-font-scraper https://example.com -d ./my-analysis
        
        # Text output only (legacy mode)
        enhanced-font-scraper https://example.com --format text --no-report
    """
    
    # Configure logging level
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Validate URL
    if not validate_url(url):
        click.echo(click.style(f"Error: Invalid URL '{url}'", fg='red'), err=True)
        sys.exit(1)
    
    # Normalize URL
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
        if verbose:
            click.echo(f"Normalized URL to: {url}")
    
    # Prepare options
    options = {
        'output_dir': output_dir,
        'timeout': timeout,
        'user_agent': user_agent,
        'delay': delay,
        'include_system': include_system,
        'no_external': no_external,
        'headless': headless,
        'screenshots': not no_screenshots,
        'generate_report': not no_report and format == 'html',
        'verbose': verbose
    }
    
    try:
        click.echo(click.style(f"🔍 Analyzing {url}...", fg='cyan', bold=True))
        
        if verbose:
            click.echo(f"Settings:")
            click.echo(f"  - Timeout: {timeout}s")
            click.echo(f"  - Delay: {delay}s")
            click.echo(f"  - Screenshots: {'Yes' if options['screenshots'] else 'No'}")
            click.echo(f"  - HTML Report: {'Yes' if options['generate_report'] else 'No'}")
            click.echo(f"  - Format: {format}")
        
        # Run comprehensive analysis
        results = asyncio.run(perform_comprehensive_analysis(url, options))
        
        if 'error' in results:
            click.echo(click.style(f"❌ Analysis failed: {results['error']}", fg='red'), err=True)
            sys.exit(1)
        
        font_results = results['font_results']
        
        # Filter results if requested
        if filter_type:
            original_count = len(font_results.fonts)
            font_results.fonts = [font for font in font_results.fonts if font.type == filter_type.lower()]
            font_results.update_statistics()
            
            if verbose:
                click.echo(f"Filtered {original_count} fonts to {len(font_results.fonts)} {filter_type} fonts")
        
        # Handle different output formats
        if format.lower() != 'html' or no_report:
            # Legacy text/json/csv output
            formatter = OutputFormatter(use_colors=True)
            
            if format.lower() == 'json':
                formatted_output = formatter.format_json_output(font_results, pretty=True)
            elif format.lower() == 'csv':
                formatted_output = formatter.format_csv_output(font_results)
            else:  # text
                formatted_output = formatter.format_text_output(font_results, verbose=verbose)
            
            # Save to file in output directory
            if 'output_dir' in results:
                output_file = Path(results['output_dir']) / f'results.{format.lower()}'
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(formatted_output)
                click.echo(f"Results saved to {output_file}")
            
            # Also display to console
            click.echo(formatted_output)
        
        # Show summary
        stats = font_results.statistics
        click.echo(click.style("\n📊 Analysis Summary:", fg='green', bold=True))
        click.echo(f"  Total fonts found: {stats.get('total_fonts', 0)}")
        click.echo(f"  Web fonts: {stats.get('web_fonts', 0)}")
        click.echo(f"  System fonts: {stats.get('system_fonts', 0)}")
        
        if 'screenshots' in results and results['screenshots']:
            click.echo(f"  Screenshots captured: {len(results['screenshots'])}")
        
        if 'report_path' in results:
            click.echo(click.style(f"\n🎉 Comprehensive report generated!", fg='green', bold=True))
            click.echo(f"📄 Report: {results['report_path']}")
            click.echo(f"📁 All files: {results['output_dir']}")
            
            # Try to open the report in browser
            try:
                import webbrowser
                webbrowser.open(f"file://{Path(results['report_path']).absolute()}")
                click.echo("🌐 Report opened in your default browser")
            except:
                click.echo("💡 Open the report file in your browser to view the analysis")
        
        # Performance warnings
        if stats.get('web_fonts', 0) > 5:
            click.echo(click.style(f"⚠️  High number of web fonts ({stats['web_fonts']}) may impact performance", fg='yellow'))
        
        if font_results.errors:
            click.echo(click.style(f"⚠️  {len(font_results.errors)} errors occurred during analysis", fg='yellow'))
            if verbose:
                for error in font_results.errors:
                    click.echo(f"    - {error}")
    
    except KeyboardInterrupt:
        click.echo(click.style("\n❌ Operation cancelled by user", fg='yellow'))
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        click.echo(click.style(f"❌ Unexpected error: {str(e)}", fg='red'), err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


@click.group()
def cli():
    """Enhanced Font Scraper - Advanced font analysis with visual reporting."""
    pass


@cli.command()
@click.argument('urls', nargs=-1, required=True)
@click.option('--output-dir', '-d', type=click.Path(), help='Base directory for batch results')
@click.option('--no-screenshots', is_flag=True, help='Skip screenshots for faster processing')
@click.option('--concurrent', '-c', type=int, default=3, help='Number of concurrent analyses (default: 3)')
def batch(urls: tuple, output_dir: Optional[str], no_screenshots: bool, concurrent: int):
    """Analyze multiple websites in batch with comprehensive reporting."""
    
    async def analyze_batch():
        base_dir = output_dir or "batch_font_analysis"
        semaphore = asyncio.Semaphore(concurrent)
        
        async def analyze_single(url: str):
            async with semaphore:
                options = {
                    'output_dir': f"{base_dir}/{url.replace('://', '_').replace('/', '_')}",
                    'screenshots': not no_screenshots,
                    'generate_report': True,
                    'timeout': 30,
                    'delay': 1.0,
                    'include_system': True,
                    'no_external': False,
                    'headless': True
                }
                
                click.echo(f"🔍 Analyzing {url}...")
                try:
                    results = await perform_comprehensive_analysis(url, options)
                    if 'report_path' in results:
                        click.echo(f"✅ {url} - Report: {results['report_path']}")
                    else:
                        click.echo(f"⚠️  {url} - Analysis completed with issues")
                except Exception as e:
                    click.echo(f"❌ {url} - Error: {e}")
        
        click.echo(f"🚀 Starting batch analysis of {len(urls)} websites...")
        click.echo(f"📁 Results will be saved to: {base_dir}")
        
        await asyncio.gather(*[analyze_single(url) for url in urls])
        
        click.echo(f"🎉 Batch analysis complete! Check {base_dir} for results.")
    
    try:
        asyncio.run(analyze_batch())
    except KeyboardInterrupt:
        click.echo(click.style("\n❌ Batch analysis cancelled", fg='yellow'))


@cli.command()
def install_browser():
    """Install Playwright browser for screenshot functionality."""
    click.echo("Installing Playwright browser dependencies...")
    try:
        import subprocess
        result = subprocess.run([sys.executable, '-m', 'playwright', 'install', 'chromium'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            click.echo(click.style("✅ Browser installation complete!", fg='green'))
        else:
            click.echo(click.style(f"❌ Installation failed: {result.stderr}", fg='red'))
    except Exception as e:
        click.echo(click.style(f"❌ Installation error: {e}", fg='red'))


@cli.command()
def version():
    """Show version information."""
    click.echo("Enhanced Font Scraper v2.0.0")
    click.echo("Features: Font detection, Screenshot capture, Visual reporting")


if __name__ == '__main__':
    main()