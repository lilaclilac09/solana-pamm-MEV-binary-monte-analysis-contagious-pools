#  PROJECT FILE ORGANIZATION VISUAL GUIDE

**Based On:** DETECTOR_VISUAL_GUIDE.md Architecture  
**Status:** Duplicate Inventory Complete  
**Date:** February 8, 2026

---

## ️ ARCHITECTURE OVERVIEW

### Production Pipeline (CURRENT)

```
┌─────────────────────────────────────────────────────┐
│         DATA CLEANING & PREPARATION                │
│  • 01_data_cleaning/                               │  
│  • 01a_data_cleaning_DeezNode_filters/             │
│  • 01b_jito_tip_filter/                            │
└──────────────┬──────────────────────────────────────┘
               ↓
┌─────────────────────────────────────────────────────┐
│         MEV DETECTION                              │
│   02_mev_detection.ipynb                         │
│   Core: fat_sandwich_detector_optimized.py       │
│      KEEP - Unified detector class               │
│   DELETE: improved_fat_sandwich_detection.py     │
│     (1098 lines, pre-optimization)                 │
└──────────────┬──────────────────────────────────────┘
               ↓
┌─────────────────────────────────────────────────────┐
│         ANALYSIS & CLASSIFICATION                  │
│   12_fat_sandwich_optimized_detector.ipynb       │ ← MAIN NOTEBOOK
│      KEEP - Latest (2/8 21:39, 31K)             │
│   KEEP supplementary notebooks:                  │
│     • 10_advanced_FP_solution/11_...classification │
│     • 04_validator_contagion_analysis.ipynb        │
└──────────────┬──────────────────────────────────────┘
               ↓
┌─────────────────────────────────────────────────────┐
│         ADVANCED ANALYSIS                          │
│   06_pool_analysis.ipynb                         │
│   Core: pamm_cross_comparison_final.py           │
│      KEEP - Clean final version (474 lines)      │
│   DELETE: pamm_cross_comparison_analysis.py      │
│     (570 lines, superseded version)                │
│                                                    │
│   09a_advanced_ml/01_gmm_clustering_analysis.ipynb
│   Core: gmm_optimized_analysis.py                │
│      KEEP - RobustScaler approach (320 lines)    │
│   INVESTIGATE: gmm_fast_analysis.py              │
│     (345 lines, timestamp conflict 20:59)          │
│   DELETE: enhanced_gmm_analysis.py               │
│     (95 lines, wrapper function only)              │
└──────────────┬──────────────────────────────────────┘
               ↓
┌─────────────────────────────────────────────────────┐
│         VULNERABILITY ANALYSIS                     │
│   04_validator_contagion_analysis.ipynb          │
│   Core: contagious_vulnerability_analyzer.py     │
│      KEEP - Active primary class (601 lines)     │
│      Used by: test_contagion_analyzer.py         │
│   ARCHIVE: 04_validator_analysis/12_...analysis.py
│     (1080 lines, old implementation)               │
└──────────────┬──────────────────────────────────────┘
               ↓
┌─────────────────────────────────────────────────────┐
│         PROFIT ANALYSIS                            │
│   12_mev_profit_mechanisms/                      │
│   Core: mev_profit_analysis.py                   │
│      KEEP                                         │
└──────────────┬──────────────────────────────────────┘
               ↓
┌─────────────────────────────────────────────────────┐
│         REPORTS & DOCUMENTATION                    │
│   README_OPTIMIZATION_COMPLETE.md                │
│   DETECTOR_VISUAL_GUIDE.md                       │
│   FILE_ORGANIZATION_REPORT.md                    │
│   CLEANUP_CHECKLIST.md                           │
└─────────────────────────────────────────────────────┘
```

---

##  CURRENT FILE STATE MATRIX

### Section 02: MEV Detection

```
STATUS: Core algorithm optimized, old version identified

┌─────────────────────────────────────────────────────────┐
│ RECOMMENDED STRUCTURE                                  │
├─────────────────────────────────────────────────────────┤
│  fat_sandwich_detector_optimized.py (481 lines)       │
│    └─ Used by: 12_fat_sandwich_optimized_detector.ipynb│
│    └─ Algorithm: A-B-A pattern detection               │
│    └─ Status: PRODUCTION READY                         │
├─────────────────────────────────────────────────────────┤
│  improved_fat_sandwich_detection.py (1098 lines)      │
│    └─ Status: SUPERSEDED - ARCHIVE TO:                │
│       ARCHIVE/old_algorithms/                          │
│    └─ Replaced by: FatSandwichDetector class            │
├─────────────────────────────────────────────────────────┤
│  12_fat_sandwich_optimized_detector.ipynb (31K, NEW) │
│    └─ Last Modified: 2/8/26 21:39                      │
│    └─ Status: PRIMARY NOTEBOOK - KEEP                 │
│    └─ Does: Interactive detection & analysis           │
├─────────────────────────────────────────────────────────┤
│  10_advanced_FP_solution/01_improved_...ipynb (1KB)  │
│    └─ Status: STUB NOTEBOOK - ARCHIVE                 │
│    └─ Reason: Content moved to 12_ notebook            │
└─────────────────────────────────────────────────────────┘

ALGORITHM GENEALOGY:
improved_fat_sandwich_detection.py (old function-based)
         ↓ REFACTORED INTO ↓
FatSandwichDetector (class-based in optimized.py)
         ↓ USED BY ↓
12_fat_sandwich_optimized_detector.ipynb (reference implementation)
```

### Section 06: Pool Analysis

```
STATUS: Clean consolidation, older version identified

┌─────────────────────────────────────────────────────────┐
│ RECOMMENDED STRUCTURE                                  │
├─────────────────────────────────────────────────────────┤
│  pamm_cross_comparison_final.py (474 lines)          │
│    └─ Status: PRIMARY - KEEP                          │
│    └─ Algorithm: Network analysis, Louvain clustering   │
│    └─ Code Reduction: 96 lines shorter than analysis   │
├─────────────────────────────────────────────────────────┤
│  pamm_cross_comparison_analysis.py (570 lines)       │
│    └─ Status: SUPERSEDED - ARCHIVE TO:                │
│       ARCHIVE/old_algorithms/                          │
│    └─ Reason: Final version is cleaner optimization    │
├─────────────────────────────────────────────────────────┤
│  06_pool_analysis.ipynb (150K)                       │
│    └─ Status: PRIMARY NOTEBOOK - KEEP                 │
│    └─ Uses: pamm_cross_comparison_final.py             │
└─────────────────────────────────────────────────────────┘

EVOLUTION:
pamm_cross_comparison_analysis.py (570 lines)
         ↓ OPTIMIZED TO ↓
pamm_cross_comparison_final.py (474 lines) [96 line reduction!]
         ↓ USED BY ↓
06_pool_analysis.ipynb
```

### Section 09a: Advanced ML / GMM Clustering

```
STATUS: ️ ALGORITHM CONFLICT - REQUIRES INVESTIGATION

┌─────────────────────────────────────────────────────────┐
│ TIMESTAMP ANOMALY DETECTED                            │
│                                                        │
│ gmm_optimized_analysis.py   | Modified: 2/8 20:53     │
│ gmm_fast_analysis.py        | Modified: 2/8 20:59     │
│                                                        │
│ BUT: gmm_fast (newer) uses old StandardScaler         │
│      gmm_optimized (older) uses superior RobustScaler │
└─────────────────────────────────────────────────────────┘

CURRENT CONFLICT:
┌─────────────────────────────────────────────────────────┐
│  gmm_optimized_analysis.py (320 lines, 20:53)        │
│    Preprocessing:                                      │
│    • RobustScaler  (better for outliers)             │
│    • IsolationForest                                   │
│    • Feature engineering optimized                     │
│    Status: RECOMMENDED AS PRIMARY                      │
├─────────────────────────────────────────────────────────┤
│  gmm_fast_analysis.py (345 lines, 20:59)             │
│    Preprocessing:                                      │
│    • StandardScaler  (sensitive to outliers)         │
│    • Basic IsolationForest                             │
│    • Standard approach                                 │
│    Status: CONFLICTING - DELETE or INVESTIGATE        │
├─────────────────────────────────────────────────────────┤
│  enhanced_gmm_analysis.py (95 lines, 11:39)          │
│    Content: def enhanced_gmm_clustering_analysis()     │
│    Type: Wrapper function with Chinese comments        │
│    Status: DELETE - not standalone                     │
├─────────────────────────────────────────────────────────┤
│  01_gmm_clustering_analysis.ipynb                     │
│    Status: MAIN NOTEBOOK - KEEP                       │
└─────────────────────────────────────────────────────────┘

RESOLUTION NEEDED:
[ ] Step 1: git log 09a_advanced_ml/gmm*.py
[ ] Step 2: Compare performance (benchmark)
[ ] Step 3: Decision:
    [A] gmm_optimized_analysis.py is superior?
        → DELETE gmm_fast_analysis.py
    [B] gmm_fast_analysis.py has new optimization?
        → Rename & document
    [C] Unclear?
        → ARCHIVE both, use notebook version
```

### Section 04: Validator/Contagion Analysis

```
STATUS: Two competing implementations - needs consolidation

┌─────────────────────────────────────────────────────────┐
│ PRIMARY IMPLEMENTATION                                │
├─────────────────────────────────────────────────────────┤
│  contagious_vulnerability_analyzer.py (601 lines)     │
│    Class: ContagiousVulnerabilityAnalyzer              │
│    Status: ACTIVE - Used by test_contagion_analyzer.py │
│    Methods:                                            │
│    • load_mev_data()                                   │
│    • identify_trigger_pool()                           │
│    • analyze_cascade_rates()                           │
│    • generate_contagion_report()                       │
├─────────────────────────────────────────────────────────┤
│  test_contagion_analyzer.py (71 lines)                │
│    Status: TEST HARNESS - KEEP                        │
│    Imports: contagious_vulnerability_analyzer          │
│    Tests: Main analyzer functionality                  │
├─────────────────────────────────────────────────────────┤
│ OLD IMPLEMENTATION (ARCHIVE)                           │
├─────────────────────────────────────────────────────────┤
│ ️ 04_validator_analysis/12_validator_contagion_analysis.py
│    Class: ValidatorContagionAnalyzer                   │
│    Lines: 1080 (much larger)                           │
│    Status: OLD - ARCHIVE TO:                          │
│             ARCHIVE/validator_analysis_old/            │
│    Reason: NOT used by active test harness            │
│    Note: 04_validator_analysis notebooks might use it │
├─────────────────────────────────────────────────────────┤
│  04_validator_contagion_analysis.ipynb               │
│    Status: MAIN NOTEBOOK - KEEP                       │
│    ️ TODO: Verify which analyzer it uses             │
│             Update if using old version               │
└─────────────────────────────────────────────────────────┘

ACTION REQUIRED:
[ ] Check 04_validator_contagion_analysis.ipynb:
    Does it import contagious_vulnerability_analyzer
    OR 04_validator_analysis/12_validator_contagion_analysis.py?
    
[ ] If uses old version:
    Update to use contagious_vulnerability_analyzer (active)
```

---

##  QUICK DECISION MATRIX

### For Each Duplicate, Decide:

```
┌──────────────────────────────────────────────────────────────┐
│ DUPLICATE FOUND: File A vs File B                           │
├──────────────────────────────────────────────────────────────┤
│ Q1: Used by production notebook?                            │
│     Yes (A) ────→ KEEP A, Archive B                         │
│     Yes (B) ────→ KEEP B, Archive A                         │
│     Neither ────→ Archive both                              │
│                                                              │
│ Q2: Which has newer algorithm/optimization?                 │
│     Timestamps:  A=20:53, B=20:59                           │
│     Algorithm:   A=RobustScaler, B=StandardScaler        │
│     Verdict:     KEEP A despite older timestamp             │
│                                                              │
│ Q3: Code quality / size?                                    │
│     A=320 lines, B=345 lines                            │
│     A=RobustScaler, B=StandardScaler                     │
│     Verdict:     KEEP A                                      │
│                                                              │
│ DECISION: Archive B, Keep A                                 │
└──────────────────────────────────────────────────────────────┘
```

---

##  FILE CONSOLIDATION SUMMARY

### Count by Section

```
┌─────────────────────────────────────────────────────┐
│ SECTION                  KEEP  ARCHIVE  DELETE      │
├─────────────────────────────────────────────────────┤
│ Fat Sandwich Detection    2      1        1         │
│ GMM Clustering            1      2        1         │
│ Pool Analysis             2      1        0         │
│ Contagion/Validator       2      2        0         │
│ Supporting Scripts        3      0        0         │
│ Notebooks (Total)        12      8        0         │
├─────────────────────────────────────────────────────┤
│ TOTAL                    22     14        2         │
│                                                     │
│  Production Files       22                        │
│  Archive/Reference      14                        │
│ ️ Can Delete             2                        │
└─────────────────────────────────────────────────────┘
```

---

##  IMPLEMENTATION ROADMAP

### Phase 1️⃣: Immediate (Obvious Duplicates)

**DELETE (No Loss):**
- [ ] improved_fat_sandwich_detection.py → replaced by FatSandwichDetector class
- [ ] enhanced_gmm_analysis.py → wrapper only
- [ ] 10_advanced_FP_solution/01_improved_*.ipynb → 1KB stubs

**ARCHIVE (Safe):**
- [ ] 06_pool_analysis/pamm_cross_comparison_analysis.py → final version exists
- [ ] 04_validator_analysis/12_validator_contagion_analysis.py → old version

### Phase 2️⃣: Investigation (Timestamp Conflicts)

**INVESTIGATE FIRST:**
```bash
# 1. Check git history
git log --oneline 09a_advanced_ml/gmm_optimized_analysis.py
git log --oneline 09a_advanced_ml/gmm_fast_analysis.py

# 2. Compare preprocessing
grep -A 10 "Scaler\|IsolationForest" 09a_advanced_ml/gmm*.py

# 3. Benchmark both
python3 << 'EOF'
# Compare execution time
import time
from gmm_optimized_analysis import *
from gmm_fast_analysis import *
# ... benchmark ...
EOF

# 4. DECIDE:
#    A) gmm_optimized is better → DELETE gmm_fast
#    B) gmm_fast is faster → KEEP both with clear naming
#    C) Unclear → ARCHIVE both
```

### Phase 3️⃣: Verification (Cross-dependencies)

**VERIFY:**
1. [ ] 04_validator_contagion_analysis.ipynb uses contagious_vulnerability_analyzer.py
2. [ ] 06_pool_analysis.ipynb uses pamm_cross_comparison_final.py
3. [ ] 12_fat_sandwich_optimized_detector.ipynb uses fat_sandwich_detector_optimized.py

---

##  SUCCESS CRITERIA

When consolidation is complete:

- [ ] **Single Implementation Per Algorithm**
  - One FatSandwichDetector class (not function-based version)
  - One active GMM implementation
  - One Pool Analysis script (final version)
  - One Contagion Analyzer (active)

- [ ] **Clear Entry Points**
  - 12_fat_sandwich_optimized_detector.ipynb → Fat Sandwich analysis
  - 06_pool_analysis.ipynb → Pool coordination
  - 04_validator_contagion_analysis.ipynb → Validator analysis
  - 09a_advanced_ml/01_gmm_clustering_analysis.ipynb → GMM analysis

- [ ] **No Broken Imports**
  - All notebooks execute without import errors
  - All imports point to production (not archived) files

- [ ] **Documentation Updated**
  - README.md references primary files
  - DETECTOR_VISUAL_GUIDE.md matches actual implementation
  - ARCHIVE/README.md created with rationale

- [ ] **Archive Organized**
  - All old files in ARCHIVE/ with clear structure
  - Backup zip created before any changes
  - Deletion log maintained

---

##  References

1. **Architecture:** [DETECTOR_VISUAL_GUIDE.md](DETECTOR_VISUAL_GUIDE.md)
2. **File Details:** [FILE_ORGANIZATION_REPORT.md](FILE_ORGANIZATION_REPORT.md)
3. **Action Items:** [CLEANUP_CHECKLIST.md](CLEANUP_CHECKLIST.md)
4. **This Guide:** FILE_ORGANIZATION_VISUAL_GUIDE.md

---

**Status:**  Analysis Complete - Ready to Execute Cleanup  
**Priority:** P1 (Affects code maintainability)  
**Estimated Time:** 60 minutes
