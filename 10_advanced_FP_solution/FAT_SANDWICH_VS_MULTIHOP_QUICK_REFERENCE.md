# Quick Reference: Fat Sandwich vs Multi-Hop Arbitrage

## The 60-Second Decision Tree

```
START: Analyzing attack cluster
    ↓
Q1: Are there 2+ different signers between first and last attacker trade?
    ├─ YES (Wrapped Victims Found) → Score +0.35 for Fat Sandwich
    └─ NO (No Victims) → Score +0.20 for Multi-Hop
    ↓
Q2: Does signer use ONLY the same token pair throughout?
    ├─ YES (e.g., only PUMP↔WSOL) → Score +0.25 for Fat Sandwich
    └─ NO (Different pairs) → Score +0.25 for Multi-Hop
    ↓
Q3: How many unique pools/AMMs does signer use?
    ├─ 1-2 pools → Score +0.20 for Fat Sandwich
    ├─ 3+ pools → Score +0.20 for Multi-Hop
    └─ Mixed → Draw
    ↓
Q4: Does signer's net token balance equal ZERO (excluding starting token)?
    ├─ YES (Cycle closed) → Strong Multi-Hop indicator
    └─ NO (Profit kept) → Strong Fat Sandwich indicator
    ↓
Q5: Did Oracle update in this slot?
    ├─ YES + tight timing → Strong Fat Sandwich indicator
    └─ NO → Slight Multi-Hop indicator
    ↓
FINAL: Compare scores
    ├─ Fat Sandwich > Multi-Hop + 0.15 → CLASSIFY AS FAT SANDWICH
    ├─ Multi-Hop > Fat Sandwich + 0.15 → CLASSIFY AS MULTI-HOP ARBITRAGE
    └─ Othewise → AMBIGUOUS (Manual review)
```

---

## Instant Checklist: 30-Second Analysis

Use this checklist when you only have 30 seconds:

### FAT SANDWICH Indicators (Mark if YES)
- [ ] Multiple different signers between front-run and back-run
- [ ] Attacker only touches one token pair (e.g., PUMP/WSOL)
- [ ] Uses 1-2 pools targeting same token pair
- [ ] Execution <50ms
- [ ] Oracle burst detected in same slot

**Count: ___ / 5**
- 4-5 marks = Definitely Fat Sandwich
- 3 marks = Likely Fat Sandwich
- 2 marks = Could be either

### MULTI-HOP ARBITRAGE Indicators (Mark if YES)
- [ ] No intermediate victim signers
- [ ] Token path forms a cycle (A→B→C→A or ends with SOL/USDC)
- [ ] Uses 3+ pools from different protocols
- [ ] Signer's net balance = 0 for all tokens
- [ ] No Oracle burst dependency

**Count: ___ / 5**
- 4-5 marks = Definitely Multi-Hop
- 3 marks = Likely Multi-Hop
- 2 marks = Could be either

---

## Visual Comparison Matrix

```
┌─────────────────────────────────────────────────────────────┐
│                 FAT SANDWICH vs MULTI-HOP                   │
├──────────────────────────────────┬──────────────────────────┤
│ Fat Sandwich (B91)               │ Multi-Hop Arbitrage      │
├──────────────────────────────────┼──────────────────────────┤
│                                                              │
│ Pattern: A→B→C→...→A             │ Pattern: A→B→C→A (Cycle) │
│ A=Attacker, B/C=Victims          │ Only 1 signer (Bot)      │
│                                                              │
│ Signature Trade Flow:            │ Signature Trade Flow:    │
│   ATTACKER:   PUMP→WSOL          │   BOT:  SOL→TOKEN_A      │
│   VICTIM:     WSOL→PUMP          │   BOT:  TOKEN_A→TOKEN_B  │
│   ATTACKER:   PUMP→WSOL          │   BOT:  TOKEN_B→SOL      │
│                                                              │
├──────────────────────────────────┼──────────────────────────┤
│ Goal: Extract slippage from      │ Goal: Exploit pool       │
│       victim transactions         │       imbalances         │
│                                                              │
│ Requires: Victim(s)              │ Requires: None           │
│                                                              │
│ Profit from: Victim loss         │ Profit from: Differential│
│              (MEV extraction)     │              pricing     │
│                                                              │
├──────────────────────────────────┼──────────────────────────┤
│ ✓ Mandatory: 2+ victims          │ ✓ Zero victims           │
│ ✓ Token pair: Same throughout    │ ✓ Token path: Cyclic     │
│ ✓ Pools: 1-2 (same pair)         │ ✓ Pools: 3+ (diverse)    │
│ ✓ Net balance: >0 (profit kept)  │ ✓ Net balance: =0        │
│ ✓ Oracle: 99.8% correlation      │ ✓ Oracle: 50% optional   │
│ ✓ Timing: <50ms (critical)       │ ✓ Timing: Variable       │
│                                                              │
├──────────────────────────────────┼──────────────────────────┤
│ Regulatory: HARMFUL              │ Regulatory: NEUTRAL      │
│ Targets: Retail users            │ Targets: Pool state      │
│                                                              │
└──────────────────────────────────┴──────────────────────────┘
```

---

## Code Snippet Library

### Quick Check 1: Victim Count
```python
def quick_victim_check(cluster_df, attacker):
    signer_indices = cluster_df[cluster_df['signer'] == attacker].index
    if len(signer_indices) < 2:
        return 0
    between = cluster_df[
        (cluster_df.index > signer_indices[0]) & 
        (cluster_df.index < signer_indices[-1])
    ]
    victims = between['signer'].nunique()
    return victims >= 2  # Boolean: Has mandatory victims?
```

### Quick Check 2: Same Pair?
```python
def same_pair_check(cluster_df, signer):
    trades = cluster_df[cluster_df['signer'] == signer]
    pairs = trades.apply(
        lambda row: tuple(sorted([row['from_token'], row['to_token']])),
        axis=1
    ).unique()
    return len(pairs) == 1  # Boolean: Only 1 unique pair?
```

### Quick Check 3: Pool Count
```python
def pool_count_check(cluster_df, signer):
    trades = cluster_df[cluster_df['signer'] == signer]
    pools = trades['amm_trade'].nunique()
    return pools  # Return count
```

### Quick Check 4: Cycle Detection
```python
def cycle_check(cluster_df, signer):
    trades = cluster_df[cluster_df['signer'] == signer].sort_values('ms_time')
    # Build path
    path = [trades.iloc[0]['from_token']]
    path.extend(trades['to_token'].tolist())
    # Check if cycle
    return path[0] == path[-1]  # Boolean: Cycle closed?
```

### Quick Check 5: Net Balance
```python
def net_balance_check(cluster_df, signer):
    trades = cluster_df[cluster_df['signer'] == signer]
    balance = {}
    for _, t in trades.iterrows():
        balance[t['from_token']] = balance.get(t['from_token'], 0) - 1
        balance[t['to_token']] = balance.get(t['to_token'], 0) + 1
    # Exclude first token
    first = trades.iloc[0]['from_token']
    nonzero = {k:v for k,v in balance.items() if k != first and v != 0}
    return len(nonzero) == 0  # Boolean: Perfect cycle?
```

---

## Scoring Shorthand

### Quick Scoring Method

```
Fat Sandwich Score = count_if([
    victims >= 2,
    same_pair == True,
    pools <= 2,
    oracle_burst == True,
    timing < 50ms
]) / 5

Multi-Hop Score = count_if([
    victims == 0,
    cycle_detected == True,
    pools >= 3,
    net_balance == 0,
    oracle_burst == False
]) / 5

Classification:
  if fs_score > mh_score + 0.2: "Fat Sandwich"
  elif mh_score > fs_score + 0.2: "Multi-Hop"
  else: "Ambiguous"
```

---

## Real-World Examples

### Example A: Obvious Fat Sandwich
```
Cluster Time Window: 1000-1150 ms (150ms total)

Trade 1 (1000ms): ATTACKER PUMP→WSOL (buy)
Trade 2 (1050ms): VICTIM1  WSOL→PUMP (buy)
Trade 3 (1100ms): VICTIM2  WSOL→PUMP (buy)
Trade 4 (1150ms): ATTACKER PUMP→WSOL (sell)

Checks:
  ✓ Victims: 2
  ✓ Same pair: PUMP/WSOL only
  ✓ Pools: 1 (RAYDIUM_PUMP_WSOL)
  ✗ Cycle: No (PUMP→WSOL→PUMP)
  ✓ Oracle: Yes (just updated)

Score: 4/5 → DEFINITELY FAT SANDWICH
```

### Example B: Obvious Multi-Hop
```
Cluster Time Window: 2000-2200 ms

Trade 1 (2000ms): BOT SOL→TOKEN_A (Orca)
Trade 2 (2050ms): BOT TOKEN_A→TOKEN_B (Orca)
Trade 3 (2100ms): BOT TOKEN_B→USDC (Jupiter)
Trade 4 (2150ms): BOT USDC→SOL (MarinadeDirect)

Checks:
  ✓ Victims: 0 (only 1 signer)
  ✓ Cycle: Yes (SOL→...→USDC/SOL)
  ✓ Pools: 3 different
  ✓ Net balance: All zero
  ✗ Oracle: No

Score: 4/5 → DEFINITELY MULTI-HOP
```

### Example C: Ambiguous (Manual Review)
```
Cluster Time Window: 5000-5200 ms

Trade 1 (5000ms): BOT1 SOL→PUMP
Trade 2 (5050ms): BOT1 PUMP→ORCA
Trade 3 (5100ms): BOT2 ORCA→SOL
Trade 4 (5150ms): BOT1 ORCA→SOL

Checks:
  ? Victims: Yes (BOT2), but BOT2 might be same operator
  ? Cycle: Partial (opens then closes)
  ? Pools: 2
  ? Net balance: Ambiguous across multiple signers
  ? Oracle: Yes

Ambiguity: Different signers, but related behavior
Recommendation: Check if BOT1 and BOT2 are related addresses
```

---

## Training Data Patterns

### Pattern 1: Classic Fat Sandwich
```
Attacker Count: 2-3 trades
Victim Count: 1-5 victims
Time Span: 10-50ms
Pools: 1-2
Conclusion: FAT SANDWICH
```

### Pattern 2: Multi-Pool Fat Sandwich
```
Attacker Count: 2-4 trades
Victim Count: 2-6 victims
Time Span: 50-150ms
Pools: 2-4 (all same pair)
Conclusion: FAT SANDWICH (same token pair overrides pool count)
```

### Pattern 3: Classic Multi-Hop
```
Bot Count: 3-5 trades
Victim Count: 0
Time Span: 50-500ms
Pools: 3-6 (diverse)
Conclusion: MULTI-HOP
```

### Pattern 4: Arbitrage + Router
```
Attacker: 2 trades (same pair)
Router: 3+ trades (different pairs, same signer)
Time Span: 200-500ms
Conclusion: Depends on primary signer
  - If attacker is primary: FAT SANDWICH
  - If router is primary: MULTI-HOP
```

---

## Common Mistakes to Avoid

❌ **Mistake 1**: Counting self-trades as victims
- Solution: Filter victims to different signers
```python
victims = [s for s in middle_trades['signer'].unique() if s != attacker]
```

❌ **Mistake 2**: Not normalizing token addresses
- Solution: Convert to uppercase and remove 'wrapped_' prefixes
```python
token = token.upper().replace('WRAPPED_', '')
```

❌ **Mistake 3**: Using wrong time window boundaries
- Solution: Use exact slot start/end times from data
```python
cluster = df[
    (df['block_timestamp'] >= slot_start) & 
    (df['block_timestamp'] <= slot_end)
]
```

❌ **Mistake 4**: Ignoring partial cycles
- Solution: Check if ends in base asset (SOL/USDC)
```python
last_token = trades.iloc[-1]['to_token']
is_closed = (last_token == first_token) or (last_token in ['SOL', 'USDC'])
```

❌ **Mistake 5**: Over-weighting oracle correlation
- Solution: Use oracle as tiebreaker, not primary factor
```python
# Oracle should only be 0.20 weight, not primary
```

---

## When to Default to Each Classification

### Default to Fat Sandwich if:
1. Any victims detected (even just 1)
2. Same token pair dominates
3. Time span < 100ms
4. Oracle burst in slot

### Default to Multi-Hop if:
1. Multiple different token pairs
2. 3+ unique pools
3. Zero victims
4. Net balance = 0

### Default to Ambiguous if:
1. Conflicting indicators
2. Incomplete data
3. Cross-signer complexity
4. Unclear transaction order

---

## Production Integration

### Step 1: Batching
```python
for cluster_id, cluster_trades in grouped_trades:
    classification = classify_single_cluster(cluster_trades)
    results.append(classification)
```

### Step 2: Quality Control
```python
high_conf = results[results['confidence'] > 0.85]
ambiguous = results[results['confidence'] <= 0.70]
print(f"High Confidence: {len(high_conf)} ({len(high_conf)/len(results):.1%})")
print(f"Ambiguous: {len(ambiguous)} ({len(ambiguous)/len(results):.1%})")
```

### Step 3: Validation
```python
# Compare against known patterns
validate_against_known_fat_sandwiches(results)
validate_against_known_arbitrage(results)
```

---

## Frequently Asked Questions

**Q: What if a cluster has multiple attackers?**
A: Analyze each signer separately. One may be Fat Sandwich, another Multi-Hop.

**Q: What if tokens have different addresses (wrapped versions)?**
A: Normalize all addresses. Use canonical symbol names (SOL, USDC, PUMP).

**Q: What about MEV through smart contracts?**
A: These tools work for observable on-chain patterns. SC-internal logic is hidden.

**Q: Can an attack be both Fat Sandwich AND Multi-Hop?**
A: Theoretically yes, but rare. Classify by dominant pattern. Primary signer's goal determines type.

**Q: What confidence threshold should I use?**
A: 
- High priority: >85%
- Medium priority: 70-85%
- Ignore: <70% (too ambiguous)

---

## Summary Scorecard

| Check | Max Points | Fat Sandwich | Multi-Hop |
|-------|-----------|---|---|
| Victims | +0.35 | +0.35 | Penalized |
| Token Path | +0.25 | +0.25 | +0.25 |
| Pool Count | +0.20 | +0.20 | +0.20 |
| Cycle Routing | +0.20 | Penalized | +0.20 |
| Oracle Burst | +0.20 | +0.20 | Optional |
| **Total** | **1.35** | **Up to 1.35** | **Up to 1.10** |

**Classification Rule**:
- Max possible: 1.00 (normalized)
- Classify to whichever has higher normalized score
- If scores within 0.15: Ambiguous
