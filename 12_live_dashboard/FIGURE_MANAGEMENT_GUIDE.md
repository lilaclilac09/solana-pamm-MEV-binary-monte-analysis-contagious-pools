# Figure Management Guide

## Extracted Figure Names

Based on the visual analysis, here are the complete figure titles:

1. **Figure DC-1**: Raw Event Type Distribution Across Protocols – Event Type Distribution (ORACLE vs TRADE)

2. **Figure DC-2**: pAMM Event Frequency Per Minute (Time Series) – pAMM Events per Minute - Highlighting Mitigation vs Toxic Activity

3. **Figure DC-3**: Missing Value Heatmap by Feature and Protocol – Missing Values Heatmap (Sampled 20k rows)

4. **Figure VAL-AMM-3** (CORRECTED): MEV Attack Pattern Comparison Across Validator-AMM Pairs – MEV Pattern Comparison: Trade Counts and MEV Pattern Distribution

## Deleting Figure Files in VS Code

### Method 1: Explorer Sidebar (Easiest)
1. Open Explorer (`Cmd+Shift+E` on Mac, `Ctrl+Shift+E` on Windows/Linux)
2. Navigate to the figures folder
3. Select files (hold `Cmd`/`Ctrl` for multi-select)
4. Right-click → Delete (or press `Delete` key)
5. Confirm deletion

### Method 2: Integrated Terminal
Open terminal in VS Code (`Ctrl+\`` or View → Terminal), then:

```bash
# Navigate to figures directory
cd path/to/figures

# Delete specific files
rm figure_dc1.png figure_dc2.png figure_dc3.png figure_val_amm3.png

# Or delete all PNG files (use with caution!)
rm *.png

# Or delete all figure files matching a pattern
rm figure_*.png
```

### Method 3: Command Palette
1. Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
2. Type "File: Reveal in Finder" (Mac) or "File: Reveal in File Explorer" (Windows)
3. Delete files using your OS file manager

## Regenerating the Corrected Figure

The corrected VAL-AMM-3 figure has been generated with accurate data:

### Data Summary
- **Total MEV Trades**: 650 (post-false positive elimination)
- **Fat Sandwich**: 312 trades (48.0%)
- **Back-Running (Oracle-timed)**: 0 validated trades (eliminated as false positives)
- **Classic Sandwich**: 95 trades (14.6%)
- **Front-Running**: 62 trades (9.5%)
- **Cross-Slot (2Fast)**: 46 trades (7.1%)

### To Regenerate
```bash
cd 12_live_dashboard
python3 generate_corrected_val_amm_3.py
```

This produces: `corrected_val_amm_3.png` (300 DPI, publication-ready)

## Files Created

1. **generate_corrected_val_amm_3.py** - Script to generate the corrected figure
2. **corrected_val_amm_3.png** - The corrected figure (300 DPI)
3. **RESEARCH_SECTION_VAL_AMM_3.md** - Rewritten research section for your paper
4. **Updated CHART_EXAMPLES.py** - Now includes the corrected VAL-AMM-3 implementation

## Quick Terminal Commands

```bash
# List all figure files
ls -lh *.png

# Find all PNG files in current directory and subdirectories
find . -name "*.png" -type f

# Delete old VAL-AMM-3 versions (if they exist)
rm val_amm_3_old.png figure_val_amm_3_incorrect.png

# Count total figure files
ls *.png | wc -l

# View file sizes
du -sh *.png
```

## Integration into Research Paper

The rewritten research section is available in `RESEARCH_SECTION_VAL_AMM_3.md` and includes:

- Complete data characterization narrative
- Corrected MEV attack pattern analysis
- Key findings and implications
- Methodology note on false positive elimination
- Proper citations for all figures

Copy the relevant sections into your LaTeX/Word document as needed.

---

*Generated: March 2, 2026*
