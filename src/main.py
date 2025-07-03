#!/usr/bin/env python3
"""
Font Scraper - Command-line tool for analyzing fonts used on websites.
"""

import sys
import os
import click
from typing import Optional

# Add src directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.font_detector import FontDetector
from src.output_formatter import OutputFormatter
from src.utils import validate_url


@click.command()
@click.argument('url', required=True)
@click.option('--output', '-o', 
              type=click.Choice(['text', 'json', 'csv'], case_sensitive=False),
              default='text',
              help='Output format (default: text)')
@click.option('--save', '-s',
              type=click.Path(),
              help='Save results to file')
@click.option('--verbose', '-v',
              is_flag=True,
              help='Show detailed information including sources and selectors')
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
@click.option('--no-colors',
              is_flag=True,
              help='Disable colored output')
@click.option('--delay',
              type=float,
              default=1.0,
              help='Delay between requests in seconds (default: 1.0)')
@click.option('--filter', '-f',
              type=click.Choice(['web', 'system', 'custom'], case_sensitive=False),
              help='Filter results by font type')
def main(url: str, output: str, save: Optional[str], verbose: bool, timeout: int,
         user_agent: Optional[str], no_external: bool, include_system: bool,
         no_colors: bool, delay: float, filter: Optional[str]):
    """
    Analyze fonts used on a website.
    
    URL: The website URL to analyze (required)
    
    Examples:
    
        font-scraper https://example.com
        
        font-scraper https://example.com --output json --save results.json
        
        font-scraper https://example.com --verbose --filter web
    """
    
    # Validate URL
    if not validate_url(url):
        click.echo(click.style(f"Error: Invalid URL '{url}'", fg='red'), err=True)
        sys.exit(1)
    
    # Normalize URL (add https:// if no scheme)
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
        click.echo(f"Normalized URL to: {url}")
    
    # Initialize components
    detector = FontDetector(
        timeout=timeout,
        user_agent=user_agent,
        delay=delay,
        include_system=include_system,
        skip_external=no_external
    )
    
    formatter = OutputFormatter(use_colors=not no_colors)
    
    try:
        # Show progress
        click.echo(f"Analyzing fonts on {url}...")
        if verbose:
            click.echo(f"Settings: timeout={timeout}s, delay={delay}s, include_system={include_system}")
        
        # Perform analysis
        results = detector.analyze_website(url)
        
        # Check for critical errors
        if not results.fonts and results.errors:
            click.echo(click.style("Analysis failed with errors:", fg='red'), err=True)
            for error in results.errors:
                click.echo(click.style(f"  - {error}", fg='red'), err=True)
            sys.exit(1)
        
        # Filter results if requested
        if filter:
            original_count = len(results.fonts)
            results.fonts = [font for font in results.fonts if font.type == filter.lower()]
            results.update_statistics()
            
            if verbose:
                click.echo(f"Filtered {original_count} fonts to {len(results.fonts)} {filter} fonts")
        
        # Format output
        if output.lower() == 'json':
            formatted_output = formatter.format_json_output(results, pretty=True)
        elif output.lower() == 'csv':
            formatted_output = formatter.format_csv_output(results)
        else:  # text
            formatted_output = formatter.format_text_output(results, verbose=verbose)
        
        # Save to file if requested
        if save:
            success = formatter.save_to_file(formatted_output, save)
            if success:
                click.echo(f"Results saved to {save}")
            else:
                click.echo(click.style(f"Failed to save results to {save}", fg='red'), err=True)
                sys.exit(1)
        
        # Output results
        click.echo(formatted_output)
        
        # Show summary
        if not save and not verbose and output.lower() == 'text':
            stats = results.statistics
            if stats.get('total_fonts', 0) > 0:
                click.echo(click.style(f"\n✓ Found {stats['total_fonts']} fonts", fg='green'))
            else:
                click.echo(click.style("\n⚠ No fonts found", fg='yellow'))
        
    except KeyboardInterrupt:
        click.echo(click.style("\nOperation cancelled by user", fg='yellow'))
        sys.exit(1)
    except Exception as e:
        click.echo(click.style(f"Unexpected error: {str(e)}", fg='red'), err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)
    finally:
        # Clean up
        detector.close()


@click.group()
def cli():
    """Font Scraper - Analyze fonts used on websites."""
    pass


@cli.command()
@click.argument('url', required=True)
@click.option('--output', '-o', default='text', help='Output format')
def analyze(url: str, output: str):
    """Analyze fonts on a website (same as main command)."""
    main.callback(url, output, None, False, 30, None, False, True, False, 1.0, None)


@cli.command()
@click.argument('urls', nargs=-1, required=True)
@click.option('--output', '-o', default='text', help='Output format')
@click.option('--save-dir', type=click.Path(exists=True), help='Directory to save results')
def batch(urls: tuple, output: str, save_dir: Optional[str]):
    """Analyze multiple websites in batch."""
    detector = FontDetector()
    formatter = OutputFormatter()
    
    for i, url in enumerate(urls, 1):
        click.echo(f"Analyzing {i}/{len(urls)}: {url}")
        
        try:
            results = detector.analyze_website(url)
            
            if output.lower() == 'json':
                formatted_output = formatter.format_json_output(results)
            elif output.lower() == 'csv':
                formatted_output = formatter.format_csv_output(results)
            else:
                formatted_output = formatter.format_text_output(results)
            
            if save_dir:
                # Create filename from URL
                safe_filename = url.replace('://', '_').replace('/', '_').replace('?', '_')
                extension = {'json': '.json', 'csv': '.csv', 'text': '.txt'}[output.lower()]
                filename = os.path.join(save_dir, f"{safe_filename}{extension}")
                formatter.save_to_file(formatted_output, filename)
                click.echo(f"Saved to {filename}")
            else:
                click.echo(formatted_output)
                click.echo("-" * 50)
        
        except Exception as e:
            click.echo(click.style(f"Error analyzing {url}: {e}", fg='red'))
    
    detector.close()


@cli.command()
def version():
    """Show version information."""
    from . import __version__
    click.echo(f"Font Scraper v{__version__}")


if __name__ == '__main__':
    main()