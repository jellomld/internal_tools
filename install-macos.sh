#!/bin/bash
set -e

# Font Scraper - macOS Easy Install Script
echo "🔤 Font Scraper - macOS Installation"
echo "=================================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first:"
    echo "   brew install python3"
    echo "   or download from: https://www.python.org/downloads/"
    exit 1
fi

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not available. Installing..."
    python3 -m ensurepip --upgrade
fi

echo "✅ Python 3 detected: $(python3 --version)"

# Create installation directory
INSTALL_DIR="$HOME/.local/bin"
mkdir -p "$INSTALL_DIR"

# Add to PATH if not already there
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo "📝 Adding $INSTALL_DIR to your PATH..."
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bash_profile
    export PATH="$HOME/.local/bin:$PATH"
fi

echo "📦 Installing Font Scraper..."

# Install the package
pip3 install --user -e .

# Create a convenient symlink
ln -sf "$(which font-scraper)" "$INSTALL_DIR/font-scraper" 2>/dev/null || true

echo ""
echo "🎉 Installation Complete!"
echo ""
echo "Usage:"
echo "  font-scraper https://example.com"
echo "  font-scraper --help"
echo ""
echo "Note: You may need to restart your terminal or run:"
echo "  source ~/.zshrc"
echo ""