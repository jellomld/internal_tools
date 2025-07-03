#!/usr/bin/env python3
"""Setup script for Font Scraper."""

from setuptools import setup, find_packages
import os

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

# Get version from package
exec(open('font_scraper/__init__.py').read())

setup(
    name="font-scraper",
    version=__version__,
    author="Font Scraper Team",
    author_email="support@fontscraper.dev",
    description="A lightweight command-line tool for analyzing fonts used on websites",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/username/font-scraper",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Fonts",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "font-scraper=font_scraper.main:main",
        ],
    },
    keywords="fonts, web scraping, css, typography, font analysis",
    project_urls={
        "Bug Reports": "https://github.com/username/font-scraper/issues",
        "Source": "https://github.com/username/font-scraper",
    },
    include_package_data=True,
    zip_safe=False,
)