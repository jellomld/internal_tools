.PHONY: install install-dev uninstall clean test help brew-install

# Default Python command
PYTHON := python3
PIP := pip3

help: ## Show this help message
	@echo "Font Scraper - macOS Installation Options"
	@echo "========================================"
	@echo ""
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""

install: ## Quick install (recommended for most users)
	@echo "🔤 Installing Font Scraper..."
	@./install-macos.sh

install-dev: ## Install in development mode
	@echo "📦 Installing Font Scraper in development mode..."
	@$(PIP) install --user -e .
	@echo "✅ Development installation complete!"

install-global: ## Install globally (requires sudo)
	@echo "🌍 Installing Font Scraper globally..."
	@sudo $(PIP) install .
	@echo "✅ Global installation complete!"

brew-install: ## Install via Homebrew (after adding tap)
	@echo "🍺 Installing via Homebrew..."
	@echo "First, add the tap: brew tap your-username/font-scraper"
	@echo "Then run: brew install font-scraper"

uninstall: ## Uninstall Font Scraper
	@echo "🗑️  Uninstalling Font Scraper..."
	@$(PIP) uninstall -y font-scraper || true
	@rm -f ~/.local/bin/font-scraper
	@echo "✅ Uninstallation complete!"

clean: ## Clean build artifacts
	@echo "🧹 Cleaning build artifacts..."
	@rm -rf build/ dist/ *.egg-info/
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@echo "✅ Clean complete!"

test: ## Run tests
	@echo "🧪 Running tests..."
	@$(PYTHON) -m pytest tests/ -v

binary: ## Create standalone binary (requires PyInstaller)
	@echo "📦 Creating standalone binary..."
	@$(PIP) install pyinstaller
	@pyinstaller --onefile --name font-scraper src/main.py
	@echo "✅ Binary created in dist/font-scraper"

check: ## Check if installation is working
	@echo "🔍 Checking Font Scraper installation..."
	@font-scraper --help > /dev/null && echo "✅ Font Scraper is working!" || echo "❌ Font Scraper not found or not working"