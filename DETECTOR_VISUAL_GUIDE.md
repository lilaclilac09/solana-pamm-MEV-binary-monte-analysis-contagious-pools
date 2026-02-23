# Fat Sandwich Detector - Quick Visual Guide

## 🎯 What It Does

```
                            INPUT DATA (df_clean)
                                    ↓
                        [TRADE Events Only]
                                    ↓
                   ┌─────────────────────────────┐
                   │  FatSandwichDetector()     │
                   │  • Initialize with trades  │
                   │  • Set parameters          │
                   └────────────┬────────────────┘
                                ↓
                   ┌─────────────────────────────┐
                   │ detect_fat_sandwiches()    │
                   │ • Rolling time windows     │
                   │ • A-B-A pattern check      │
                   │ • Victim ratio filter      │
                   │ • Token pair validation    │
                   │ • Confidence scoring       │
                   └────────────┬────────────────┘
                                ↓
                        [Detected Sandwiches]
                                    ↓
                   ┌─────────────────────────────┐
                   │ classify_all_attacks()     │
                   │ • Extract attack cluster   │
                   │ • Analyze victims          │
                   │ • Check token paths        │
                   │ • Score components         │
                   │ • Classify type            │
                   └────────────┬────────────────┘
                                ↓
                        [Classified Results]
                                    ↓
                OUTPUT: DataFrame with columns:
                • attack_type (fat_sandwich / multi_hop_arbitrage / ambiguous)
                • confidence (0.0-1.0)
                • fat_sandwich_score
                • multi_hop_score
                • victim_count
                • token_pairs
                • unique_pools
                • is_cycle
```

---

## 🔬 Detection Algorithm

### Step 1: Rolling Time Window Scanning

```
Timeline:  T0────────────────T1────────────────T2────────────────T3
           │                 │                 │                 │
           └─── WINDOW 1s ──→│                 │                 │
                             T1─── WINDOW 1s ──→│                 │
                                                 T2─── WINDOW 1s ──→│

Each window (1s, 2s, 5s, 10s):
┌─────────────────────────────────┐
│ Trade 1: Alice → BOB            │
│ Trade 2: BOB → Charlie          │  A-B-A Pattern?
│ Trade 3: Charlie → Alice        │  ✓ Alice (A) first & last
│ Trade 4: Alice → BOB            │  ✗ Skip (already counted)
└─────────────────────────────────┘
         ↓
Result: ✅ Fat Sandwich Detected
```

### Step 2: A-B-A Pattern Validation

```
Pattern Check:

    A (Attacker)
    │    B1 (Victim 1)
    │    │   B2 (Victim 2)
    ↓    ↓   ↓
    ┌──┬──┬──┬──┐
    │A1│B1│B2│A2│  ← All trades in window (ms_time order)
    └──┴──┴──┴──┘
       ↑     ↑
       └─────┘ Same signer? ✓

Validation Checklist:
✓ First signer == Last signer
✓ Middle trades have different signers (victims)
✓ No victim is the attacker
✓ Minimum attacker trades ≥ 2
```

### Step 3: Victim Ratio Filtering

```
Filter Aggregator Routing:

If victim_ratio = victims / total_trades > 0.8
    ⚠️  Likely aggregator routing, not MEV
    → SKIP

If victim_ratio ≤ 0.8
    ✓ Enough concentrated attack
    → CONTINUE
```

### Step 4: Token Pair Validation

```
Token Pair Reversal Check:

Attacker's first trade:  USDC → SOL
Attacker's last trade:   SOL → USDC
                         ↑       ↑
                    Reversed! ✓ Valid

If NOT reversed:
    ⚠️ Not a sandwich pattern
    → SKIP
```

### Step 5: Confidence Scoring

```
Score Components (max 10 pts):

Base scoring:
  +3 pts: victim_ratio < 0.3 (very concentrated)
  +2 pts: victim_ratio 0.3-0.5 (concentrated)
  
  +2 pts: attacker_trades ≥ 3 (aggressive)
  
  +2 pts: token_pair reversal validated
  
  +1 pt:  window_seconds ≤ 2 (fast execution)
  
  +1 pt:  victim_count ≥ 3 (multiple targets)

Final Confidence:
  score ≥ 6 pts: "high" ✓
  score 4-5 pts: "medium" ⚠️
  score < 4 pts: "low" ❌
```

---

## 📊 Classification Algorithm

### Phase 1: Gather Evidence

```
For each detected sandwich, analyze:

1. VICTIM EVIDENCE
   ├─ Victim count (from A-B-A middle)
   ├─ Victim ratio
   └─ Has mandatory victims? (≥2)

2. TOKEN EVIDENCE
   ├─ Token pair count
   ├─ Are they same throughout? (same_pair = 1)
   └─ Is it a cycle? (A→B→C→...→A)

3. POOL EVIDENCE
   ├─ Unique pools used
   ├─ Pool diversity pattern
   └─ Appears coordinated?
```

### Phase 2: Score Attack Type

```
FAT SANDWICH SCORING:
─────────────────────
+0.35: Has wrapped victims (mandatory)
+0.25: Uses same token pair throughout
+0.20: Low pool diversity (1-2 pools)
────────────
Max = 0.80

vs

MULTI-HOP ARBITRAGE SCORING:
─────────────────────────────
+0.35: Cycle routing detected
+0.25: Multiple different token pairs (≥3)
+0.20: High pool diversity (≥3 pools)
+0.20: No wrapped victims needed
────────────
Max = 0.80
```

### Phase 3: Make Decision

```
Decision Tree:

if fs_score > mh_score + 0.15:
    → Return "fat_sandwich"
           confidence = fs_score

elif mh_score > fs_score + 0.15:
    → Return "multi_hop_arbitrage"
           confidence = mh_score

else:
    → Return "ambiguous"  (too close to call)
           confidence = max(fs_score, mh_score)


Example Scoring:
┌──────────────────────────┐
│ Attack #42               │
├──────────────────────────┤
│ Victims: 5       → +0.35 │
│ Same pair: Yes   → +0.25 │
│ Pool diversity:2 → +0.20 │
├──────────────────────────┤
│ FS Score: 0.80           │
│ MH Score: 0.00           │
├──────────────────────────┤
│ Result: FAT_SANDWICH     │
│ Conf: 80%                │
└──────────────────────────┘
```

---

## 🎮 Usage Examples

### Interactive (Notebook)

```
1. Open: 12_fat_sandwich_optimized_detector.ipynb
2. Cell by cell execution with output
3. Real-time parameter adjustment
4. Visual analysis at each step
```

### Command Line (Script)

```bash
cd /Users/aileen/Downloads/pamm/solana-pamm-analysis/solana-pamm-MEV-binary-monte-analysis
python3 fat_sandwich_detector_optimized.py
```

### Programmatic (Import)

```python
from fat_sandwich_detector_optimized import FatSandwichDetector

df_trades = load_trade_data()
detector = FatSandwichDetector(df_trades)

# Detect
sandwiches, stats = detector.detect_fat_sandwiches(
    window_seconds=[1, 2, 5, 10],  # Adjust windows
    min_trades=5,                   # Adjust sensitivity
)

# Classify
classified = detector.classify_all_attacks(sandwiches)

# Analyze
analyze_results(classified)
```

---

## 📈 Output Interpretation

### Results DataFrame Columns

```
DETECTION COLUMNS:
├─ attacker_signer: Address of attacker
├─ victim_count: Number of different victims
├─ victim_signers: List of victim addresses
├─ total_trades: Total trades in window
├─ attacker_trades: Attacker's trade count
├─ victim_ratio: Victims / Total trades
├─ window_seconds: Time window size used
├─ actual_time_span_ms: Real time (milliseconds)
├─ start_slot / end_slot: Solana slots
├─ validator: Which validator ran it
├─ confidence: high / medium / low
├─ confidence_score: Numeric score
└─ confidence_reasons: explain_why

CLASSIFICATION COLUMNS:
├─ attack_type: fat_sandwich | multi_hop_arbitrage | ambiguous
├─ confidence: 0.0-1.0 score
├─ fat_sandwich_score: Component score
├─ multi_hop_score: Component score
├─ is_cycle: Boolean (cycle routing detected)
└─ token_pairs: Number of different pairs
```

### Interpreting Results

```
EXAMPLE Row:
┌─────────────────────────────┐
│ attacker_signer:            │
│   9B5X4zA...Yw4Kp2C3J       │  ← Who attacked
├─────────────────────────────┤
│ Confidence: 0.87 ✓          │  ← Very confident
│ attack_type: fat_sandwich   │  ← Type identified
├─────────────────────────────┤
│ victim_count: 8             │  ← 8 victims wrapped
│ token_pairs: 1              │  ← Only one pair (USDC↔SOL)
│ window_seconds: 2           │  ← Fast (2 seconds)
├─────────────────────────────┤
│ actual_time_span_ms: 1,247  │  ← Actually 1.2s
│ validator: Validator_42     │  ← Which validator
└─────────────────────────────┘

INTERPRETATION:
✅ High confidence Fat Sandwich attack
✅ Attacker wrapped 8 victims
✅ Completed in 1.2 seconds
✅ Used same token pair (likely SOL pair)
✅ Likely extracted value = slippage × 8 victims
```

---

## 🎨 Parameter Guide

### Time Windows: `window_seconds`

```
[1]     → Catch fast attacks (aggressive bots)
        → High FP rate (single-block ops)

[1, 2]  → Standard (most MEV happens here)

[1, 2, 5, 10]
        → Comprehensive (catch variations)

[5, 10, 30]
        → Slower patterns (less common)

Why multiple?
- Some attacks happen in 1s
- Some take 2-5s to coordinate
- Multiple windows = more detections
```

### Victim Ratio: `max_victim_ratio`

```
0.5 (50%)
  → Very strict (only attacks with <50% victim trades)
  → Filters most aggregator routing
  → May miss some real attacks

0.8 (80%)
  → Balanced (standard recommendation)
  → Allows some aggregator traffic
  → Catches most real attacks

0.95 (95%)
  → Very permissive
  → Allows mostly victim trades
  → More false positives
```

### Minimum Trades: `min_trades`

```
3  → Very sensitive (high FP rate)
5  → Standard (recommended)
10 → Conservative (high FN rate)
```

---

## 🚨 Common Issues & Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| No detections | Parameters too strict | Lower `min_trades`, raise `max_victim_ratio` |
| Too many low confidence | Window too large | Use smaller `window_seconds` |
| Very slow | Large dataset | Use `sample_size` parameter |
| Memory error | Data too big | Process by AMM pool separately |

---

## 📝 Summary

The optimized detector:
1. **Scans** trades in rolling time windows ⏱️
2. **Validates** A-B-A pattern + victims 👥
3. **Filters** aggregator routing 🚫
4. **Scores** confidence 📊
5. **Classifies** attack type 🎯
6. **Outputs** detailed results 📋

All in one unified, easy-to-use class! ✨
