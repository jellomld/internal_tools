# Font Scraper - macOS Installation Guide

This guide provides multiple simplified installation options for Font Scraper on macOS.

## 🚀 Recommended: One-Command Install

The fastest way to get started:

```bash
curl -sSL https://raw.githubusercontent.com/infamous/font-scraper/main/install-macos.sh | bash
```

## 🔧 Alternative Methods

### Method 1: Clone and Use Makefile
```bash
git clone https://github.com/infamous/font-scraper.git
cd font-scraper
make install
```

### Method 2: Homebrew (Future)
```bash
# Coming soon!
brew tap infamous/tools
brew install font-scraper
```

### Method 3: Standalone Binary
```bash
# Download pre-built binary (when available)
curl -L -o font-scraper https://github.com/infamous/font-scraper/releases/latest/download/font-scraper-macos
chmod +x font-scraper
sudo mv font-scraper /usr/local/bin/
```

### Method 4: Build Your Own Binary
```bash
git clone https://github.com/infamous/font-scraper.git
cd font-scraper
./build-binary.sh
```

## 📋 What Each Method Does

| Method | Pros | Cons | Best For |
|--------|------|------|----------|
| One-Command Install | Fastest, handles everything | Requires internet | Most users |
| Makefile | Clean, organized commands | Need to clone first | Developers |
| Homebrew | Native macOS, easy updates | Not available yet | macOS enthusiasts |
| Pre-built Binary | No Python needed | Larger file size | Simple setups |
| Build Binary | Customizable | Takes time to build | Advanced users |

## ✅ Verification

After installation, verify it works:

```bash
font-scraper --help
font-scraper https://example.com
```

## 🗑️ Uninstall

To remove Font Scraper:

```bash
make uninstall
# or manually:
pip3 uninstall font-scraper
rm -f ~/.local/bin/font-scraper
```

## 🚨 Troubleshooting

### Python Not Found
```bash
# Install Python via Homebrew
brew install python3

# Or download from python.org
# https://www.python.org/downloads/
```

### Permission Denied
```bash
# Make scripts executable
chmod +x install-macos.sh
chmod +x build-binary.sh
```

### PATH Issues
```bash
# Add to PATH (restart terminal after)
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

## 📞 Support

If you encounter issues:
1. Check that Python 3.7+ is installed: `python3 --version`
2. Ensure pip is working: `pip3 --version`
3. Try the manual installation method from the main README
4. Open an issue on GitHub

---

**Previous Installation (Still Works)**

The original installation methods from the README still work if you prefer them:
- `pip install -e .`
- Direct script execution
- Python module mode