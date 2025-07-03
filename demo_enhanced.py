#!/usr/bin/env python3
"""
Demo of Enhanced Font Scraper capabilities
"""

import sys
import os
import json
import tempfile
from datetime import datetime
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Try importing with fallbacks
try:
    from src.font_detector import FontDetector
    from src.output_formatter import OutputFormatter
    from src.utils import validate_url
except ImportError:
    print("❌ Error: Cannot import font scraper modules")
    print("Please ensure you're running from the correct directory")
    sys.exit(1)

def create_demo_report():
    """Create a demo HTML report showing enhanced capabilities."""
    
    # Sample font data for demonstration
    sample_fonts = [
        {
            "name": "Roboto",
            "type": "web",
            "provider": "Google Fonts",
            "weights": ["300", "400", "700"],
            "styles": ["normal", "italic"],
            "format": "woff2",
            "source": "https://fonts.googleapis.com/css2?family=Roboto"
        },
        {
            "name": "Arial",
            "type": "system",
            "provider": None,
            "weights": ["400"],
            "styles": ["normal"],
            "format": None,
            "source": None
        },
        {
            "name": "Open Sans",
            "type": "web", 
            "provider": "Google Fonts",
            "weights": ["400", "600"],
            "styles": ["normal"],
            "format": "woff2",
            "source": "https://fonts.googleapis.com/css2?family=Open+Sans"
        }
    ]
    
    # Create sample report HTML
    report_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enhanced Font Scraper Demo Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 0;
            background: #f5f5f5;
            color: #333;
            line-height: 1.6;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            text-align: center;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }}
        .card {{
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 1.5rem;
            margin: 2rem 0;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
            margin: 2rem 0;
        }}
        .stat-card {{
            text-align: center;
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 4px;
            border: 1px solid #e9ecef;
        }}
        .stat-number {{
            font-size: 2rem;
            font-weight: bold;
            color: #667eea;
            display: block;
        }}
        .font-item {{
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            padding: 1rem;
            margin: 0.5rem 0;
            background: #fafafa;
        }}
        .font-name {{
            font-weight: bold;
            color: #333;
            margin-bottom: 0.5rem;
            font-size: 1.1rem;
        }}
        .font-details {{
            font-size: 0.9rem;
            color: #666;
            line-height: 1.4;
        }}
        .feature-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin: 2rem 0;
        }}
        .feature {{
            background: #e8f2ff;
            padding: 1.5rem;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        .feature h3 {{
            margin-top: 0;
            color: #667eea;
        }}
        .demo-note {{
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            padding: 1rem;
            border-radius: 4px;
            margin: 2rem 0;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎨 Enhanced Font Scraper 2.0</h1>
        <p>Demonstration Report</p>
        <p>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
    </div>
    
    <div class="container">
        <div class="demo-note">
            <strong>🚀 Demo Report:</strong> This demonstrates the enhanced capabilities of Font Scraper 2.0. 
            In a real analysis, this would contain actual website screenshots, font samples, and comprehensive data.
        </div>
        
        <!-- Enhanced Features -->
        <div class="card">
            <h2>🆕 Enhanced Features in 2.0</h2>
            <div class="feature-grid">
                <div class="feature">
                    <h3>📸 Screenshot Capture</h3>
                    <p>Automatically captures website screenshots and visual font samples using browser automation.</p>
                </div>
                <div class="feature">
                    <h3>📊 Visual Reports</h3>
                    <p>Beautiful, interactive HTML reports with tabbed navigation and responsive design.</p>
                </div>
                <div class="feature">
                    <h3>⚡ Performance Analysis</h3>
                    <p>Detailed metrics on font loading impact with optimization recommendations.</p>
                </div>
                <div class="feature">
                    <h3>🔄 Batch Processing</h3>
                    <p>Analyze multiple websites concurrently with organized output structure.</p>
                </div>
                <div class="feature">
                    <h3>🛡️ Robust Error Handling</h3>
                    <p>Retry logic, graceful error recovery, and comprehensive logging.</p>
                </div>
                <div class="feature">
                    <h3>🎯 Enhanced Detection</h3>
                    <p>Improved font detection accuracy with better provider analysis.</p>
                </div>
            </div>
        </div>
        
        <!-- Sample Statistics -->
        <div class="card">
            <h2>📊 Sample Analysis Statistics</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <span class="stat-number">{len(sample_fonts)}</span>
                    <div>Total Fonts</div>
                </div>
                <div class="stat-card">
                    <span class="stat-number">{len([f for f in sample_fonts if f['type'] == 'web'])}</span>
                    <div>Web Fonts</div>
                </div>
                <div class="stat-card">
                    <span class="stat-number">{len([f for f in sample_fonts if f['type'] == 'system'])}</span>
                    <div>System Fonts</div>
                </div>
                <div class="stat-card">
                    <span class="stat-number">{len(set(f['provider'] for f in sample_fonts if f['provider']))}</span>
                    <div>Font Providers</div>
                </div>
            </div>
        </div>
        
        <!-- Sample Fonts -->
        <div class="card">
            <h2>🔤 Sample Font Detection</h2>
            {[f'''
            <div class="font-item">
                <div class="font-name">{font["name"]}</div>
                <div class="font-details">
                    <strong>Type:</strong> {font["type"].title()}<br>
                    {f'<strong>Provider:</strong> {font["provider"]}<br>' if font["provider"] else ''}
                    <strong>Weights:</strong> {", ".join(font["weights"])}<br>
                    <strong>Styles:</strong> {", ".join(font["styles"])}<br>
                    {f'<strong>Format:</strong> {font["format"]}<br>' if font["format"] else ''}
                    {f'<strong>Source:</strong> <a href="{font["source"]}" target="_blank">{font["source"][:60]}...</a>' if font["source"] else ''}
                </div>
            </div>
            ''' for font in sample_fonts]}
        </div>
        
        <!-- Installation & Usage -->
        <div class="card">
            <h2>🚀 Getting Started</h2>
            <h3>Installation</h3>
            <pre style="background: #f8f9fa; padding: 1rem; border-radius: 4px; overflow-x: auto;"><code># Install dependencies
python3 setup_enhanced.py

# Basic usage
./enhanced-font-scraper https://example.com

# With custom options
./enhanced-font-scraper https://example.com --no-screenshots --format json

# Batch processing
enhanced-font-scraper batch https://site1.com https://site2.com</code></pre>
            
            <h3>Key Improvements</h3>
            <ul>
                <li><strong>Visual Analysis:</strong> Screenshot capture and font sample generation</li>
                <li><strong>Enhanced Reporting:</strong> Interactive HTML reports with performance insights</li>
                <li><strong>Better Reliability:</strong> Robust error handling and retry mechanisms</li>
                <li><strong>Batch Processing:</strong> Analyze multiple sites efficiently</li>
                <li><strong>Performance Monitoring:</strong> Track analysis metrics and resource usage</li>
            </ul>
        </div>
        
        <!-- Technical Details -->
        <div class="card">
            <h2>🔧 Technical Enhancements</h2>
            <div class="font-details">
                <strong>New Dependencies:</strong><br>
                • Playwright (browser automation)<br>
                • Pillow (image processing)<br>
                • Jinja2 (HTML templating)<br>
                • tqdm (progress bars)<br>
                • psutil (performance monitoring)<br><br>
                
                <strong>Architecture Improvements:</strong><br>
                • Modular screenshot capture system<br>
                • Comprehensive report generation<br>
                • Enhanced error handling utilities<br>
                • Performance monitoring framework<br>
                • Robust HTTP session management
            </div>
        </div>
    </div>
</body>
</html>
    """
    
    # Create output directory
    output_dir = Path("demo_output")
    output_dir.mkdir(exist_ok=True)
    
    # Save demo report
    report_path = output_dir / "enhanced_demo_report.html"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_html)
    
    return str(report_path)

def test_basic_functionality():
    """Test basic font detection functionality."""
    
    print("🔍 Testing basic font detection...")
    
    try:
        # Test URL validation
        test_url = "https://example.com"
        if validate_url(test_url):
            print("✅ URL validation working")
        else:
            print("❌ URL validation failed")
            return False
        
        # Test FontDetector initialization
        detector = FontDetector(timeout=10, include_system=True)
        print("✅ FontDetector initialization working")
        
        # Test OutputFormatter
        formatter = OutputFormatter(use_colors=True)
        print("✅ OutputFormatter initialization working")
        
        detector.close()
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

def main():
    """Main demo function."""
    print("🎨 Enhanced Font Scraper 2.0 - Demo")
    print("=" * 50)
    
    # Test basic functionality
    if test_basic_functionality():
        print("✅ Core functionality is working")
    else:
        print("⚠️  Some issues with core functionality")
    
    # Create demo report
    print("\n📊 Creating demonstration report...")
    try:
        report_path = create_demo_report()
        print(f"✅ Demo report created: {report_path}")
        
        # Try to open in browser
        try:
            import webbrowser
            full_path = Path(report_path).absolute()
            webbrowser.open(f"file://{full_path}")
            print("🌐 Demo report opened in browser")
        except:
            print("💡 Open the demo report file in your browser to view")
            
    except Exception as e:
        print(f"❌ Failed to create demo report: {e}")
    
    print("\n🎉 Demo complete!")
    print("\nThe enhanced version provides:")
    print("  • 📸 Automated screenshot capture")
    print("  • 📊 Interactive HTML reports")
    print("  • ⚡ Performance analysis")
    print("  • 🔄 Batch processing")
    print("  • 🛡️ Robust error handling")
    print("  • 🎯 Enhanced font detection")
    
    print(f"\nTo use the full enhanced version:")
    print(f"  1. Ensure all dependencies are installed")
    print(f"  2. Run: python3 setup_enhanced.py")
    print(f"  3. Use: ./enhanced-font-scraper https://example.com")

if __name__ == "__main__":
    main()