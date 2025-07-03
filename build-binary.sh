#!/bin/bash
set -e

echo "📦 Building Font Scraper Standalone Binary for macOS"
echo "=================================================="

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo "📥 Installing PyInstaller..."
    pip3 install pyinstaller
fi

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build/ dist/ *.spec

# Create binary
echo "🔨 Building standalone binary..."
pyinstaller \
    --onefile \
    --name font-scraper \
    --add-data "src:src" \
    --hidden-import src.main \
    --hidden-import src.font_detector \
    --hidden-import src.scraper \
    --hidden-import src.css_parser \
    --hidden-import src.output_formatter \
    --hidden-import src.utils \
    src/main.py

# Test the binary
echo "🧪 Testing the binary..."
./dist/font-scraper --help > /dev/null

echo ""
echo "✅ Binary build complete!"
echo "📍 Location: ./dist/font-scraper"
echo "📏 Size: $(du -h ./dist/font-scraper | cut -f1)"
echo ""
echo "To install the binary:"
echo "  sudo cp ./dist/font-scraper /usr/local/bin/"
echo ""
echo "Or for user-only install:"
echo "  mkdir -p ~/.local/bin"
echo "  cp ./dist/font-scraper ~/.local/bin/"
echo "  echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.zshrc"
echo ""