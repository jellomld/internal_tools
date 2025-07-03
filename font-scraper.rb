class FontScraper < Formula
  desc "Command-line tool for analyzing fonts used on websites"
  homepage "https://github.com/infamous/font-scraper"
  url "https://github.com/infamous/font-scraper/archive/v1.0.0.tar.gz"
  sha256 "YOUR_SHA256_HERE"  # Replace with actual SHA256 of the release archive
  license "MIT"

  depends_on "python@3.11"

  def install
    virtualenv_install_with_resources
  end

  test do
    system "#{bin}/font-scraper", "--help"
  end
end