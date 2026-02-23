# Validator-AMM Risk Analysis with Mitigation Framework

**Analysis Date:** February 11, 2026
**Dataset:** 617 Fat Sandwich Cases
**Cross-Reference:** VALIDATOR_CONTAGION_FRAMEWORK.md

## Executive Summary

- **Total Validator-AMM Pairs:** 344
- **Top 20 Pairs Account For:** 117 cases (19.0% of total) and 70.28 SOL (62.5% of profit)
- **Concentration Ratio:** Top 20 pairs = 19.0% of attack surface
- **Recommended Focus:** Target top 20 pairs first for maximum impact

## Top 20 Highest-Risk Validator-AMM Pairs

| Rank | Validator | AMM | Cases | Total Profit | Avg Profit | Attackers | Risk Score | Recommendation |
|------|-----------|-----|-------|--------------|------------|-----------|------------|----------------|
| 1 | HEL1USMZKAL2odpN... | HumidiFi | 15 | 10.476 | 0.6984 | 15 | 142.3 | CRITICAL |
| 2 | 22rU5yUmdVThrkoP... | HumidiFi | 2 | 13.725 | 6.8625 | 2 | 142.2 | CRITICAL |
| 3 | DRpbCBMxVnDK7maP... | HumidiFi | 8 | 6.822 | 0.8528 | 8 | 88.2 | HIGH |
| 4 | HnfPZDrbJFooiP9v... | HumidiFi | 4 | 7.110 | 1.7775 | 4 | 81.1 | HIGH |
| 5 | FNKgX9dYUhYQFRTM... | HumidiFi | 7 | 5.427 | 0.7753 | 7 | 71.8 | HIGH |
| 6 | ChorusmmK7i1AxXe... | HumidiFi | 4 | 3.861 | 0.9652 | 4 | 48.6 | MEDIUM |
| 7 | Fd7btgySsrjuo25C... | HumidiFi | 10 | 1.890 | 0.1890 | 10 | 43.9 | MEDIUM |
| 8 | HEL1USMZKAL2odpN... | BisonFi | 13 | 1.098 | 0.0845 | 13 | 43.5 | MEDIUM |
| 9 | DRpbCBMxVnDK7maP... | SolFiV2 | 11 | 1.062 | 0.0965 | 11 | 38.1 | MEDIUM |
| 10 | 5pPRHniefFjkiaAr... | HumidiFi | 3 | 2.934 | 0.9780 | 3 | 36.8 | MEDIUM |
| 11 | 9W3QTgBhkU4Bwg6c... | HumidiFi | 7 | 1.602 | 0.2289 | 7 | 33.5 | MEDIUM |
| 12 | DRpbCBMxVnDK7maP... | TesseraV | 8 | 1.107 | 0.1384 | 8 | 31.1 | MEDIUM |
| 13 | 6TkKqq15wXjqEjNg... | HumidiFi | 2 | 2.601 | 1.3005 | 2 | 31.0 | MEDIUM |
| 14 | EvnRmnMrd69kFdbL... | SolFiV2 | 3 | 2.196 | 0.7320 | 3 | 29.5 | MEDIUM |
| 15 | CiR8HNCfkjtcongP... | BisonFi | 2 | 2.187 | 1.0935 | 2 | 26.9 | MEDIUM |
| 16 | A1vqhA2fS6K7CvHs... | HumidiFi | 2 | 1.845 | 0.9225 | 2 | 23.4 | MEDIUM |
| 17 | ChorusmmK7i1AxXe... | GoonFi | 5 | 0.954 | 0.1908 | 5 | 22.0 | MEDIUM |
| 18 | Fd7btgySsrjuo25C... | BisonFi | 6 | 0.576 | 0.0960 | 6 | 20.8 | MEDIUM |
| 19 | 4SsMncJdtKiUcDtu... | HumidiFi | 2 | 1.575 | 0.7875 | 2 | 20.8 | MEDIUM |
| 20 | JD549HsbJHeEKKUr... | HumidiFi | 3 | 1.233 | 0.4110 | 3 | 19.8 | MEDIUM |

## Risk Categories

### CRITICAL Risk (2 pairs)
**Definition:** Risk score > 100 (multiple high cases OR very high profit concentration)

- **HEL1USMZKAL2odpNBj2o... + HumidiFi:** 15 cases, 10.476 SOL
- **22rU5yUmdVThrkoPieVN... + HumidiFi:** 2 cases, 13.725 SOL

### HIGH Risk (3 pairs)
**Definition:** Risk score 50-100 (significant attack frequency)
- Total cases in HIGH risk category: 19
- Total profit from HIGH risk: 19.36 SOL

### MEDIUM Risk (14 pairs)
**Definition:** Risk score 20-50 (occasional exploitation)
- Total cases in MEDIUM risk: 78

## Validator Concentration (Contagion Risk)

**Top Validators Enabling Contagion (hitting multiple AMMs):**

| Rank | Validator | Cases | AMMs Hit | Profit | Contagion Severity |
|------|-----------|-------|----------|--------|-------------------|
| 1 | HEL1USMZKAL2odpN... | 37 | 6 | 11.727 | CRITICAL |
| 2 | DRpbCBMxVnDK7maP... | 28 | 4 | 9.045 | HIGH |
| 3 | Fd7btgySsrjuo25C... | 22 | 6 | 3.105 | CRITICAL |
| 4 | DtdSSG8ZJRZVv5Jx... | 17 | 6 | 2.538 | CRITICAL |
| 5 | ChorusmmK7i1AxXe... | 16 | 4 | 5.247 | HIGH |
| 6 | 9W3QTgBhkU4Bwg6c... | 15 | 5 | 2.205 | CRITICAL |
| 7 | 9jxgosAfHgHzwnxs... | 14 | 4 | 0.549 | HIGH |
| 8 | 9UM8wQ8F5oMiRcP5... | 12 | 4 | 0.693 | HIGH |
| 9 | CAo1dCGYrB6NhHh5... | 12 | 5 | 1.746 | CRITICAL |
| 10 | Hz5aLvpKScNWoe9Y... | 12 | 4 | 0.999 | HIGH |

## Protocol Vulnerability Ranking (from Validator-AMM Perspective)

| Protocol | Cases | Total Profit | Unique Validators | Avg Profit/Case | Risk Level |
|----------|-------|--------------|-------------------|-----------------|----------|
| HumidiFi | 167 | 75.11 | 83 | 0.4497 | CRITICAL |
| BisonFi | 111 | 11.23 | 56 | 0.1012 | HIGH |
| GoonFi | 101 | 7.88 | 58 | 0.0781 | HIGH |
| TesseraV | 93 | 7.83 | 58 | 0.0842 | HIGH |
| SolFiV2 | 95 | 7.50 | 55 | 0.0789 | HIGH |
| ZeroFi | 47 | 2.77 | 33 | 0.0590 | HIGH |
| ObricV2 | 3 | 0.11 | 1 | 0.0360 | MEDIUM |

## Mitigation Strategies Applied to High-Risk Pairs

### Slot-Level MEV Filtering

**Priority:** HIGHEST
**Expected Impact:** 60-70% reduction
**Implementation Effort:** MEDIUM
**How It Works:** Reject non-Jito bundles during high-MEV slots

**Best Applied To (9 pairs):**
- HEL1USMZKAL2odpN... + HumidiFi: 15 cases, 10.476 SOL
- DRpbCBMxVnDK7maP... + HumidiFi: 8 cases, 6.822 SOL
- FNKgX9dYUhYQFRTM... + HumidiFi: 7 cases, 5.427 SOL
- Fd7btgySsrjuo25C... + HumidiFi: 10 cases, 1.890 SOL
- HEL1USMZKAL2odpN... + BisonFi: 13 cases, 1.098 SOL
- ... and 4 more

### TWAP-Based Oracle Updates

**Priority:** HIGH
**Expected Impact:** 50-60% reduction
**Implementation Effort:** MEDIUM
**How It Works:** Aggregate prices over 12 slots with randomized timing

**Best Applied To (12 pairs):**
- HEL1USMZKAL2odpN... + HumidiFi: 15 cases, 10.476 SOL
- DRpbCBMxVnDK7maP... + HumidiFi: 8 cases, 6.822 SOL
- HnfPZDrbJFooiP9v... + HumidiFi: 4 cases, 7.110 SOL
- FNKgX9dYUhYQFRTM... + HumidiFi: 7 cases, 5.427 SOL
- ChorusmmK7i1AxXe... + HumidiFi: 4 cases, 3.861 SOL
- ... and 7 more

### Commit-Reveal Transactions

**Priority:** MEDIUM
**Expected Impact:** 80-90% reduction
**Implementation Effort:** HIGH
**How It Works:** Two-phase protocol: hide intent in phase 1, reveal in phase 2

**Best Applied To (10 pairs):**
- HEL1USMZKAL2odpN... + HumidiFi: 15 cases, 10.476 SOL
- 22rU5yUmdVThrkoP... + HumidiFi: 2 cases, 13.725 SOL
- DRpbCBMxVnDK7maP... + HumidiFi: 8 cases, 6.822 SOL
- HnfPZDrbJFooiP9v... + HumidiFi: 4 cases, 7.110 SOL
- FNKgX9dYUhYQFRTM... + HumidiFi: 7 cases, 5.427 SOL
- ... and 5 more

### Validator Diversity Routing

**Priority:** ONGOING
**Expected Impact:** 20-30% reduction
**Implementation Effort:** LOW
**How It Works:** Route large trades to non-hotspot validators

**Best Applied To (5 pairs):**
- HEL1USMZKAL2odpN... (hits 6 AMMs, 37 cases)
- DRpbCBMxVnDK7maP... (hits 4 AMMs, 28 cases)
- Fd7btgySsrjuo25C... (hits 6 AMMs, 22 cases)
- DtdSSG8ZJRZVv5Jx... (hits 6 AMMs, 17 cases)
- ChorusmmK7i1AxXe... (hits 4 AMMs, 16 cases)

## Prioritized Implementation Roadmap

### Phase 1 (Immediate - Week 1-2)
**Target:** CRITICAL risk pairs (2 pairs)

1. **Deploy Validator Diversity Routing** (LOW effort)
   - Route large trades away from HEL1US and DRpbCBMxVnDK
   - Expected: 20-30% reduction in top-2 validator attacks

2. **Monitor Slot-Level MEV Patterns** (prep work)
   - Instrument validators for high-MEV slot detection
   - Collect baseline data for filtering thresholds

### Phase 2 (Near-term - Week 3-4)
**Target:** HIGH risk pairs (3 pairs)

1. **Enable Slot-Level MEV Filtering** (MEDIUM effort)
   - Implement on baseline validators (non-critical)
   - Expected: 60-70% reduction in coordinated attacks

2. **Coordinate TWAP Oracle Upgrades** (MEDIUM effort)
   - Start with HumidiFi (most vulnerable protocol)
   - Expected: 50-60% reduction in oracle-based attacks

### Phase 3 (Medium-term - Month 2)
**Target:** MEDIUM risk pairs (14 pairs)

1. **Implement Commit-Reveal for High-Value Trades** (HIGH effort)
   - Start with optional user opt-in
   - Expected: 80-90% reduction in sandwich attacks

2. **Cross-Protocol Coordination** (prep)
   - Align on consistent MEV filtering standards
   - Share attacker intelligence

## Projected Risk Reduction

| Phase | Implementation | Estimated Attack Reduction | Residual Risk |
|-------|-----------------|----------------------------|-----------|
| 0 (Baseline) | None | 0% | 100% |
| 1 | Validator Diversity | 20-30% | 70-80% |
| 2 | + Slot Filtering + TWAP | 60-75% | 25-40% |
| 3 | + Commit-Reveal (opt-in) | 75-90% | 10-25% |

## Conclusion

The top 20 validator-AMM pairs represent **19.0% of attack surface** (117 cases) and **62.5% of extracted MEV** (70.28 SOL).

**Recommended Action:** Focus mitigation efforts on the CRITICAL and HIGH risk pairs first.

**Key Insight:** Contagion is enabled by validator concentration (HEL1US processes 6% of fat sandwiches).
Reducing reliance on hotspot validators will have multiplicative downstream effects across all AMM pairs.

**Next Step:** Cross-reference specific protocols (e.g., HumidiFi) with their developer teams to coordinate TWAP oracle implementations on priority validators.
