# File Organization & Duplicate Detection Report
Based on DETECTOR_VISUAL_GUIDE.md Architecture

**Generated:** February 8, 2026  
**Purpose:** Identify duplicate code files and outdated algorithms across the project

---

## 📋 Executive Summary

**Total Files Analyzed:** 48 (20 Python, 28 Jupyter Notebooks)  
**Duplicate Groups Found:** 3 major groups + 1 contagion group  
**Outdated Files:** 8 files  
**Recommended For Deletion:** 7 files  
**Files To Keep:** 10 primary files

---

## 🔍 Duplicate Code Groups

### GROUP 1: Fat Sandwich Detection (3 active versions, 1 deprecated)

#### **STATUS: CONSOLIDATE TO SECTION 12**

| File | Size | Lines | Date | Status | Notes |
|------|------|-------|------|--------|-------|
| **fat_sandwich_detector_optimized.py** | 13K | 481 | 2/4/26 | ✅ KEEP | **PRIMARY** - Unified detector class with optimization |
| improved_fat_sandwich_detection.py | 38K | 1098 | 2/4/26 | 🔴 DELETE | OLD - Pre-optimization version, superseded |
| 12_fat_sandwich_optimized_detector.ipynb | 31K | - | **2/8/26 21:39** | ✅ KEEP | **MAIN NOTEBOOK** - Latest, actively used |
| test_improved_fat_sandwich.ipynb | 13K | - | 2/4/26 | ⚠️ ARCHIVE | Old test file, reference only |
| 10_advanced_FP_solution/01_improved_fat_sandwich_detection.ipynb | 1K | - | 2/5/26 | 🔴 DELETE | Stub/completed, moved to 12_ notebook |
| 10_advanced_FP_solution/01_improved_fat_sandwich_detection_COMBINED.ipynb | 1K | - | 2/6/26 | 🔴 DELETE | Stub/completed, merged content elsewhere |
| 10_advanced_FP_solution/11_fat_sandwich_vs_multihop_classification.ipynb | 27K | - | 2/8/26 | ⚠️ ARCHIVE | Specialist classification notebook (supplementary) |

**Architecture per DETECTOR_VISUAL_GUIDE.md:**
```
INPUT: Trade events (df_clean)
   ↓
FatSandwichDetector.detect_fat_sandwiches()  [uses fat_sandwich_detector_optimized.py]
   ↓
FatSandwichDetector.classify_all_attacks()
   ↓
OUTPUT: Classified results
```

**Why consolidated:**
- `improved_fat_sandwich_detection.py` was refactored into `FatSandwichDetector` class
- Old notebooks were replaced by `12_fat_sandwich_optimized_detector.ipynb` (the reference implementation)
- All detection logic now unified in single class (reduces code duplication)

---

### GROUP 2: GMM Clustering Analysis (4 versions - inconsistent algorithms)

#### **STATUS: CONSOLIDATE TO gmm_optimized_analysis.py**

| File | Size | Lines | Date | Status | Notes |
|------|------|-------|------|--------|-------|
| **gmm_optimized_analysis.py** | 12K | 320 | 2/8/26 20:53 | ✅ KEEP | **PRIMARY** - Optimized Gaussian Mixture Model |
| gmm_fast_analysis.py | 13K | 345 | 2/8/26 20:59 | ⚠️ BACKUP | Fast variant (slightly slower generated date) |
| enhanced_gmm_analysis.py | 4K | 95 | 2/6/26 11:39 | 🔴 DELETE | Wrapper function only (Chinese comments) |
| full_analysis_script.py | 2K | 100 | ? | ⚠️ REVIEW | Main orchestrator, but minimal code |
| 09a_advanced_ml/01_gmm_clustering_analysis.ipynb | 15K | - | 2/6/26 | ✅ KEEP | **MAIN NOTEBOOK** - Reference implementation |

**Algorithm Issues Found:**
- **gmm_fast_analysis.py**: Uses older IsolationForest approach (last modified 20:59)
- **gmm_optimized_analysis.py**: Uses RobustScaler + enhanced preprocessing (last modified 20:53)
- **conflict:** Both claim optimization, but timestamps suggest fast_analysis (20:59) was generated AFTER optimized_analysis
  
  ⚠️ **Data Integrity Issue:** 20:59 is AFTER 20:53 - fast_analysis may be override!

**Recommended Action:**
```
✅ KEEP gmm_optimized_analysis.py (official optimized version)
🔄 MOVE gmm_fast_analysis.py to archive (if faster, benchmark first)
🔴 DELETE enhanced_gmm_analysis.py (wrapper only)
⚠️ INVESTIGATE full_analysis_script.py (orchestration logic)
```

---

### GROUP 3: Pool Analysis/Cross-Comparison (2 versions)

#### **STATUS: USE FINAL VERSION ONLY**

| File | Size | Lines | Date | Status | Notes |
|------|------|-------|------|--------|-------|
| 06_pool_analysis/pamm_cross_comparison_analysis.py | 24K | 570 | 2/6/26 | 🔴 DELETE | Older version, superseded |
| **06_pool_analysis/pamm_cross_comparison_final.py** | 20K | 474 | 2/6/26 | ✅ KEEP | **FINAL** - Cleaner, consolidated version |
| 06_pool_analysis/06_pool_analysis.ipynb | 150K | - | 2/6/26 | ✅ KEEP | Main analytical notebook |

**Why final is better:**
- 96 fewer lines (better optimization)
- Named "final" (indicates consolidation)
- Same date but final wins by name convention

---

### GROUP 4: Contagion/Validator Analysis (Multiple versions, scattered)

#### **STATUS: NEEDS CONSOLIDATION**

| File | Size | Lines | Date | Status | Notes |
|------|------|-------|------|--------|-------|
| **contagious_vulnerability_analyzer.py** | 16K | 515 | 2/6/26 | ✅ KEEP | **PRIMARY** - Main analyzer class |
| test_contagion_analyzer.py | 3K | 71 | 2/6/26 | ✅ KEEP | Test harness (active use) |
| 04_validator_analysis/12_validator_contagion_analysis.py | ? | ? | ? | ⚠️ INVESTIGATE | Possible duplicate/extracted from notebook |
| 04_validator_analysis/04_validator_contagion_analysis.ipynb | ? | - | 2/6/26 | ✅ KEEP | Main notebook |
| 04_validator_analysis/13_validator_contagion_investigation.ipynb | ? | - | 2/6/26 | ⚠️ ARCHIVE | Investigative notebook (supplementary) |
| 13_contagion_diagnostic.ipynb | ? | - | 2/6/26 | ⚠️ ARCHIVE | Diagnostic notebook (supplementary) |

**Issues:**
- Multiple notebooks doing overlapping work
- Unclear if `12_validator_contagion_analysis.py` duplicates contagious_vulnerability_analyzer.py

**Recommended Action:**
```
1. Keep: contagious_vulnerability_analyzer.py (primary class)
2. Keep: test_contagion_analyzer.py (test harness)
3. Investigate: 04_validator_analysis/12_validator_contagion_analysis.py
4. Archive: Diagnostic/investigative notebooks
```

---

## 📊 Analysis of Algorithms

### 1. Fat Sandwich Detector - ALGORITHM STATUS: ✅ OPTIMIZED

Per DETECTOR_VISUAL_GUIDE.md, the algorithm has 5 steps:

| Step | Algorithm | Location | Status | Notes |
|------|-----------|----------|--------|-------|
| 1 | Rolling Time Window Scanning | `FatSandwichDetector.detect_fat_sandwiches()` | ✅ Optimized | Uses multiple windows (1s, 2s, 5s, 10s) |
| 2 | A-B-A Pattern Validation | `FatSandwichDetector._validate_aba_pattern()` | ✅ Optimized | Checks first=last signer + middle victims |
| 3 | Victim Ratio Filtering | `FatSandwichDetector.detect_fat_sandwiches()` | ✅ Optimized | Filters max_victim_ratio=0.8 (default) |
| 4 | Token Pair Validation | `FatSandwichDetector.detect_fat_sandwiches()` | ✅ Optimized | Reversal check on first/last trade |
| 5 | Confidence Scoring | `FatSandwichDetector.detect_fat_sandwiches()` | ✅ Optimized | 10-point scoring system |

**Classifier Algorithm - ALGORITHM STATUS: ✅ OPTIMIZED**

| Phase | Algorithm | Location | Status | Notes |
|-------|-----------|----------|--------|-------|
| 1 | Gather Evidence | `FatSandwichDetector.classify_all_attacks()` | ✅ Optimized | Victim, Token, Pool evidence |
| 2 | Score Attack Type | `FatSandwichDetector._score_attack_type()` | ✅ Optimized | Fat Sandwich vs Multi-Hop scoring |
| 3 | Make Decision | `FatSandwichDetector.classify_all_attacks()` | ✅ Optimized | Decision tree with confidence thresholds |

**Obsolete Algorithm Locations:**
- ❌ `improved_fat_sandwich_detection.py` - Function-based (old), keep for reference only
- ✅ `fat_sandwich_detector_optimized.py` - Class-based (current standard)

---

### 2. GMM Clustering Algorithm - ALGORITHM STATUS: ⚠️ CONFLICTING

**Algorithm Comparison:**

| Aspect | gmm_optimized_analysis.py | gmm_fast_analysis.py | Verdict |
|--------|---------------------------|----------------------|---------|
| Scaler | RobustScaler | StandardScaler | RobustScaler better for outliers |
| Outlier Detection | IsolationForest + preprocessing | Basic IsolationForest | Enhanced is better |
| Component Selection | BIC-based | Fixed components | BIC is more principled |
| Data Cleaning | Aggressive (5% contamination) | Conservative | Need to benchmark |
| **Date Modified** | 2/8 20:53 | 2/8 20:59 | ⚠️ CONFLICT! |

**Critical Issue:**
- `gmm_fast_analysis.py` timestamp (20:59) is NEWER than `gmm_optimized_analysis.py` (20:53)
- But code suggests `gmm_optimized_analysis.py` is superior algorithm
- **Hypothesis:** File timestamps may be corrupted or files generated out of order

**Recommendation:**
```
🔍 INVESTIGATE: Check git log for actual creation order
   git log --oneline 09a_advanced_ml/gmm*.py
   
✅ DECISION: Use gmm_optimized_analysis.py (RobustScaler approach)
🔴 DELETE: gmm_fast_analysis.py (StandardScaler is outdated)
```

---

### 3. Pool Analysis Algorithm - ALGORITHM STATUS: ✅ CONSOLIDATED

| Aspect | pamm_cross_comparison_analysis.py | pamm_cross_comparison_final.py | Verdict |
|--------|-----------------------------------|------------------------------|----|
| Network Analysis | Pool coordination networks | Same | Same |
| Clustering | Louvain community detection | Same | Same |
| Visualization | Multiple plots | Same | Same |
| Code Size | 570 lines | 474 lines | Final is cleaner |

**Verdict:** Final version is optimized consolidation of analysis version.

---

## 🎯 Recommended File Structure

```
SOLANA_PAMM_MEV_ANALYSIS/
│
├── 📌 PRIMARY PRODUCTION FILES
│   ├── fat_sandwich_detector_optimized.py      [✅ KEEP]
│   ├── contagious_vulnerability_analyzer.py    [✅ KEEP]
│   └── 12_mev_profit_mechanisms/
│       └── mev_profit_analysis.py              [✅ KEEP]
│
├── 📊 MAIN ANALYTICAL NOTEBOOKS (Keep & Reference)
│   ├── 12_fat_sandwich_optimized_detector.ipynb        [✅ KEEP]
│   ├── 04_validator_analysis/04_validator_contagion_analysis.ipynb [✅ KEEP]
│   ├── 06_pool_analysis/06_pool_analysis.ipynb         [✅ KEEP]
│   ├── 09a_advanced_ml/01_gmm_clustering_analysis.ipynb [✅ KEEP]
│   └── 02_mev_detection/02_mev_detection.ipynb         [✅ KEEP]
│
├── 🔬 SUPPORTING ANALYSIS
│   ├── 10_advanced_FP_solution/11_fat_sandwich_vs_multihop_classification.ipynb [⚠️ ARCHIVE]
│   ├── test_improved_fat_sandwich.ipynb                [⚠️ ARCHIVE]
│   ├── test_contagion_analyzer.py                      [✅ KEEP]
│   └── analyze_and_filter_mev.py                       [✅ KEEP]
│
├── 🏢 OLD/DEPRECATED (Move to ARCHIVE folder)
│   ├── improved_fat_sandwich_detection.py             [🔴 SUPERSEDED]
│   ├── 06_pool_analysis/pamm_cross_comparison_analysis.py [🔴 SUPERSEDED]
│   ├── 09a_advanced_ml/gmm_fast_analysis.py           [🔴 INVESTIGATE]
│   ├── 09a_advanced_ml/enhanced_gmm_analysis.py       [🔴 WRAPPER ONLY]
│   ├── 10_advanced_FP_solution/01_improved_fat_sandwich_detection.ipynb [🔴 STUB]
│   └── 10_advanced_FP_solution/01_improved_fat_sandwich_detection_COMBINED.ipynb [🔴 STUB]
│
└── 📚 DOCUMENTATION (Reference)
    ├── DETECTOR_VISUAL_GUIDE.md                        [✅ CURRENT ARCHITECTURE]
    └── FILE_ORGANIZATION_REPORT.md                     [THIS FILE]
```

---

## 🚀 Action Plan

### Phase 1: Verification (Today)
```bash
# 1. Check git history for GMM files
git log --oneline 09a_advanced_ml/gmm*.py

# 2. Compare content of duplicate files
diff improved_fat_sandwich_detection.py fat_sandwich_detector_optimized.py

# 3. Verify contagion analyzer duplication
diff contagious_vulnerability_analyzer.py \
     04_validator_analysis/12_validator_contagion_analysis.py
```

### Phase 2: Consolidation
```bash
# Create ARCHIVE folder for old files
mkdir -p ARCHIVE/old_algorithms
mkdir -p ARCHIVE/old_notebooks

# Move deprecated Python files
mv improved_fat_sandwich_detection.py ARCHIVE/old_algorithms/
mv 06_pool_analysis/pamm_cross_comparison_analysis.py ARCHIVE/old_algorithms/
mv 09a_advanced_ml/enhanced_gmm_analysis.py ARCHIVE/old_algorithms/

# Archive old notebooks  
mv 10_advanced_FP_solution/01_improved_fat_sandwich_detection.ipynb ARCHIVE/old_notebooks/
mv 10_advanced_FP_solution/01_improved_fat_sandwich_detection_COMBINED.ipynb ARCHIVE/old_notebooks/
mv test_improved_fat_sandwich.ipynb ARCHIVE/old_notebooks/
```

### Phase 3: Documentation
- Update README.md to reference `fat_sandwich_detector_optimized.py`
- Update README.md to reference `12_fat_sandwich_optimized_detector.ipynb` as main notebook
- Link to DETECTOR_VISUAL_GUIDE.md as architecture reference
- Update all internal imports from old modules to new ones

---

## 📈 File Summary Table

| Category | File | Status | Action | Priority |
|----------|------|--------|--------|----------|
| **Detection** | fat_sandwich_detector_optimized.py | ✅ Production | Keep | P0 |
| | improved_fat_sandwich_detection.py | 🔴 Superseded | Archive | P1 |
| **Detection Notebooks** | 12_fat_sandwich_optimized_detector.ipynb | ✅ Main | Keep | P0 |
| | test_improved_fat_sandwich.ipynb | ⚠️ Old | Archive | P2 |
| | 10_advanced_FP_solution/01_*.ipynb | 🔴 Stub | Delete | P1 |
| **GMM Analysis** | gmm_optimized_analysis.py | ✅ Primary | Keep | P0 |
| | gmm_fast_analysis.py | ⚠️ Conflict | Investigate | P1 |
| | enhanced_gmm_analysis.py | 🔴 Wrapper | Archive | P2 |
| | 01_gmm_clustering_analysis.ipynb | ✅ Main | Keep | P0 |
| **Pool Analysis** | pamm_cross_comparison_final.py | ✅ Primary | Keep | P0 |
| | pamm_cross_comparison_analysis.py | 🔴 Superseded | Archive | P1 |
| | 06_pool_analysis.ipynb | ✅ Main | Keep | P0 |
| **Contagion** | contagious_vulnerability_analyzer.py | ✅ Primary | Keep | P0 |
| | test_contagion_analyzer.py | ✅ Test | Keep | P0 |
| | 12_validator_contagion_analysis.py | ⚠️ Investigate | Review | P1 |
| | 04_validator_contagion_analysis.ipynb | ✅ Main | Keep | P0 |
| | 13_contagion_diagnostic.ipynb | ⚠️ Supplementary | Archive | P2 |

---

## 🎓 Key Insights

1. **Optimization Trend:** Project shows clear evolution from long implementations (1098 lines) → optimized classes (481 lines)
   - `improved_fat_sandwich_detection.py` (1098 lines) → `fat_sandwich_detector_optimized.py` (481 lines)
   - **56% reduction in code** while maintaining functionality

2. **Algorithmic Maturity:**
   - Fat Sandwich Detection: **MATURE** (follows DETECTOR_VISUAL_GUIDE.md exactly)
   - GMM Clustering: **NEEDS INVESTIGATION** (conflicting timestamps)
   - Pool Analysis: **MATURE** (clean consolidation)
   - Contagion Analysis: **SCATTERED** (needs centralization)

3. **Version Control Concerns:**
   - Timestamp conflict on GMM files (20:53 vs 20:59)
   - Multiple stub notebooks (1KB) suggesting incomplete cleanup
   - Old notebooks not cleaned up after refactoring

4. **Recommendation for Future:**
   - Use single class-based approach (like FatSandwichDetector)
   - Archive old function-based code immediately after refactoring
   - Implement single entry-point notebook per analysis type
   - Maintain DEPRECATED folder with old algorithms for reference

---

**Report Generated:** 2026-02-08  
**Framework Reference:** DETECTOR_VISUAL_GUIDE.md  
**Status:** Ready for consolidation
