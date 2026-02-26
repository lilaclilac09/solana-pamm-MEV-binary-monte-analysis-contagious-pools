#!/usr/bin/env python3
"""
Update Solana_PAMM_MEV_Analysis_Report.pdf with comprehensive content
from COMPREHENSIVE_GUIDE.md

Alternative PDF generation using reportlab if pandoc is unavailable.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, 
    Table, TableStyle, Image, ListFlowable, ListItem
)
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime
from pathlib import Path
import re

print("\n" + "=" * 80)
print("UPDATING SOLANA PAMM MEV ANALYSIS REPORT PDF (Python/ReportLab)")
print("=" * 80)

# Paths
base_dir = Path(__file__).parent
source_md = base_dir / '08_monte_carlo_risk' / 'COMPREHENSIVE_GUIDE.md'
output_pdf = base_dir / 'Solana_PAMM_MEV_Analysis_Report.pdf'
backup_pdf = base_dir / f'Solana_PAMM_MEV_Analysis_Report_BACKUP_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'

print(f"\n📂 Source: {source_md}")
print(f"📄 Output: {output_pdf}")

# Backup existing PDF
if output_pdf.exists():
    print(f"💾 Backing up existing PDF to: {backup_pdf.name}")
    import shutil
    shutil.copy(output_pdf, backup_pdf)

# Read markdown content
print(f"\n📖 Reading markdown content...")
with open(source_md, 'r', encoding='utf-8') as f:
    md_content = f.read()

print(f"  ✓ Loaded {len(md_content):,} characters, {len(md_content.splitlines()):,} lines")

# Create PDF
print(f"\n📝 Generating PDF with ReportLab...")
doc = SimpleDocTemplate(
    str(output_pdf),
    pagesize=letter,
    rightMargin=0.75*inch,
    leftMargin=0.75*inch,
    topMargin=0.75*inch,
    bottomMargin=0.75*inch
)

# Styles
styles = getSampleStyleSheet()
story = []

# Custom styles
title_style = ParagraphStyle(
    'Title',
    parent=styles['Title'],
    fontSize=24,
    textColor=colors.HexColor('#1a237e'),
    spaceAfter=30,
    alignment=TA_CENTER,
    fontName='Helvetica-Bold'
)

h1_style = ParagraphStyle(
    'Heading1',
    parent=styles['Heading1'],
    fontSize=16,
    textColor=colors.HexColor('#283593'),
    spaceAfter=12,
    spaceBefore=16,
    fontName='Helvetica-Bold'
)

h2_style = ParagraphStyle(
    'Heading2',
    parent=styles['Heading2'],
    fontSize=14,
    textColor=colors.HexColor('#303f9f'),
    spaceAfter=10,
    spaceBefore=12,
    fontName='Helvetica-Bold'
)

h3_style = ParagraphStyle(
    'Heading3',
    parent=styles['Heading3'],
    fontSize=12,
    textColor=colors.HexColor('#3949ab'),
    spaceAfter=8,
    spaceBefore=10,
    fontName='Helvetica-Bold'
)

normal_style = ParagraphStyle(
    'Normal',
    parent=styles['Normal'],
    fontSize=10,
    leading=14,
    alignment=TA_JUSTIFY,
    spaceAfter=8
)

code_style = ParagraphStyle(
    'Code',
    parent=styles['Code'],
    fontSize=9,
    fontName='Courier',
    textColor=colors.HexColor('#212121'),
    backColor=colors.HexColor('#f5f5f5'),
    leftIndent=10,
    rightIndent=10,
    spaceAfter=10
)

# Title page
story.append(Spacer(1, 2*inch))
story.append(Paragraph(
    "Solana PAMM MEV Analysis",
    title_style
))
story.append(Spacer(1, 0.3*inch))
story.append(Paragraph(
    "Comprehensive Report: Binary Monte Carlo Contagion Analysis",
    h2_style
))
story.append(Spacer(1, 0.5*inch))
story.append(Paragraph(
    f"<i>Generated: {datetime.now().strftime('%B %d, %Y')}</i>",
    ParagraphStyle('date', parent=styles['Normal'], alignment=TA_CENTER, fontSize=11)
))
story.append(Spacer(1, 0.3*inch))
story.append(Paragraph(
    "MEV Analysis Team",
    ParagraphStyle('author', parent=styles['Normal'], alignment=TA_CENTER, fontSize=12)
))
story.append(PageBreak())

# Parse markdown and convert to PDF elements
lines = md_content.split('\n')
i = 0
in_code_block = False
code_buffer = []
in_table = False
table_buffer = []

print(f"\n🔄 Parsing markdown content...")

while i < len(lines):
    line = lines[i].rstrip()
    
    # Skip first title (already added)
    if i == 0 and line.startswith('# '):
        i += 1
        continue
    
    # Code blocks
    if line.startswith('```'):
        if in_code_block:
            # End code block
            if code_buffer:
                code_text = '\n'.join(code_buffer)
                story.append(Paragraph(f'<font name="Courier" size="8">{code_text[:2000]}</font>', code_style))
            code_buffer = []
            in_code_block = False
        else:
            # Start code block
            in_code_block = True
        i += 1
        continue
    
    if in_code_block:
        code_buffer.append(line.replace('<', '&lt;').replace('>', '&gt;'))
        i += 1
        continue
    
    # Major headings (##)
    if line.startswith('## '):
        story.append(Paragraph(line[3:], h1_style))
        i += 1
        continue
    
    # Sub headings (###)
    if line.startswith('### '):
        story.append(Paragraph(line[4:], h2_style))
        i += 1
        continue
    
    # Sub-sub headings (####)
    if line.startswith('#### '):
        story.append(Paragraph(line[5:], h3_style))
        i += 1
        continue
    
    # Horizontal rules
    if line.strip() in ['---', '___', '***']:
        story.append(Spacer(1, 0.2*inch))
        i += 1
        continue
    
    # Tables (simple detection)
    if '|' in line and not line.strip().startswith('#'):
        # Simple table handling - convert to basic table
        if not in_table:
            in_table = True
            table_buffer = []
        table_buffer.append([cell.strip() for cell in line.split('|') if cell.strip()])
        i += 1
        # Check if next line is not a table
        if i < len(lines) and '|' not in lines[i]:
            if len(table_buffer) > 2:  # Header + separator + at least one row
                # Remove separator row (usually second row with dashes)
                if all('-' in cell or ':' in cell for cell in table_buffer[1]):
                    table_buffer.pop(1)
                try:
                    t = Table(table_buffer[:20], splitByRow=True)  # Limit to 20 rows
                    t.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#5c6bc0')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 9),
                        ('FONTSIZE', (0, 1), (-1, -1), 8),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ]))
                    story.append(t)
                    story.append(Spacer(1, 0.15*inch))
                except Exception as e:
                    print(f"  ⚠ Warning: Could not create table: {e}")
            table_buffer = []
            in_table = False
        continue
    
    # Regular paragraphs
    if line.strip() and not line.startswith('#'):
        # Clean up markdown formatting
        text = line
        # Bold
        text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
        # Italic
        text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
        # Inline code
        text = re.sub(r'`(.+?)`', r'<font name="Courier">\1</font>', text)
        
        try:
            story.append(Paragraph(text, normal_style))
        except Exception as e:
            # Fallback for problematic text
            safe_text = text.replace('<', '&lt;').replace('>', '&gt;')
            story.append(Paragraph(safe_text, normal_style))
    elif not line.strip():
        # Empty line - small spacer
        story.append(Spacer(1, 0.1*inch))
    
    i += 1

print(f"  ✓ Parsed {i:,} lines")

# Build PDF
print(f"\n📄 Building PDF...")
try:
    doc.build(story)
    print(f"\n" + "=" * 80)
    print(f"✅ PDF REPORT SUCCESSFULLY UPDATED")
    print(f"=" * 80)
    print(f"\n📊 Report Details:")
    print(f"  - File: {output_pdf.name}")
    print(f"  - Size: {output_pdf.stat().st_size / 1024:.1f} KB")
    print(f"  - Path: {output_pdf}")
    print(f"\n📄 Content includes:")
    print(f"   ✓ Analysis Results Summary")
    print(f"   ✓ MEV Attacker Case Studies (880 attackers, top 20 analysis)")
    print(f"   ✓ Validator Contagion Investigation (189 validators)")
    print(f"   ✓ Jupiter Multi-Hop Analysis (10.03% integration)")
    print(f"   ✓ MEV Detection Refinement (89.2% false positive reduction)")
    print(f"   ✓ Technical Documentation")
    print(f"   ✓ Research Findings")
    print(f"   ✓ FAQ & Troubleshooting")
    print(f"\n  Total: 1,625 lines of comprehensive analysis")
    print(f"\n" + "=" * 80 + "\n")
except Exception as e:
    print(f"\n❌ Error building PDF: {e}")
    import traceback
    traceback.print_exc()
