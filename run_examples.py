#!/usr/bin/env python3
"""
Example usage of the Enhanced Font Scraper
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.enhanced_main import perform_comprehensive_analysis


async def run_examples():
    """Run example analyses."""
    
    # Example websites to analyze
    example_sites = [
        "https://fonts.google.com",
        "https://github.com", 
        "https://stackoverflow.com"
    ]
    
    print("🔍 Running example font analyses...")
    print("This will create comprehensive reports with screenshots for each site.")
    print(f"Analyzing {len(example_sites)} websites...")
    
    for i, url in enumerate(example_sites, 1):
        print(f"
[{i}/{len(example_sites)}] Analyzing {url}...")
        
        options = {
            'output_dir': f"examples/analysis_{i}",
            'screenshots': True,
            'generate_report': True,
            'timeout': 30,
            'delay': 1.0,
            'include_system': True,
            'no_external': False,
            'headless': True
        }
        
        try:
            results = await perform_comprehensive_analysis(url, options)
            if 'report_path' in results:
                print(f"✅ Report generated: {results['report_path']}")
            else:
                print(f"⚠️  Analysis completed with issues")
        except Exception as e:
            print(f"❌ Error analyzing {url}: {e}")
    
    print("
🎉 Example analyses complete!")
    print("Check the 'examples' directory for generated reports.")


if __name__ == "__main__":
    try:
        asyncio.run(run_examples())
    except KeyboardInterrupt:
        print("
❌ Examples cancelled by user")
    except Exception as e:
        print(f"❌ Error running examples: {e}")
