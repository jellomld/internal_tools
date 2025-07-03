#!/usr/bin/env python3
"""
Setup script for Enhanced Font Scraper with all dependencies including browser automation.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def run_command(cmd, description=""):
    """Run a command and handle errors gracefully."""
    print(f"{'🔧 ' if description else ''}{description or cmd}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        if result.stdout:
            print(f"✅ {description or 'Command'} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stderr:
            print(f"Details: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True


def install_dependencies():
    """Install Python dependencies."""
    print("\n📦 Installing Python dependencies...")
    
    # First, upgrade pip
    run_command(f"{sys.executable} -m pip install --break-system-packages --upgrade pip", "Upgrading pip")
    
    # Install main dependencies
    dependencies = [
        "requests>=2.28.0",
        "beautifulsoup4>=4.11.0",
        "cssutils>=2.6.0",
        "click>=8.1.0",
        "colorama>=0.4.6",
        "validators>=0.20.0",
        "urllib3>=1.26.0",
        "tinycss2>=1.2.0",
        "lxml>=4.9.0",
        "playwright>=1.40.0",
        "pillow>=10.0.0",
        "jinja2>=3.1.0",
        "tqdm>=4.66.0",
        "psutil>=5.9.0"
    ]
    
    for dep in dependencies:
        if not run_command(f"{sys.executable} -m pip install --break-system-packages {dep}", f"Installing {dep.split('>=')[0]}"):
            print(f"⚠️  Failed to install {dep}")
            return False
    
    return True


def install_playwright_browser():
    """Install Playwright browser components."""
    print("\n🌐 Installing browser components for screenshot capture...")
    
    # Install Playwright browsers
    if not run_command(f"{sys.executable} -m playwright install chromium", "Installing Chromium browser"):
        print("⚠️  Browser installation failed. Screenshots may not work.")
        return False
    
    print("✅ Browser components installed successfully")
    return True


def create_launcher_scripts():
    """Create convenient launcher scripts."""
    print("\n📝 Creating launcher scripts...")
    
    # Create enhanced launcher
    launcher_content = '''#!/usr/bin/env python3
"""Enhanced Font Scraper Launcher"""
import sys
import os

# Add src directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import and run the enhanced main
try:
    from src.enhanced_main import main
    main()
except ImportError as e:
    print(f"Error importing enhanced main: {e}")
    print("Please ensure all dependencies are installed by running setup_enhanced.py")
    sys.exit(1)
'''
    
    with open("enhanced-font-scraper", "w") as f:
        f.write(launcher_content)
    
    # Make executable on Unix-like systems
    if platform.system() != "Windows":
        os.chmod("enhanced-font-scraper", 0o755)
    
    # Create batch file for Windows
    if platform.system() == "Windows":
        bat_content = f'''@echo off
{sys.executable} "%~dp0enhanced-font-scraper" %*
'''
        with open("enhanced-font-scraper.bat", "w") as f:
            f.write(bat_content)
    
    print("✅ Launcher scripts created")
    return True


def create_example_usage():
    """Create example usage script."""
    example_content = '''#!/usr/bin/env python3
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
        print(f"\n[{i}/{len(example_sites)}] Analyzing {url}...")
        
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
    
    print("\n🎉 Example analyses complete!")
    print("Check the 'examples' directory for generated reports.")


if __name__ == "__main__":
    try:
        asyncio.run(run_examples())
    except KeyboardInterrupt:
        print("\n❌ Examples cancelled by user")
    except Exception as e:
        print(f"❌ Error running examples: {e}")
'''
    
    with open("run_examples.py", "w") as f:
        f.write(example_content)
    
    print("✅ Example usage script created")


def verify_installation():
    """Verify that everything is working."""
    print("\n🔍 Verifying installation...")
    
    try:
        # Test imports
        import requests
        import playwright
        import click
        import jinja2
        from PIL import Image
        print("✅ All required modules can be imported")
        
        # Test Playwright
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            browser.close()
        print("✅ Browser automation is working")
        
        return True
    except Exception as e:
        print(f"❌ Installation verification failed: {e}")
        return False


def main():
    """Main setup function."""
    print("🚀 Enhanced Font Scraper Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Install browser
    if not install_playwright_browser():
        print("⚠️  Browser installation issues, but continuing...")
    
    # Create scripts
    create_launcher_scripts()
    create_example_usage()
    
    # Verify installation
    if verify_installation():
        print("\n🎉 Enhanced Font Scraper setup complete!")
        print("\nUsage:")
        print("  ./enhanced-font-scraper https://example.com")
        print("  python enhanced-font-scraper https://example.com")
        print("  python run_examples.py")
        print("\nFeatures:")
        print("  ✅ Comprehensive font detection")
        print("  ✅ Website screenshot capture")
        print("  ✅ Beautiful HTML reports")
        print("  ✅ Font sample generation")
        print("  ✅ Performance analysis")
        print("  ✅ Batch processing")
    else:
        print("\n⚠️  Setup completed with some issues")
        print("Some features may not work correctly")
    
    print(f"\nFiles created:")
    print(f"  - enhanced-font-scraper (main launcher)")
    print(f"  - run_examples.py (usage examples)")
    if platform.system() == "Windows":
        print(f"  - enhanced-font-scraper.bat (Windows launcher)")


if __name__ == "__main__":
    main()