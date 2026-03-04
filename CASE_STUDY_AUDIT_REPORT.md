# Case Study Data Consistency Audit Report
**Date:** March 4, 2026  
**Status:** ✅ VALIDATION PASSED

## Summary

Comprehensive audit and fix of case study data inconsistencies across all report sources. All data now synchronized with canonical JSON source.

## Issues Found and Fixed

### Case 1 (JUP/WSOL Launch Attack)

**Python Dashboard Issues:**
- ❌ Profit: 0.571 SOL → ✅ Fixed to **3.185 SOL**
- ❌ ROI: 285% → ✅ Fixed to **91%**
- ❌ Duration: 189ms → ✅ Fixed to **800ms**
- ❌ Wrong timeline data → ✅ Fixed with canonical JSON data

**HTML Report Issues:**
- ❌ Profit metric: 0.571 SOL → ✅ Fixed to **3.185 SOL**
- ❌ ROI metric: 285% → ✅ Fixed to **91%**
- ❌ Duration: 189ms → ✅ Fixed to **800ms**
- ❌ Victim loss: $25.3K → ✅ Fixed to **0.225 SOL**
- ❌ Wrong attack timeline → ✅ Replaced with canonical attack sequence

### Case 2 (PYTH/WSOL Oracle Lag Exploitation)

**Python Dashboard Issues:**
- ❌ Wrong attacker: AEB9dXBoxkrapNd59Kg29JefMMf3M1WLcNA12XjKSf4R → ✅ Fixed to **YubVwWeg1vHFr17Q7HQQETcke7sFvMabqU8wbv8NXQW**
- ❌ Wrong victim action: "800K PYTH buy" → ✅ Fixed to **"750K WSOL → PYTH (stake pool deposit)"**
- ❌ Profit: 3.312 SOL → ✅ Fixed to **2.856 SOL**
- ❌ ROI: 552% → ✅ Fixed to **102%**
- ❌ Wrong attack type: "Multi-slot LP" → ✅ Fixed to **"Oracle Lag Sandwich"**
- ❌ Duration: 2.4 seconds → ✅ Fixed to **600ms**

**HTML Report Issues:**
- ❌ Title: "Multi-Slot Sandwich + LP Strategy" → ✅ Fixed to **"Oracle Lag Exploitation"**
- ❌ Wrong victim trade: "1.2M PYTH → WSOL" → ✅ Fixed to **"750K WSOL → PYTH"**
- ❌ Profit: 3.312 SOL → ✅ Fixed to **2.856 SOL**
- ❌ ROI: 552% → ✅ Fixed to **102%**
- ❌ Duration: 2.4s → ✅ Fixed to **600ms**
- ❌ Victim loss: $146.8K → ✅ Fixed to **0.246 SOL**
- ❌ Wrong multi-slot LP narrative → ✅ Replaced with **oracle lag attack mechanics**

**Summary Table Issues:**
- ❌ Case 1 row: wrong profit/ROI/duration → ✅ Fixed
- ❌ Case 2 row: wrong profit/ROI/duration/type → ✅ Fixed
- ❌ Total row: aggregates wrong → ✅ Fixed

## Canonical Data (from JSON source)

### CASE-001-460701000: JUP/WSOL Launch Period Flash Crash Extraction
- **Token Pair:** JUP/WSOL
- **Attacker:** YubQzu18FDqJRyNfG8JqHmsdbxhnoQqcKUHBdUkN6tP
- **Attack Type:** fat_sandwich
- **Duration:** 800ms
- **Victim Action:** Buy 500,000 JUP tokens with USDC/WSOL
- **Victim Loss:** 0.225 SOL (225 JUP slippage)
- **Gross Profit:** 3.245 SOL
- **Net Profit:** **3.185 SOL**
- **ROI:** **91%**

### CASE-002-461628000: PYTH/WSOL Oracle Lag Exploitation
- **Token Pair:** PYTH/WSOL
- **Attacker:** YubVwWeg1vHFr17Q7HQQETcke7sFvMabqU8wbv8NXQW
- **Attack Type:** sandwich (oracle lag)
- **Duration:** 600ms
- **Victim Action:** Deposit for stake pool (750K WSOL → PYTH)
- **Victim Loss:** 0.246 SOL (30K PYTH slippage)
- **Gross Profit:** 2.916 SOL
- **Net Profit:** **2.856 SOL**
- **ROI:** **102%**

### CASE-003-463311000: SOL/USDC Critical Liquidity Drain Attack
- **Token Pair:** SOL/USDC
- **Attacker:** AEB9dXBoxkrapNd59Kg29JefMMf3M1WLcNA12XjKSf4R
- **Attack Type:** liquidity_drain_sandwich
- **Duration:** 520ms
- **Victim Action:** Withdraw from lending protocol (1000 SOL → USDC)
- **Victim Loss:** 18,200 USDC
- **Gross Profit:** 8.243 SOL
- **Net Profit:** **8.183 SOL**
- **ROI:** **125.89%**

## Files Modified

1. **✅ app/attack_case_studies.py**
   - Fixed case1_overview (profit, ROI, duration)
   - Fixed case1_timeline (attack sequence)
   - Fixed case1_financials (profit breakdown)
   - Fixed case2_overview (attacker, type, profit, ROI, duration)
   - Fixed case2_timeline (victim action, amounts)
   - Fixed case2_financials (profit breakdown)
   - Fixed comparative_summary table
   - Fixed validator_analysis table

2. **✅ index.html**
   - Fixed Case 1 metrics section (profit, ROI, duration, victim loss)
   - Fixed Case 1 attack breakdown narrative
   - Fixed Case 2 title and metrics (profit, ROI, duration, victim loss)
   - Fixed Case 2 victim trade description (1.2M PYTH → 750K WSOL)
   - Fixed Case 2 attack mechanics (removed wrong multi-slot LP narrative)
   - Fixed summary table rows for Case 1 and Case 2

3. **✅ validate_case_studies.py** (NEW)
   - Created automated validation script
   - Compares all sources against canonical JSON
   - Detects profit, ROI, attacker, victim action mismatches
   - Returns exit code 0 on success, 1 on failure

## Validation Results

```
✅ VALIDATION PASSED

- Case 1 profit matches: 3.185 SOL ✅
- Case 1 ROI matches: 91% ✅
- Case 2 attacker corrected ✅
- Case 2 victim action corrected ✅
- Case 2 profit matches: 2.856 SOL ✅
- Case 2 ROI matches: 102% ✅
```

## Root Cause Analysis

The inconsistencies arose from:

1. **Multiple data entry points:** Case studies were manually created in Python, HTML, and academic report generator without centralized validation
2. **Confusion between different attack scenarios:** Case 2 data was mixed with a hypothetical multi-slot LP attack that doesn't exist in the canonical JSON
3. **WSOL confusion:** "1.2k WSOL = 0.8 SOL" was actually mixing "1.2M PYTH tokens" with "0.8 WSOL fees" from different parts of a non-existent narrative
4. **No automated validation:** Changes to JSON source weren't propagated to other files

## Prevention Measures Implemented

1. **✅ Validation Script:** Created `validate_case_studies.py` to automatically check consistency
2. **✅ Canonical Source:** Established `outputs/mev_attack_case_studies.json` as single source of truth
3. **✅ Documentation:** This report documents the canonical data structure
4. **⚠️ Recommended:** Add CI/CD check to run validation before deployments
5. **⚠️ Recommended:** Generate reports from JSON programmatically rather than manual entry

## Next Steps

To prevent future inconsistencies:

1. Run `python validate_case_studies.py` before any deployment
2. Update JSON source first, then regenerate all reports
3. Consider creating a report generator that reads from JSON automatically
4. Add the validation script to your deployment pipeline

## Commands to Verify

```bash
# Run validation
python validate_case_studies.py

# Should output: ✅ VALIDATION PASSED
```
