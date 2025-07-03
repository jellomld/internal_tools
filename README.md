# Font Scraper

A lightweight, professional command-line tool for analyzing fonts used on websites. Extract comprehensive font information including web fonts, system fonts, and CSS properties from any website.

## Features

- **Web Font Detection**: Automatically detects Google Fonts, Adobe Fonts, and custom web fonts
- **System Font Analysis**: Identifies system font fallbacks and font stacks
- **Multiple Output Formats**: Text, JSON, and CSV output options
- **CSS Analysis**: Parses @font-face declarations and font-family properties
- **Professional CLI**: Clean command-line interface with comprehensive options

## Installation

### Using pip (Recommended)

```bash
pip install font-scraper
```

### From Source

```bash
git clone https://github.com/username/font-scraper.git
cd font-scraper
pip install -e .
```

## Quick Start

```bash
# Analyze a website
font-scraper https://example.com

# Get JSON output
font-scraper https://example.com --output json

# Save results to file
font-scraper https://example.com --save results.txt

# Verbose output with details
font-scraper https://example.com --verbose
```

## Usage

### Basic Commands

```bash
# Analyze fonts on a website
font-scraper https://example.com

# Filter by font type
font-scraper https://example.com --filter web

# Custom timeout and delay
font-scraper https://example.com --timeout 60 --delay 2.0
```

### Output Formats

#### Text Output (Default)
```
Font Analysis Results for https://example.com
==================================================

Web Fonts (2):
  ✓ Roboto (Google Fonts)
    - Weights: 300, 400, 700
    - Styles: normal, italic

  ✓ Open Sans (Google Fonts)
    - Weights: 400, 600

System Fonts (3):
  ✓ Arial
  ✓ Helvetica
  ✓ Georgia

✓ Found 5 fonts
```

#### JSON Output
```bash
font-scraper https://example.com --output json
```

```json
{
  "url": "https://example.com",
  "fonts": [
    {
      "name": "Roboto",
      "type": "web",
      "provider": "Google Fonts",
      "weights": ["300", "400", "700"],
      "styles": ["normal", "italic"],
      "source": "https://fonts.googleapis.com/css2?family=Roboto"
    }
  ],
  "statistics": {
    "total_fonts": 5,
    "web_fonts": 2,
    "system_fonts": 3
  }
}
```

#### CSV Output
```bash
font-scraper https://example.com --output csv --save results.csv
```

## Command Line Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--output` | `-o` | Output format (text, json, csv) | text |
| `--save` | `-s` | Save results to file | - |
| `--verbose` | `-v` | Show detailed information | false |
| `--timeout` | `-t` | Request timeout in seconds | 30 |
| `--delay` | | Delay between requests | 1.0 |
| `--filter` | `-f` | Filter by font type (web, system, custom) | - |
| `--no-external` | | Skip external CSS files | false |
| `--no-colors` | | Disable colored output | false |

## Examples

### Analyze Multiple Font Types
```bash
# Only web fonts
font-scraper https://typography.com --filter web

# Include system fonts
font-scraper https://example.com --include-system

# Exclude external CSS
font-scraper https://example.com --no-external
```

### Export and Analysis
```bash
# Export to JSON for further analysis
font-scraper https://fonts.google.com --output json --save google-fonts.json

# CSV for spreadsheet analysis
font-scraper https://github.com --output csv --save github-fonts.csv
```

## Requirements

- Python 3.8+
- Internet connection for website analysis

## Dependencies

The tool uses minimal, well-maintained dependencies:

- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing
- `cssutils` - CSS parsing
- `click` - CLI interface
- `colorama` - Terminal colors
- `tinycss2` - Alternative CSS parser
- `lxml` - XML/HTML processing

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📧 Email: support@fontscraper.dev
- 🐛 Issues: [GitHub Issues](https://github.com/username/font-scraper/issues)
- 📖 Documentation: [GitHub Wiki](https://github.com/username/font-scraper/wiki)
