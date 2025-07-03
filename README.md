# Font Scraper

A powerful command-line tool for analyzing fonts used on websites. This tool extracts comprehensive font information including web fonts, system fonts, CSS properties, and font loading details from any website.

## Features

- **Comprehensive Font Detection**: Finds all fonts used on a website including:
  - Web fonts (@font-face declarations)
  - System font fallbacks
  - Google Fonts, Adobe Fonts, Font Awesome
  - Custom font services
- **Multiple Output Formats**: Text, JSON, and CSV output
- **Detailed Analysis**: Font weights, styles, formats, CSS selectors, and sources
- **Respectful Scraping**: Built-in delays and proper user agent handling
- **Robust Error Handling**: Graceful handling of network issues and malformed CSS
- **Batch Processing**: Analyze multiple websites at once

## Installation

### 🚀 Quick Install (Recommended for macOS)

#### One-Command Install
```bash
# Download and run the installer
curl -sSL https://raw.githubusercontent.com/infamous/font-scraper/main/install-macos.sh | bash
```

#### Or clone and install
```bash
git clone https://github.com/infamous/font-scraper.git
cd font-scraper
make install
```

#### Homebrew (Coming Soon)
```bash
brew tap infamous/tools
brew install font-scraper
```

### 🔧 Alternative Installation Methods

#### Option 1: Quick Makefile Commands
```bash
make help          # See all available commands
make install       # Quick install
make install-dev   # Development mode
make check         # Verify installation
```

#### Option 2: Manual Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Make the script executable
chmod +x font-scraper

# Run directly
./font-scraper https://example.com
```

#### Option 3: Package Installation
```bash
# Install as a package
pip install -e .

# Run from anywhere
font-scraper https://example.com
```

#### Option 4: Python Module
```bash
# Run as a Python module
python -m src.main https://example.com
```

## Usage

### Basic Usage
```bash
# Analyze a website
font-scraper https://example.com

# Get detailed output
font-scraper https://example.com --verbose

# Save results to file
font-scraper https://example.com --save results.txt

# Output as JSON
font-scraper https://example.com --output json --save results.json

# Filter by font type
font-scraper https://example.com --filter web
```

### Advanced Options
```bash
# Custom timeout and delay
font-scraper https://example.com --timeout 60 --delay 2.0

# Skip external CSS files
font-scraper https://example.com --no-external

# Exclude system fonts
font-scraper https://example.com --include-system false

# Custom user agent
font-scraper https://example.com --user-agent "Custom Bot 1.0"

# Disable colors
font-scraper https://example.com --no-colors
```

### Command Line Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--output` | `-o` | Output format (text, json, csv) | text |
| `--save` | `-s` | Save results to file | - |
| `--verbose` | `-v` | Show detailed information | false |
| `--timeout` | `-t` | Request timeout in seconds | 30 |
| `--user-agent` | `-u` | Custom user agent string | - |
| `--no-external` | - | Skip external CSS files | false |
| `--include-system` | - | Include system fonts | true |
| `--no-colors` | - | Disable colored output | false |
| `--delay` | - | Delay between requests (seconds) | 1.0 |
| `--filter` | `-f` | Filter by font type (web, system, custom) | - |

## Output Examples

### Text Output
```
Font Analysis Results for https://example.com
==================================================

Summary:
- Total fonts found: 8
- Web fonts: 3
- System fonts: 4
- Custom fonts: 1
- CSS files analyzed: 2
- Google Fonts: 2

Web Fonts (3):
  ✓ Roboto (Google Fonts)
    - Weights: 300, 400, 700
    - Styles: normal, italic
    - Format: woff2

  ✓ Open Sans (Google Fonts)
    - Weights: 400, 600
    - Styles: normal

System Fonts (4):
  ✓ Arial
  ✓ Helvetica
  ✓ Times New Roman
  ✓ Georgia

✓ Found 8 fonts
```

### JSON Output
```json
{
  "url": "https://example.com",
  "timestamp": "2024-01-15T10:30:00Z",
  "fonts": [
    {
      "name": "Roboto",
      "type": "web",
      "provider": "Google Fonts",
      "weights": ["300", "400", "700"],
      "styles": ["normal", "italic"],
      "format": "woff2",
      "source": "https://fonts.googleapis.com/css2?family=Roboto",
      "selectors": [".header", ".nav", "body"]
    }
  ],
  "statistics": {
    "total_fonts": 8,
    "web_fonts": 3,
    "system_fonts": 4,
    "custom_fonts": 1
  }
}
```

## Dependencies

- **requests**: HTTP requests for fetching web pages
- **beautifulsoup4**: HTML parsing
- **cssutils**: CSS parsing and analysis
- **click**: Command-line interface
- **colorama**: Colored terminal output
- **validators**: URL validation
- **tinycss2**: Alternative CSS parser
- **lxml**: XML/HTML processing

## Architecture

The font scraper is built with a modular architecture:

```
src/
├── main.py              # CLI interface and entry point
├── font_detector.py     # Main font detection engine
├── scraper.py           # Web scraping functionality
├── css_parser.py        # CSS parsing and font extraction
├── output_formatter.py  # Results formatting
└── utils.py             # Data structures and utilities
```

### Key Components

1. **WebScraper**: Handles fetching HTML and CSS content
2. **CSSParser**: Parses CSS to extract font information
3. **FontDetector**: Coordinates analysis and font detection
4. **OutputFormatter**: Formats results in various output formats

## Font Detection Strategy

The tool uses multiple strategies to detect fonts:

1. **CSS Analysis**: Parses all CSS files for font-family declarations and @font-face rules
2. **Web Font Services**: Detects Google Fonts, Adobe Fonts, Font Awesome, and other CDNs
3. **HTML Analysis**: Examines inline styles and font loading scripts
4. **Import Processing**: Follows @import statements to analyze additional CSS

## Examples

### Analyze Google's Homepage
```bash
font-scraper https://google.com --verbose --output json --save google-fonts.json
```

### Check Font Usage on Multiple Sites
```bash
font-scraper https://github.com https://stackoverflow.com https://medium.com --filter web
```

### Get CSV Report for Spreadsheet Analysis
```bash
font-scraper https://typography.com --output csv --save typography-analysis.csv
```

## Troubleshooting

### Common Issues

1. **Connection Timeouts**: Increase timeout with `--timeout 60`
2. **Rate Limiting**: Increase delay with `--delay 2.0`
3. **Missing Fonts**: Use `--verbose` to see detailed extraction info
4. **Large Sites**: Use `--no-external` to skip external CSS files

### Error Handling

The tool gracefully handles:
- Network connection issues
- Malformed HTML/CSS
- Missing or blocked resources
- Rate limiting
- Invalid URLs

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Changelog

### v1.0.0
- Initial release
- Complete font detection functionality
- Multiple output formats
- Comprehensive CLI interface
- Robust error handling
