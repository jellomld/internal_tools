"""HTML report generation for font analysis results."""

import os
import json
import base64
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
import logging

from jinja2 import Template
from PIL import Image

from src.utils import Font, ScrapeResults

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generates comprehensive HTML reports for font analysis."""
    
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        self.screenshots_dir = self.output_dir / 'screenshots'
        self.screenshots_dir.mkdir(exist_ok=True)
        
        self.assets_dir = self.output_dir / 'assets'
        self.assets_dir.mkdir(exist_ok=True)
    
    def generate_report(self, results: ScrapeResults, screenshots: Dict[str, str], 
                       font_samples: Dict[str, str], font_usage_analysis: Dict = None) -> str:
        """Generate a comprehensive HTML report."""
        
        # Copy images to assets directory and get relative paths
        screenshot_paths = self._copy_images_to_assets(screenshots)
        font_sample_paths = self._copy_images_to_assets(font_samples)
        
        # Generate report data
        report_data = {
            'url': results.url,
            'timestamp': datetime.now(),
            'analysis_timestamp': results.timestamp,
            'fonts': results.fonts,
            'statistics': results.statistics,
            'screenshots': screenshot_paths,
            'font_samples': font_sample_paths,
            'font_usage_analysis': font_usage_analysis or {},
            'css_files': results.css_files,
            'errors': results.errors,
            'summary': self._generate_enhanced_summary(results),
            'font_categories': self._categorize_fonts(results.fonts),
            'provider_analysis': self._analyze_providers(results.fonts),
            'performance_metrics': self._calculate_performance_metrics(results.fonts)
        }
        
        # Generate HTML report
        html_content = self._render_html_template(report_data)
        
        # Save report
        report_path = self.output_dir / 'font_analysis_report.html'
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Generate additional files
        self._generate_json_data(report_data)
        self._generate_css_file()
        
        return str(report_path)
    
    def _copy_images_to_assets(self, image_paths: Dict[str, str]) -> Dict[str, str]:
        """Copy images to assets directory and return relative paths."""
        relative_paths = {}
        
        for name, path in image_paths.items():
            if os.path.exists(path):
                filename = f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                dest_path = self.assets_dir / filename
                
                try:
                    # Copy and optionally resize image
                    with Image.open(path) as img:
                        # Resize if too large
                        if img.width > 1200:
                            ratio = 1200 / img.width
                            new_height = int(img.height * ratio)
                            img = img.resize((1200, new_height), Image.Resampling.LANCZOS)
                        
                        img.save(dest_path, 'PNG', optimize=True)
                    
                    relative_paths[name] = f"assets/{filename}"
                except Exception as e:
                    logger.error(f"Error copying image {path}: {e}")
        
        return relative_paths
    
    def _generate_enhanced_summary(self, results: ScrapeResults) -> Dict:
        """Generate an enhanced summary with additional insights."""
        fonts = results.fonts
        
        summary = {
            'total_fonts': len(fonts),
            'web_fonts': len([f for f in fonts if f.type == 'web']),
            'system_fonts': len([f for f in fonts if f.type == 'system']),
            'custom_fonts': len([f for f in fonts if f.type == 'custom']),
            'unique_providers': len(set(f.provider for f in fonts if f.provider)),
            'google_fonts': len([f for f in fonts if f.provider == 'Google Fonts']),
            'adobe_fonts': len([f for f in fonts if f.provider == 'Adobe Fonts']),
            'font_awesome': len([f for f in fonts if f.provider == 'Font Awesome']),
            'total_font_weights': sum(len(f.weights) for f in fonts if f.weights),
            'total_font_styles': sum(len(f.styles) for f in fonts if f.styles),
        }
        
        # Font format analysis
        formats = {}
        for font in fonts:
            if font.format:
                formats[font.format] = formats.get(font.format, 0) + 1
        summary['formats'] = formats
        
        # Weight distribution
        weights = {}
        for font in fonts:
            for weight in font.weights:
                weights[weight] = weights.get(weight, 0) + 1
        summary['weight_distribution'] = weights
        
        return summary
    
    def _categorize_fonts(self, fonts: List[Font]) -> Dict[str, List[Font]]:
        """Categorize fonts by various criteria."""
        categories = {
            'by_type': {'web': [], 'system': [], 'custom': []},
            'by_provider': {},
            'by_format': {},
            'by_weight_count': {'single': [], 'multiple': []},
            'by_usage': {'headers': [], 'body': [], 'navigation': [], 'other': []}
        }
        
        for font in fonts:
            # By type
            if font.type in categories['by_type']:
                categories['by_type'][font.type].append(font)
            
            # By provider
            provider = font.provider or 'Unknown'
            if provider not in categories['by_provider']:
                categories['by_provider'][provider] = []
            categories['by_provider'][provider].append(font)
            
            # By format
            format_name = font.format or 'Unknown'
            if format_name not in categories['by_format']:
                categories['by_format'][format_name] = []
            categories['by_format'][format_name].append(font)
            
            # By weight count
            weight_category = 'multiple' if len(font.weights) > 1 else 'single'
            categories['by_weight_count'][weight_category].append(font)
            
            # By usage (based on selectors)
            usage_type = self._determine_usage_type(font.selectors)
            categories['by_usage'][usage_type].append(font)
        
        return categories
    
    def _determine_usage_type(self, selectors: List[str]) -> str:
        """Determine the primary usage type based on selectors."""
        if not selectors:
            return 'other'
        
        selector_text = ' '.join(selectors).lower()
        
        if any(header in selector_text for header in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'title', 'heading']):
            return 'headers'
        elif any(nav in selector_text for nav in ['nav', 'menu', 'navigation', 'navbar']):
            return 'navigation'
        elif any(body in selector_text for body in ['p', 'body', 'content', 'text', 'article']):
            return 'body'
        else:
            return 'other'
    
    def _analyze_providers(self, fonts: List[Font]) -> Dict:
        """Analyze font providers and their characteristics."""
        providers = {}
        
        for font in fonts:
            provider = font.provider or 'Unknown'
            if provider not in providers:
                providers[provider] = {
                    'count': 0,
                    'fonts': [],
                    'total_weights': 0,
                    'formats': set(),
                    'has_web_fonts': False
                }
            
            provider_data = providers[provider]
            provider_data['count'] += 1
            provider_data['fonts'].append(font.name)
            provider_data['total_weights'] += len(font.weights)
            
            if font.format:
                provider_data['formats'].add(font.format)
            
            if font.type == 'web':
                provider_data['has_web_fonts'] = True
        
        # Convert sets to lists for JSON serialization
        for provider_data in providers.values():
            provider_data['formats'] = list(provider_data['formats'])
        
        return providers
    
    def _calculate_performance_metrics(self, fonts: List[Font]) -> Dict:
        """Calculate performance-related metrics."""
        metrics = {
            'web_font_requests': len([f for f in fonts if f.type == 'web' and f.source]),
            'external_font_services': len(set(f.provider for f in fonts if f.provider and f.type == 'web')),
            'total_font_variants': sum(len(f.weights) * len(f.styles) for f in fonts if f.weights and f.styles),
            'google_fonts_requests': len([f for f in fonts if f.provider == 'Google Fonts']),
            'custom_font_files': len([f for f in fonts if f.type == 'web' and f.provider == 'Custom']),
        }
        
        # Estimate potential performance impact
        if metrics['web_font_requests'] > 5:
            metrics['performance_concern'] = 'High number of web font requests may impact load time'
        elif metrics['web_font_requests'] > 2:
            metrics['performance_concern'] = 'Moderate web font usage'
        else:
            metrics['performance_concern'] = 'Low web font usage'
        
        return metrics
    
    def _render_html_template(self, data: Dict) -> str:
        """Render the HTML template with data."""
        template_str = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Font Analysis Report - {{ data.url }}</title>
    <link rel="stylesheet" href="assets/report_styles.css">
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 2rem; }
        .container { max-width: 1200px; margin: 0 auto; padding: 0 1rem; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; margin: 2rem 0; }
        .card { background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); padding: 1.5rem; }
        .screenshot { max-width: 100%; height: auto; border-radius: 4px; margin: 1rem 0; }
        .font-item { border: 1px solid #e0e0e0; border-radius: 4px; padding: 1rem; margin: 0.5rem 0; }
        .font-name { font-weight: bold; color: #333; margin-bottom: 0.5rem; }
        .font-details { font-size: 0.9em; color: #666; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; }
        .stat-card { text-align: center; background: #f8f9fa; padding: 1rem; border-radius: 4px; }
        .stat-number { font-size: 2rem; font-weight: bold; color: #667eea; }
        .error { background: #ffe6e6; border: 1px solid #ff9999; padding: 0.5rem; border-radius: 4px; margin: 0.5rem 0; }
        .success { color: #28a745; }
        .warning { color: #ffc107; }
        .tabs { border-bottom: 2px solid #e0e0e0; margin: 2rem 0 1rem 0; }
        .tab { display: inline-block; padding: 0.5rem 1rem; cursor: pointer; border-bottom: 2px solid transparent; }
        .tab.active { border-bottom-color: #667eea; color: #667eea; font-weight: bold; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
    </style>
</head>
<body>
    <div class="header">
        <div class="container">
            <h1>Font Analysis Report</h1>
            <p>Analysis of {{ data.url }}</p>
            <p>Generated on {{ data.timestamp.strftime('%B %d, %Y at %I:%M %p') }}</p>
        </div>
    </div>
    
    <div class="container">
        <!-- Summary Statistics -->
        <div class="card" style="margin: 2rem 0;">
            <h2>Summary Statistics</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{{ data.summary.total_fonts }}</div>
                    <div>Total Fonts</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{{ data.summary.web_fonts }}</div>
                    <div>Web Fonts</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{{ data.summary.system_fonts }}</div>
                    <div>System Fonts</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{{ data.summary.unique_providers }}</div>
                    <div>Font Providers</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{{ data.performance_metrics.web_font_requests }}</div>
                    <div>Web Font Requests</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{{ data.performance_metrics.total_font_variants }}</div>
                    <div>Font Variants</div>
                </div>
            </div>
        </div>
        
        <!-- Screenshots -->
        {% if data.screenshots %}
        <div class="card">
            <h2>Website Screenshots</h2>
            <div class="grid">
                {% for name, path in data.screenshots.items() %}
                <div>
                    <h3>{{ name.replace('_', ' ').title() }}</h3>
                    <img src="{{ path }}" alt="{{ name }}" class="screenshot">
                </div>
                {% endfor %}
            </div>
        </div>
        {% endif %}
        
        <!-- Font Samples -->
        {% if data.font_samples %}
        <div class="card">
            <h2>Font Samples</h2>
            {% for name, path in data.font_samples.items() %}
            <div style="margin: 1rem 0;">
                <h3>{{ name.replace('_', ' ').title() }}</h3>
                <img src="{{ path }}" alt="{{ name }}" class="screenshot">
            </div>
            {% endfor %}
        </div>
        {% endif %}
        
        <!-- Detailed Font Analysis -->
        <div class="card">
            <h2>Font Analysis</h2>
            
            <div class="tabs">
                <div class="tab active" onclick="showTab('web-fonts')">Web Fonts</div>
                <div class="tab" onclick="showTab('system-fonts')">System Fonts</div>
                <div class="tab" onclick="showTab('providers')">Providers</div>
                <div class="tab" onclick="showTab('performance')">Performance</div>
            </div>
            
            <div id="web-fonts" class="tab-content active">
                <h3>Web Fonts ({{ data.font_categories.by_type.web|length }})</h3>
                {% for font in data.font_categories.by_type.web %}
                <div class="font-item">
                    <div class="font-name">{{ font.name }}</div>
                    <div class="font-details">
                        {% if font.provider %}<strong>Provider:</strong> {{ font.provider }}<br>{% endif %}
                        {% if font.weights %}<strong>Weights:</strong> {{ font.weights|join(', ') }}<br>{% endif %}
                        {% if font.styles %}<strong>Styles:</strong> {{ font.styles|join(', ') }}<br>{% endif %}
                        {% if font.format %}<strong>Format:</strong> {{ font.format }}<br>{% endif %}
                        {% if font.source %}<strong>Source:</strong> <a href="{{ font.source }}" target="_blank">{{ font.source[:60] }}...</a><br>{% endif %}
                    </div>
                </div>
                {% endfor %}
            </div>
            
            <div id="system-fonts" class="tab-content">
                <h3>System Fonts ({{ data.font_categories.by_type.system|length }})</h3>
                {% for font in data.font_categories.by_type.system %}
                <div class="font-item">
                    <div class="font-name">{{ font.name }}</div>
                    <div class="font-details">
                        <strong>Type:</strong> System Font<br>
                        {% if font.selectors %}<strong>Used in:</strong> {{ font.selectors[:3]|join(', ') }}{% if font.selectors|length > 3 %} (and {{ font.selectors|length - 3 }} more){% endif %}{% endif %}
                    </div>
                </div>
                {% endfor %}
            </div>
            
            <div id="providers" class="tab-content">
                <h3>Font Providers Analysis</h3>
                {% for provider, info in data.provider_analysis.items() %}
                <div class="font-item">
                    <div class="font-name">{{ provider }}</div>
                    <div class="font-details">
                        <strong>Font Count:</strong> {{ info.count }}<br>
                        <strong>Total Weights:</strong> {{ info.total_weights }}<br>
                        <strong>Formats:</strong> {{ info.formats|join(', ') }}<br>
                        <strong>Fonts:</strong> {{ info.fonts[:5]|join(', ') }}{% if info.fonts|length > 5 %} (and {{ info.fonts|length - 5 }} more){% endif %}
                    </div>
                </div>
                {% endfor %}
            </div>
            
            <div id="performance" class="tab-content">
                <h3>Performance Analysis</h3>
                <div class="font-item">
                    <div class="font-name">Performance Metrics</div>
                    <div class="font-details">
                        <strong>Web Font Requests:</strong> {{ data.performance_metrics.web_font_requests }}<br>
                        <strong>External Font Services:</strong> {{ data.performance_metrics.external_font_services }}<br>
                        <strong>Total Font Variants:</strong> {{ data.performance_metrics.total_font_variants }}<br>
                        <strong>Google Fonts Requests:</strong> {{ data.performance_metrics.google_fonts_requests }}<br>
                        <strong>Assessment:</strong> <span class="{% if 'High' in data.performance_metrics.performance_concern %}warning{% else %}success{% endif %}">{{ data.performance_metrics.performance_concern }}</span>
                    </div>
                </div>
                
                <h4>Recommendations</h4>
                <div class="font-item">
                    <ul>
                        {% if data.performance_metrics.web_font_requests > 5 %}
                        <li class="warning">Consider reducing the number of web font requests to improve load times</li>
                        {% endif %}
                        {% if data.performance_metrics.total_font_variants > 10 %}
                        <li class="warning">High number of font variants may impact performance - consider using fewer weights/styles</li>
                        {% endif %}
                        {% if data.performance_metrics.google_fonts_requests > 0 %}
                        <li class="success">Google Fonts provides optimized delivery and caching</li>
                        {% endif %}
                        <li>Consider using font-display: swap for better loading performance</li>
                        <li>Preload critical fonts to reduce layout shift</li>
                    </ul>
                </div>
            </div>
        </div>
        
        <!-- Errors -->
        {% if data.errors %}
        <div class="card">
            <h2>Analysis Errors</h2>
            {% for error in data.errors %}
            <div class="error">{{ error }}</div>
            {% endfor %}
        </div>
        {% endif %}
        
        <!-- Technical Details -->
        <div class="card">
            <h2>Technical Details</h2>
            <div class="font-details">
                <strong>Analysis Duration:</strong> {{ (data.timestamp - data.analysis_timestamp).total_seconds() }} seconds<br>
                <strong>CSS Files Analyzed:</strong> {{ data.css_files|length }}<br>
                <strong>User Agent:</strong> Font Scraper Tool<br>
                <strong>Analysis Method:</strong> CSS parsing, DOM analysis, screenshot capture
            </div>
        </div>
    </div>
    
    <script>
        function showTab(tabName) {
            // Hide all tab contents
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            
            // Remove active class from all tabs
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Show selected tab content
            document.getElementById(tabName).classList.add('active');
            
            // Add active class to clicked tab
            event.target.classList.add('active');
        }
    </script>
</body>
</html>
        """
        
        template = Template(template_str)
        return template.render(data=data)
    
    def _generate_json_data(self, data: Dict):
        """Generate JSON data file for programmatic access."""
        json_path = self.output_dir / 'analysis_data.json'
        
        # Convert non-serializable objects
        json_data = {
            'url': data['url'],
            'timestamp': data['timestamp'].isoformat(),
            'analysis_timestamp': data['analysis_timestamp'].isoformat(),
            'fonts': [self._font_to_dict(font) for font in data['fonts']],
            'statistics': data['statistics'],
            'summary': data['summary'],
            'performance_metrics': data['performance_metrics'],
            'provider_analysis': data['provider_analysis'],
            'css_files': data['css_files'],
            'errors': data['errors']
        }
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
    
    def _font_to_dict(self, font: Font) -> Dict:
        """Convert Font object to dictionary."""
        return {
            'name': font.name,
            'type': font.type,
            'source': font.source,
            'weights': font.weights,
            'styles': font.styles,
            'format': font.format,
            'provider': font.provider,
            'selectors': font.selectors,
            'unicode_range': font.unicode_range
        }
    
    def _generate_css_file(self):
        """Generate CSS file for the report."""
        css_content = """
/* Font Analysis Report Styles */
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    padding: 0;
    background-color: #f5f5f5;
    color: #333;
    line-height: 1.6;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 1rem;
}

.header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 2rem;
    text-align: center;
}

.header h1 {
    margin: 0 0 0.5rem 0;
    font-size: 2.5rem;
}

.header p {
    margin: 0.25rem 0;
    opacity: 0.9;
}

.card {
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    padding: 1.5rem;
    margin: 2rem 0;
}

.card h2 {
    margin-top: 0;
    color: #333;
    border-bottom: 2px solid #667eea;
    padding-bottom: 0.5rem;
}

.grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
    margin: 2rem 0;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 1rem;
}

.stat-card {
    text-align: center;
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 4px;
    border: 1px solid #e9ecef;
}

.stat-number {
    font-size: 2rem;
    font-weight: bold;
    color: #667eea;
    display: block;
}

.screenshot {
    max-width: 100%;
    height: auto;
    border-radius: 4px;
    margin: 1rem 0;
    border: 1px solid #ddd;
}

.font-item {
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    padding: 1rem;
    margin: 0.5rem 0;
    background: #fafafa;
}

.font-name {
    font-weight: bold;
    color: #333;
    margin-bottom: 0.5rem;
    font-size: 1.1rem;
}

.font-details {
    font-size: 0.9rem;
    color: #666;
    line-height: 1.4;
}

.font-details strong {
    color: #333;
}

.error {
    background: #ffe6e6;
    border: 1px solid #ff9999;
    padding: 0.5rem;
    border-radius: 4px;
    margin: 0.5rem 0;
    color: #cc0000;
}

.success {
    color: #28a745;
}

.warning {
    color: #ffc107;
}

.tabs {
    border-bottom: 2px solid #e0e0e0;
    margin: 2rem 0 1rem 0;
}

.tab {
    display: inline-block;
    padding: 0.5rem 1rem;
    cursor: pointer;
    border-bottom: 2px solid transparent;
    margin-right: 1rem;
    transition: all 0.3s ease;
}

.tab:hover {
    background-color: #f8f9fa;
}

.tab.active {
    border-bottom-color: #667eea;
    color: #667eea;
    font-weight: bold;
}

.tab-content {
    display: none;
    padding: 1rem 0;
}

.tab-content.active {
    display: block;
}

.tab-content h3 {
    color: #667eea;
    margin-top: 0;
}

.tab-content h4 {
    color: #333;
    margin: 1.5rem 0 1rem 0;
}

.tab-content ul {
    margin: 0;
    padding-left: 1.5rem;
}

.tab-content li {
    margin: 0.5rem 0;
}

a {
    color: #667eea;
    text-decoration: none;
}

a:hover {
    text-decoration: underline;
}

@media (max-width: 768px) {
    .header h1 {
        font-size: 2rem;
    }
    
    .stats-grid {
        grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    }
    
    .grid {
        grid-template-columns: 1fr;
    }
    
    .tab {
        font-size: 0.9rem;
        padding: 0.4rem 0.8rem;
    }
}
        """
        
        css_path = self.assets_dir / 'report_styles.css'
        with open(css_path, 'w', encoding='utf-8') as f:
            f.write(css_content)