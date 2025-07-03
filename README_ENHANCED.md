# Enhanced Font Scraper 2.0

A powerful, comprehensive font analysis tool with visual reporting, screenshot capture, and advanced analytics. This enhanced version provides deep insights into website typography with beautiful, interactive reports.

## 🆕 What's New in 2.0

- **📸 Screenshot Capture**: Automatically captures website screenshots and font samples
- **📊 Visual Reports**: Beautiful HTML reports with interactive analysis
- **🎯 Enhanced Detection**: Improved font detection with better accuracy
- **⚡ Performance Analysis**: Detailed performance metrics and recommendations
- **🔄 Batch Processing**: Analyze multiple websites concurrently
- **🛡️ Robust Error Handling**: Retry logic and graceful error recovery
- **📱 Responsive Design**: Mobile-friendly report layouts

## ✨ Features

### Comprehensive Font Detection
- Web fonts (@font-face declarations)
- Google Fonts, Adobe Fonts, Font Awesome
- System font fallbacks
- Custom font services
- CSS font properties and selectors

### Visual Analysis
- Full-page website screenshots
- Font sample generation with multiple test texts
- Element-specific screenshots
- Visual font comparison

### Advanced Reporting
- Interactive HTML reports with tabbed navigation
- Performance metrics and recommendations
- Font categorization and provider analysis
- Export to JSON, CSV, and text formats

### Performance Insights
- Font loading impact analysis
- Provider performance comparison
- Optimization recommendations
- Resource usage metrics

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/your-repo/enhanced-font-scraper.git
cd enhanced-font-scraper

# Run the enhanced setup
python setup_enhanced.py
```

The setup script will:
- Install all Python dependencies
- Download browser components for screenshots
- Create launcher scripts
- Verify the installation

### 2. Basic Usage

```bash
# Comprehensive analysis with HTML report
./enhanced-font-scraper https://example.com

# Quick analysis without screenshots
./enhanced-font-scraper https://example.com --no-screenshots

# Text output (legacy mode)
./enhanced-font-scraper https://example.com --format text --no-report
```

### 3. View Results

The tool creates organized output directories with:
- `font_analysis_report.html` - Interactive HTML report
- `screenshots/` - Website and font sample images
- `assets/` - Report assets and stylesheets
- `analysis_data.json` - Machine-readable data

## 📖 Detailed Usage

### Command Line Options

```bash
enhanced-font-scraper [OPTIONS] URL

Options:
  -d, --output-dir PATH           Output directory for results
  -f, --format [text|json|csv|html]  Output format (default: html)
  --no-screenshots               Skip screenshot capture
  --no-report                    Skip HTML report generation
  -v, --verbose                  Show detailed information
  -t, --timeout INTEGER          Request timeout in seconds
  -u, --user-agent TEXT          Custom user agent string
  --no-external                  Skip external CSS files
  --include-system               Include system fonts
  --delay FLOAT                  Delay between requests
  --headless / --no-headless     Browser headless mode
  --filter-type [web|system|custom]  Filter by font type
```

### Examples

#### Basic Analysis
```bash
# Full analysis with all features
enhanced-font-scraper https://fonts.google.com

# Results will be in: font_analysis_results/fonts.google.com_20241215_143022/
```

#### Custom Output Directory
```bash
enhanced-font-scraper https://github.com -d ./github-analysis
```

#### Fast Analysis (No Screenshots)
```bash
enhanced-font-scraper https://example.com --no-screenshots --format json
```

#### Batch Analysis
```bash
enhanced-font-scraper batch https://github.com https://stackoverflow.com https://fonts.google.com
```

#### Filter Results
```bash
# Only web fonts
enhanced-font-scraper https://example.com --filter-type web

# Only system fonts
enhanced-font-scraper https://example.com --filter-type system
```

## 📊 Report Features

### Interactive HTML Reports Include:

**Summary Dashboard**
- Total fonts found
- Font type breakdown
- Provider statistics
- Performance metrics

**Screenshots Gallery**
- Full-page website capture
- Above-the-fold view
- Text element samples
- Font sample comparisons

**Detailed Analysis Tabs**
- **Web Fonts**: External fonts with sources and formats
- **System Fonts**: Fallback fonts and usage patterns
- **Providers**: Font service analysis and statistics
- **Performance**: Load time impact and optimization tips

**Technical Details**
- CSS files analyzed
- Error reports
- Analysis duration
- Method documentation

## 🔧 Advanced Configuration

### Browser Settings

```bash
# Use visible browser (for debugging)
enhanced-font-scraper https://example.com --no-headless

# Custom timeout for slow sites
enhanced-font-scraper https://example.com --timeout 60

# Custom delay for rate limiting
enhanced-font-scraper https://example.com --delay 2.0
```

### Output Formats

```bash
# HTML report (default)
enhanced-font-scraper https://example.com

# JSON for programmatic use
enhanced-font-scraper https://example.com --format json

# CSV for spreadsheet analysis
enhanced-font-scraper https://example.com --format csv

# Text for terminal viewing
enhanced-font-scraper https://example.com --format text
```

## 🔄 Batch Processing

Process multiple websites efficiently:

```bash
enhanced-font-scraper batch \
  https://github.com \
  https://stackoverflow.com \
  https://fonts.google.com \
  --output-dir ./batch-results \
  --concurrent 3
```

Features:
- Concurrent processing (configurable)
- Individual reports per site
- Organized output structure
- Progress tracking
- Error isolation

## 🛠️ Development

### Project Structure

```
enhanced-font-scraper/
├── src/
│   ├── enhanced_main.py          # Enhanced CLI interface
│   ├── screenshot_capture.py     # Browser automation
│   ├── report_generator.py       # HTML report generation
│   ├── robust_utils.py          # Enhanced utilities
│   ├── font_detector.py         # Font detection engine
│   ├── css_parser.py            # CSS parsing
│   ├── output_formatter.py      # Legacy formatters
│   └── utils.py                 # Core utilities
├── setup_enhanced.py            # Installation script
├── enhanced-font-scraper        # Main launcher
├── run_examples.py             # Usage examples
└── README_ENHANCED.md          # This file
```

### Dependencies

**Core Libraries:**
- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing
- `cssutils` - CSS parsing
- `click` - CLI interface

**Enhancement Libraries:**
- `playwright` - Browser automation
- `pillow` - Image processing
- `jinja2` - HTML templating
- `tqdm` - Progress bars

**System Requirements:**
- Python 3.8+
- 2GB+ RAM (for browser automation)
- 500MB+ disk space (for browser)

## 🐛 Troubleshooting

### Common Issues

**Browser Installation Failed**
```bash
# Manually install browser
python -m playwright install chromium

# Or run install command
enhanced-font-scraper install-browser
```

**Permission Errors**
```bash
# Make launcher executable (Unix/Linux/Mac)
chmod +x enhanced-font-scraper

# Or run with Python directly
python src/enhanced_main.py https://example.com
```

**Memory Issues**
```bash
# Disable screenshots for large sites
enhanced-font-scraper https://example.com --no-screenshots

# Reduce concurrent batch processing
enhanced-font-scraper batch urls... --concurrent 1
```

**Network Timeouts**
```bash
# Increase timeout
enhanced-font-scraper https://example.com --timeout 60

# Add delay between requests
enhanced-font-scraper https://example.com --delay 2.0
```

### Error Logs

Check `font_scraper.log` for detailed error information:

```bash
tail -f font_scraper.log
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

### Testing

```bash
# Run example analyses
python run_examples.py

# Test specific functionality
python -c "from src.enhanced_main import perform_comprehensive_analysis; print('Import OK')"
```

## 📄 License

MIT License - see LICENSE file for details.

## 🆚 Version Comparison

| Feature | v1.0 | v2.0 Enhanced |
|---------|------|---------------|
| Font Detection | ✅ | ✅ Enhanced |
| Text Output | ✅ | ✅ |
| JSON/CSV Export | ✅ | ✅ |
| HTML Reports | ❌ | ✅ |
| Screenshots | ❌ | ✅ |
| Visual Samples | ❌ | ✅ |
| Performance Analysis | ❌ | ✅ |
| Batch Processing | Basic | ✅ Advanced |
| Error Recovery | Basic | ✅ Robust |
| Progress Tracking | ❌ | ✅ |

## 🔗 Links

- [Original Font Scraper](README.md)
- [Installation Guide](setup_enhanced.py)
- [Usage Examples](run_examples.py)
- [Issue Tracker](https://github.com/your-repo/issues)

---

**Enhanced Font Scraper 2.0** - Making typography analysis comprehensive, visual, and insightful. 🎨✨