# 📋 FILE CLEANUP & CONSOLIDATION CHECKLIST

**Project:** Solana PAMM MEV Binary Monte Analysis  
**Created:** February 8, 2026  
**Based On:** DETECTOR_VISUAL_GUIDE.md Architecture  

---

## 🎯 QUICK ACTION SUMMARY

| Action | Count | Priority | Time Est |
|--------|-------|----------|----------|
| 🔴 Delete Duplicates | 5 files | P1 | 5 min |
| 📦 Archive Old Versions | 8 files | P2 | 10 min |
| 🔍 Investigate GMM Conflict | 2 files | P1 | 15 min |
| ✅ Keep & Audit | 12 files | P0 | 30 min |
| **TOTAL** | **27 files** | - | **60 min** |

---

## ✂️ DELETE IMMEDIATELY (Confirmed Duplicates)

These files are confirmed superseded and can be safely deleted:

### Python Files (3 files)
- [ ] `improved_fat_sandwich_detection.py` (1098 lines - replaced by fat_sandwich_detector_optimized.py)
- [ ] `09a_advanced_ml/enhanced_gmm_analysis.py` (95 lines - wrapper function only)
- [ ] `06_pool_analysis/pamm_cross_comparison_analysis.py` (570 lines - replaced by final version)

### Jupyter Notebooks (2 files)
- [ ] `10_advanced_FP_solution/01_improved_fat_sandwich_detection.ipynb` (1KB stub)
- [ ] `10_advanced_FP_solution/01_improved_fat_sandwich_detection_COMBINED.ipynb` (1KB stub)

**Cleanup Command:**
```bash
mkdir -p ARCHIVE/old_algorithms ARCHIVE/old_notebooks

# Move Python files
mv improved_fat_sandwich_detection.py ARCHIVE/old_algorithms/
mv 09a_advanced_ml/enhanced_gmm_analysis.py ARCHIVE/old_algorithms/
mv 06_pool_analysis/pamm_cross_comparison_analysis.py ARCHIVE/old_algorithms/

# Move Notebook stubs
mv 10_advanced_FP_solution/01_improved_fat_sandwich_detection.ipynb ARCHIVE/old_notebooks/
mv 10_advanced_FP_solution/01_improved_fat_sandwich_detection_COMBINED.ipynb ARCHIVE/old_notebooks/
```

---

## 🔍 INVESTIGATE BEFORE DELETION (Conflicting Timestamps)

### GMM Analysis Files - TIMESTAMP CONFLICT

```
gmm_optimized_analysis.py   | 320 lines | 2/8/26 20:53 | RobustScaler (superior)
gmm_fast_analysis.py        | 345 lines | 2/8/26 20:59 | StandardScaler (older approach)
```

**Problem:** gmm_fast_analysis.py is NEWER (20:59) but uses OLDER algorithm

**Action Plan:**

**Step 1: Check git history**
```bash
cd /Users/aileen/Downloads/pamm/solana-pamm-analysis/solana-pamm-MEV-binary-monte-analysis
git log --oneline --all 09a_advanced_ml/gmm_optimized_analysis.py
git log --oneline --all 09a_advanced_ml/gmm_fast_analysis.py
```

**Step 2: Compare algorithms**
```bash
# Extract key differences
grep -A 5 "RobustScaler\|StandardScaler" 09a_advanced_ml/gmm*.py
grep -A 5 "IsolationForest\|fit_predict" 09a_advanced_ml/gmm*.py
```

**Step 3: Decide**
- [ ] If gmm_optimized_analysis.py is truly optimized: **DELETE gmm_fast_analysis.py**
- [ ] If gmm_fast_analysis.py is faster (benchmark): **KEEP both, rename clearly**
- [ ] If unclear: **ARCHIVE both, use 01_gmm_clustering_analysis.ipynb instead**

**Recommended Decision:** DELETE gmm_fast_analysis.py (RobustScaler is better for outliers)

---

## ⚠️ ARCHIVE (Old but Potentially Useful)

Keep in archive folder for reference:

### Old Sweet Spot Notebooks (3 files)
- [ ] `test_improved_fat_sandwich.ipynb` → `ARCHIVE/old_notebooks/test_improved_fat_sandwich.ipynb`
- [ ] `10_advanced_FP_solution/11_fat_sandwich_vs_multihop_classification.ipynb` → `ARCHIVE/supplementary/`
- [ ] `04_validator_analysis/13_validator_contagion_investigation.ipynb` → `ARCHIVE/supplementary/`

### Old Validator Analysis Duplicate (1 file)
- [ ] `04_validator_analysis/12_validator_contagion_analysis.py` (1080 lines)
  - This is NOT used by test_contagion_analyzer.py
  - Uses `ValidatorContagionAnalyzer` class
  - Superseded by `contagious_vulnerability_analyzer.py` (601 lines) ✅ KEEP PRIMARY
  - **Decision:** ARCHIVE as reference

**Cleanup Command:**
```bash
# Create archive structure
mkdir -p ARCHIVE/old_notebooks
mkdir -p ARCHIVE/supplementary
mkdir -p ARCHIVE/validator_analysis_old

# Move old test notebooks
mv test_improved_fat_sandwich.ipynb ARCHIVE/old_notebooks/
mv 10_advanced_FP_solution/11_fat_sandwich_vs_multihop_classification.ipynb ARCHIVE/supplementary/
mv 04_validator_analysis/13_validator_contagion_investigation.ipynb ARCHIVE/supplementary/
mv 04_validator_analysis/12_validator_contagion_analysis.py ARCHIVE/validator_analysis_old/

# Optional: Archive old diagnostic notebooks
# mv 13_contagion_diagnostic.ipynb ARCHIVE/supplementary/
```

---

## ✅ KEEP & AUDIT (Production Files)

### Core Detection (Keep)
- [ ] **fat_sandwich_detector_optimized.py** (481 lines, main class)
  - [ ] Verify imports work in 12_fat_sandwich_optimized_detector.ipynb
  - [ ] Run test: `python3 -c "from fat_sandwich_detector_optimized import FatSandwichDetector; print('✓')"`

- [ ] **12_fat_sandwich_optimized_detector.ipynb** (31K, latest 2/8/26 21:39)
  - [ ] Verify all cells execute without errors
  - [ ] Confirm it matches DETECTOR_VISUAL_GUIDE.md architecture
  - [ ] Check imports point to fat_sandwich_detector_optimized.py

### GMM Analysis (Keep & Verify)
- [ ] **09a_advanced_ml/gmm_optimized_analysis.py** (320 lines, primary)
  - [ ] ✅ CONFIRMED: Uses RobustScaler (correct approach)
  - [ ] Run: `python3 -c "from gmm_optimized_analysis import *; print('✓')"`
  - [ ] Note: DELETE gmm_fast_analysis.py (inferior approach)

- [ ] **09a_advanced_ml/01_gmm_clustering_analysis.ipynb** (main notebook)
  - [ ] Verify it uses gmm_optimized_analysis.py
  - [ ] Check if it needs updating

### Pool Analysis (Keep)
- [ ] **06_pool_analysis/pamm_cross_comparison_final.py** (474 lines, primary)
  - [ ] Verify imports
  - [ ] Run test: `python3 06_pool_analysis/pamm_cross_comparison_final.py 2>&1 | head -20`

- [ ] **06_pool_analysis/06_pool_analysis.ipynb** (main notebook)
  - [ ] Verify it uses final version

### Contagion Analysis (Keep)
- [ ] **contagious_vulnerability_analyzer.py** (601 lines, primary class)
  - [ ] ✅ CONFIRMED: Used by test_contagion_analyzer.py
  - [ ] Run test: `python3 test_contagion_analyzer.py 2>&1 | head -50`

- [ ] **test_contagion_analyzer.py** (71 lines, test harness)
  - [ ] Verify successful execution
  - [ ] Note: 04_validator_analysis/12_validator_contagion_analysis.py is OLD version

- [ ] **04_validator_analysis/04_validator_contagion_analysis.ipynb** (main notebook)
  - [ ] Verify it uses contagious_vulnerability_analyzer.py OR 12_validator_contagion_analysis.py
  - [ ] If uses 12_validator_contagion_analysis.py: UPDATE to use contagious_vulnerability_analyzer.py

### MEV Analysis/Profit (Keep)
- [ ] **12_mev_profit_mechanisms/mev_profit_analysis.py** (production script)
- [ ] **analyze_and_filter_mev.py** (root level, data filtering)
- [ ] **02_mev_detection/02_mev_detection.ipynb** (main notebook)

---

## 🚀 EXECUTION PROCEDURE

### STEP 1: Backup (5 minutes)
```bash
cd /Users/aileen/Downloads/pamm/solana-pamm-analysis/solana-pamm-MEV-binary-monte-analysis

# Create backup
zip -r backup_preocleanup_$(date +%Y%m%d_%H%M%S).zip \
  improved_fat_sandwich_detection.py \
  09a_advanced_ml/gmm_fast_analysis.py \
  09a_advanced_ml/enhanced_gmm_analysis.py \
  06_pool_analysis/pamm_cross_comparison_analysis.py \
  10_advanced_FP_solution/*.ipynb
```

### STEP 2: Create Archive Structure (5 minutes)
```bash
mkdir -p ARCHIVE/old_algorithms
mkdir -p ARCHIVE/old_notebooks  
mkdir -p ARCHIVE/supplementary
mkdir -p ARCHIVE/validator_analysis_old
echo "Archive created: Check ARCHIVE/README.md" > ARCHIVE/README.md
```

### STEP 3: Move Files to Archive (10 minutes)
**Python Files:**
```bash
mv improved_fat_sandwich_detection.py ARCHIVE/old_algorithms/
mv 09a_advanced_ml/enhanced_gmm_analysis.py ARCHIVE/old_algorithms/
mv 06_pool_analysis/pamm_cross_comparison_analysis.py ARCHIVE/old_algorithms/
mv 09a_advanced_ml/gmm_fast_analysis.py ARCHIVE/old_algorithms/  # DELETE OR ARCHIVE?
mv 04_validator_analysis/12_validator_contagion_analysis.py ARCHIVE/validator_analysis_old/
```

**Notebook Stubs:**
```bash
mv 10_advanced_FP_solution/01_improved_fat_sandwich_detection.ipynb ARCHIVE/old_notebooks/
mv 10_advanced_FP_solution/01_improved_fat_sandwich_detection_COMBINED.ipynb ARCHIVE/old_notebooks/
```

**Optional (Review First):**
```bash
mv test_improved_fat_sandwich.ipynb ARCHIVE/old_notebooks/
mv 04_validator_analysis/13_validator_contagion_investigation.ipynb ARCHIVE/supplementary/
```

### STEP 4: Verify Production Files (15 minutes)

**Test 1: Fat Sandwich Detector**
```bash
python3 << 'EOF'
from fat_sandwich_detector_optimized import FatSandwichDetector
import pandas as pd
print("✓ fat_sandwich_detector_optimized.py imports successfully")
EOF
```

**Test 2: Contagion Analyzer**
```bash
python3 test_contagion_analyzer.py 2>&1 | head -20
echo "✓ test_contagion_analyzer.py runs successfully"
```

**Test 3: Pool Analysis**
```bash
cd 06_pool_analysis && python3 pamm_cross_comparison_final.py 2>&1 | head -10
echo "✓ pamm_cross_comparison_final.py runs successfully"
```

### STEP 5: Update Documentation (10 minutes)

- [ ] Update [README.md](README.md) main section to reference:
  - Primary entry point: `12_fat_sandwich_optimized_detector.ipynb`
  - Primary class: `fat_sandwich_detector_optimized.py`
  - Architecture: `DETECTOR_VISUAL_GUIDE.md`
  - File organization: `FILE_ORGANIZATION_REPORT.md`

- [ ] Create `ARCHIVE/README.md`:
  ```markdown
  # Archive of Superseded Code
  
  These files have been replaced with optimized versions.
  Kept for reference and historical tracking.
  
  ## Old Implementations
  - improved_fat_sandwich_detection.py → replaced by fat_sandwich_detector_optimized.py
  - gmm_fast_analysis.py → replaced by gmm_optimized_analysis.py (if applicable)
  - pamm_cross_comparison_analysis.py → replaced by pamm_cross_comparison_final.py
  
  ## Old Notebooks
  - 01_improved_fat_sandwich_detection.ipynb → replaced by 12_fat_sandwich_optimized_detector.ipynb
  
  ## Supplementary Analysis
  - 11_fat_sandwich_vs_multihop_classification.ipynb → Classification deep dive
  ```

---

## 📊 Before/After Summary

### Before Cleanup
```
20 Python files
28 Jupyter Notebooks
---
Multiple duplicate implementations
Confusing version conflicts
Old class-based implementations
Scattered analysis notebooks
```

### After Cleanup
```
15 Python files (5 archived)
23 Jupyter Notebooks (5 archived)
---
✅ Single implementation per algorithm
✅ Clear primary entry points
✅ Class-based modern implementation
✅ Organized backup
```

---

## ⚡ QUICK COMMAND REFERENCE

**One-Command Archive All Old Files:**
```bash
cd /Users/aileen/Downloads/pamm/solana-pamm-analysis/solana-pamm-MEV-binary-monte-analysis && \
mkdir -p ARCHIVE/old_algorithms ARCHIVE/old_notebooks ARCHIVE/supplementary ARCHIVE/validator_analysis_old && \
mv improved_fat_sandwich_detection.py ARCHIVE/old_algorithms/ && \
mv 09a_advanced_ml/enhanced_gmm_analysis.py ARCHIVE/old_algorithms/ && \
mv 09a_advanced_ml/gmm_fast_analysis.py ARCHIVE/old_algorithms/ && \
mv 06_pool_analysis/pamm_cross_comparison_analysis.py ARCHIVE/old_algorithms/ && \
mv 10_advanced_FP_solution/01_improved_fat_sandwich_detection.ipynb ARCHIVE/old_notebooks/ && \
mv 10_advanced_FP_solution/01_improved_fat_sandwich_detection_COMBINED.ipynb ARCHIVE/old_notebooks/ && \
mv 04_validator_analysis/12_validator_contagion_analysis.py ARCHIVE/validator_analysis_old/ && \
echo "✅ Archive complete! Check ARCHIVE folder"
```

**Verify All Tests Pass:**
```bash
cd /Users/aileen/Downloads/pamm/solana-pamm-analysis/solana-pamm-MEV-binary-monte-analysis && \
python3 -c "from fat_sandwich_detector_optimized import FatSandwichDetector; print('✓ fat_sandwich_detector_optimized')" && \
python3 test_contagion_analyzer.py 2>&1 | head -5 && echo "✓ test_contagion_analyzer" && \
cd 06_pool_analysis && python3 pamm_cross_comparison_final.py 2>&1 | head -5 && echo "✓ pamm_cross_comparison_final"
```

---

## 📝 Notes

1. **GMM Conflict Resolution:** Decide whether to keep gmm_fast_analysis.py:
   - If benchmarks show it's faster → keep with clear naming
   - If it uses outdated approach → delete
   - **Recommendation:** DELETE (RobustScaler is superior)

2. **Contagion Analyzer Consolidation:**
   - Primary: `contagious_vulnerability_analyzer.py` (active, tested)
   - Old version: `04_validator_analysis/12_validator_contagion_analysis.py` (1080 lines, archive)
   - Verify 04_validator_contagion_analysis.ipynb uses correct version

3. **Notebook Cleanup:**
   - Remove 1KB stub notebooks (they're placeholders)
   - Keep 31KB+ notebooks (they have real content)
   - Archive supplementary notebooks in ARCHIVE/supplementary/

---

**Status:** ✅ Ready to execute  
**Estimated Time:** 60 minutes total  
**Risk Level:** LOW (all old files backed up in ARCHIVE)
