#!/usr/bin/env python3
"""
Generate PDF Report from Comprehensive Guide

Converts COMPREHENSIVE_GUIDE.md to a professional PDF report.

Usage:
    python3 generate_pdf_report.py
    
Output:
    COMPREHENSIVE_MEV_ANALYSIS_REPORT.pdf
    
Requirements:
    pip install markdown pdfkit
    # macOS: brew install wkhtmltopdf
    # Linux: sudo apt-get install wkhtmltopdf
"""

import markdown
import pdfkit
from pathlib import Path
from datetime import datetime

print("\n" + "="*80)
print("PDF REPORT GENERATION")
print("="*80)

# Paths
base_dir = Path(__file__).parent
guide_path = base_dir / '08_monte_carlo_risk' / 'COMPREHENSIVE_GUIDE.md'
output_path = base_dir / 'COMPREHENSIVE_MEV_ANALYSIS_REPORT.pdf'

print(f"\n📂 Input: {guide_path}")
print(f"📄 Output: {output_path}")

# Read Markdown
print("\n📖 Reading Markdown content...")
with open(guide_path, 'r', encoding='utf-8') as f:
    md_content = f.read()

print(f"  ✓ Loaded {len(md_content):,} characters")

# Convert Markdown to HTML
print("\n🔄 Converting Markdown to HTML...")
html_content = markdown.markdown(
    md_content,
    extensions=[
        'markdown.extensions.tables',
        'markdown.extensions.fenced_code',
        'markdown.extensions.codehilite',
        'markdown.extensions.toc',
        'markdown.extensions.extra'
    ]
)

print(f"  ✓ Generated {len(html_content):,} characters of HTML")

# Add CSS styling for professional appearance
css_style = """
<style>
    body {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        line-height: 1.6;
        color: #333;
        max-width: 900px;
        margin: 0 auto;
        padding: 20px;
    }
    h1 {
        color: #2c3e50;
        border-bottom: 3px solid #3498db;
        padding-bottom: 10px;
    }
    h2 {
        color: #34495e;
        border-bottom: 2px solid #95a5a6;
        padding-bottom: 8px;
        margin-top: 30px;
    }
    h3 {
        color: #7f8c8d;
        margin-top: 20px;
    }
    table {
        border-collapse: collapse;
        width: 100%;
        margin: 20px 0;
    }
    th {
        background-color: #3498db;
        color: white;
        font-weight: bold;
        padding: 12px;
        text-align: left;
        border: 1px solid #2980b9;
    }
    td {
        padding: 10px;
        border: 1px solid #bdc3c7;
    }
    tr:nth-child(even) {
        background-color: #ecf0f1;
    }
    code {
        background-color: #f4f4f4;
        padding: 2px 6px;
        border-radius: 3px;
        font-family: 'Courier New', monospace;
        font-size: 0.9em;
    }
    pre {
        background-color: #2c3e50;
        color: #ecf0f1;
        padding: 15px;
        border-radius: 5px;
        overflow-x: auto;
    }
    pre code {
        background-color: transparent;
        color: #ecf0f1;
        padding: 0;
    }
    .highlight {
        background-color: #fff9c4;
        padding: 2px 4px;
    }
    blockquote {
        border-left: 4px solid #3498db;
        padding-left: 15px;
        margin-left: 0;
        color: #7f8c8d;
        font-style: italic;
    }
    a {
        color: #3498db;
        text-decoration: none;
    }
    a:hover {
        text-decoration: underline;
    }
</style>
"""

# Create full HTML document
html_doc = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Comprehensive MEV Analysis Report</title>
    {css_style}
</head>
<body>
    <div style="text-align: center; margin-bottom: 40px;">
        <h1 style="font-size: 2.5em; margin-bottom: 10px;">Comprehensive MEV Analysis Report</h1>
        <p style="font-size: 1.2em; color: #7f8c8d;">
            Solana pAMM MEV Binary Monte Carlo Analysis
        </p>
        <p style="color: #95a5a6;">
            Generated: {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}
        </p>
        <hr style="border: 2px solid #3498db; width: 50%;">
    </div>
    {html_content}
    <div style="text-align: center; margin-top: 60px; padding-top: 20px; border-top: 2px solid #bdc3c7;">
        <p style="color: #95a5a6; font-size: 0.9em;">
            End of Report | Generated from COMPREHENSIVE_GUIDE.md
        </p>
    </div>
</body>
</html>
"""

print("\n🎨 HTML document created with professional styling")

# PDF options for wkhtmltopdf
options = {
    'page-size': 'Letter',
    'margin-top': '0.75in',
    'margin-right': '0.75in',
    'margin-bottom': '0.75in',
    'margin-left': '0.75in',
    'encoding': 'UTF-8',
    'no-outline': None,
    'enable-local-file-access': None,
    'print-media-type': None,
}

# Generate PDF
print("\n📄 Generating PDF...")
try:
    pdfkit.from_string(html_doc, str(output_path), options=options)
    print(f"  ✓ PDF generated successfully!")
    print(f"\n📊 Report Details:")
    print(f"  - File: {output_path.name}")
    print(f"  - Size: {output_path.stat().st_size / 1024:.1f} KB")
    print(f"  - Path: {output_path}")
    
except Exception as e:
    print(f"\n❌ Error generating PDF: {e}")
    print("\n💡 Solution:")
    print("  1. Install wkhtmltopdf:")
    print("     macOS: brew install wkhtmltopdf")
    print("     Linux: sudo apt-get install wkhtmltopdf")
    print("  2. Install Python packages:")
    print("     pip install markdown pdfkit")
    print("\n  Alternative: Use pandoc")
    print("     brew install pandoc")
    print("     pandoc 08_monte_carlo_risk/COMPREHENSIVE_GUIDE.md -o REPORT.pdf")

print("\n" + "="*80)
print("✅ PDF GENERATION COMPLETE")
print("="*80 + "\n")
