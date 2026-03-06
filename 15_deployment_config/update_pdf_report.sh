#!/bin/bash
# Update Solana_PAMM_MEV_Analysis_Report.pdf with new comprehensive content

echo "================================================================================"
echo "UPDATING SOLANA PAMM MEV ANALYSIS REPORT PDF"
echo "================================================================================"

cd "$(dirname "$0")"

# Check if pandoc is installed
if ! command -v pandoc &> /dev/null; then
    echo "❌ Pandoc not found. Installing via Homebrew..."
    brew install pandoc
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install pandoc. Please install manually:"
        echo "   brew install pandoc"
        exit 1
    fi
fi

echo "✅ Pandoc found: $(which pandoc)"
echo ""

# Source markdown file
SOURCE_MD="08_monte_carlo_risk/COMPREHENSIVE_GUIDE.md"
OUTPUT_PDF="Solana_PAMM_MEV_Analysis_Report.pdf"
BACKUP_PDF="Solana_PAMM_MEV_Analysis_Report_BACKUP_$(date +%Y%m%d_%H%M%S).pdf"

# Check if source exists
if [ ! -f "$SOURCE_MD" ]; then
    echo "❌ Source file not found: $SOURCE_MD"
    exit 1
fi

echo "📂 Source: $SOURCE_MD"
echo "📄 Output: $OUTPUT_PDF"
echo ""

# Backup existing PDF if it exists
if [ -f "$OUTPUT_PDF" ]; then
    echo "💾 Backing up existing PDF to: $BACKUP_PDF"
    cp "$OUTPUT_PDF" "$BACKUP_PDF"
fi

# Generate PDF with enhanced options
echo "📝 Generating comprehensive PDF report..."
echo ""

pandoc "$SOURCE_MD" \
    -o "$OUTPUT_PDF" \
    --pdf-engine=pdflatex \
    --variable geometry:margin=1in \
    --variable fontsize=11pt \
    --variable documentclass=report \
    --variable colorlinks=true \
    --variable linkcolor=blue \
    --variable urlcolor=blue \
    --variable toccolor=black \
    --toc \
    --toc-depth=3 \
    --number-sections \
    --highlight-style=tango \
    --metadata title="Solana PAMM MEV Analysis: Comprehensive Report" \
    --metadata author="MEV Analysis Team" \
    --metadata date="February 26, 2026" \
    -V papersize=letter \
    -V mainfont="Helvetica" \
    -V monofont="Courier New" \
    2>&1

if [ $? -eq 0 ]; then
    echo ""
    echo "================================================================================"
    echo "✅ PDF REPORT SUCCESSFULLY UPDATED"
    echo "================================================================================"
    echo ""
    echo "📊 Report Details:"
    ls -lh "$OUTPUT_PDF"
    echo ""
    echo "📍 Location: $(pwd)/$OUTPUT_PDF"
    echo "💾 Backup: $(pwd)/$BACKUP_PDF"
    echo ""
    echo "📄 Content includes:"
    echo "   ✓ Analysis Results Summary"
    echo "   ✓ MEV Attacker Case Studies (880 attackers, top 20 analysis)"
    echo "   ✓ Validator Contagion Investigation (189 validators, network topology)"
    echo "   ✓ Jupiter Multi-Hop Analysis (10.03% integration, 4.3× amplification)"
    echo "   ✓ MEV Detection Refinement (89.2% false positive reduction)"
    echo "   ✓ Technical Documentation"
    echo "   ✓ User Guide"
    echo "   ✓ Research Findings"
    echo "   ✓ Integration Instructions"
    echo "   ✓ FAQ & Troubleshooting"
    echo ""
    echo "Total: 1,625 lines of comprehensive analysis"
    echo ""
else
    echo ""
    echo "================================================================================"
    echo "❌ ERROR GENERATING PDF"
    echo "================================================================================"
    echo ""
    echo "Troubleshooting:"
    echo "1. Ensure LaTeX is installed:"
    echo "   brew install --cask mactex-no-gui"
    echo ""
    echo "2. Or use alternative PDF engine:"
    echo "   pandoc $SOURCE_MD -o $OUTPUT_PDF --pdf-engine=wkhtmltopdf"
    echo ""
    echo "3. Or generate HTML instead:"
    echo "   pandoc $SOURCE_MD -o Solana_PAMM_MEV_Analysis_Report.html --toc --toc-depth=3"
    echo ""
    exit 1
fi
