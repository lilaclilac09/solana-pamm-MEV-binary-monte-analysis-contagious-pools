# 12_mev_profit_mechanisms - Quick Start Guide

## What's in This Folder?

A comprehensive analysis of **how MEV attackers generate profits** through front-running and sandwich attacks on Solana.

## Core Files

### 📊 Analysis Scripts
- **`mev_profit_analysis.py`** - Main profit analysis engine
  - Profit generation mechanisms
  - Sandwich attack mechanics
  - Attacker behavior patterns
  - Validator relationships
  - Pool exploitation analysis
  
- **`frontrunning_mechanics.py`** - Front-running execution details
  - Attack sequence analysis
  - Price impact mechanisms
  - Transaction ordering strategies
  - Multi-leg swap patterns
  - Attack frequency patterns

### 📖 Documentation
- **`MEV_PROFIT_MECHANISMS.md`** - Comprehensive guide (READ THIS FIRST)
  - How attacks generate profit
  - Cost vs profit analysis
  - Attack success patterns
  - Risk and protection mechanisms

### 📁 Outputs
- `mev_profit_summary.csv` - All profitable attacks ranked
- `attacker_statistics.csv` - Attacker profiles and patterns
- `pool_exploitation_statistics.csv` - Vulnerability by pool
- `attack_execution_patterns.csv` - Attack mechanics breakdown

## Quick Start

### 1️⃣ Run Core Analysis
```bash
python3 mev_profit_analysis.py
```
This generates:
- Detailed profit analysis (terminal output)
- CSV files with attacker & pool statistics
- JSON summary of key metrics

### 2️⃣ Run Execution Analysis
```bash
python3 frontrunning_mechanics.py
```
This generates:
- Attack execution sequence analysis (terminal output)
- Price impact mechanism breakdown
- Transaction ordering patterns
- CSV with execution details

### 3️⃣ View Results
```bash
# See summary of all profitable attacks
cat outputs/mev_profit_summary.csv | head -20

# See attacker profiles
cat outputs/attacker_statistics.csv | head -10

# See pool vulnerabilities
cat outputs/pool_exploitation_statistics.csv | head -15
```

## Key Findings

### 📈 Profitability
- **Average net profit per attack:** 3.37 SOL
- **Average ROI:** ~500% (10x return on transaction costs)
- **Profit margin:** ~90% (costs are minimal)
- **Highest profit:** 13.716 SOL (single attack)

### 🎯 Attack Types
- **Fat Sandwich attacks:** Most profitable (2000+ transactions)
- **Completion rate:** ~76% achieve full sandwich closure
- **Partial successes:** Still profitable even without complete back-run

### 🏊 Pool Targets
Top exploited pools:
1. **HumidiFi** - 14 out of 20 attacks (why? highest liquidity, large victim orders)
2. **BisonFi** - 2 attacks, high profit per attack
3. **SolFiV2** - 1 attack
4. **TesseraV** - 1 attack

### 💰 Top Attacker
- **Signer:** `YubQzu18FDqJRyNfG8JqHmsdbxhnoQqcKUHBdUkN6tP`
- **Profit:** 23.31 SOL from 2 attacks
- **Average:** 11.655 SOL per attack

### 📍 Validator Concentration
- Multiple validators showing high attack frequency
- Suggests validator selection is strategic
- Some validators may be more vulnerable to MEV

## How Profits Are Generated

### The Sandwich Attack Profit Chain

```
Price: 1 token = $1.00

[1] FRONT-RUN: Attacker buys tokens
    → Price moves UP to $1.05 (favorable for attacker)

[2] VICTIM TRADES: Sells large order
    → Price moves DOWN to $0.92 (due to large supply)

[3] BACK-RUN: Attacker sells their tokens
    → Execute at ~$0.92 (but they bought at $1.05)

WAIT - HOW IS THIS PROFITABLE?
Answer: The profit comes from the spread between:
- Pre-attack price (what victims expected)
- Post-attack price (what victims got)
- Attacker captures this difference through complex routing
```

### Real Example from Data
```
Attack: HumidiFi
Gross profit: 15.24 SOL
Transaction cost: 1.524 SOL
Net profit: 13.716 SOL
ROI: 800% return on costs

This represents 2,888 transactions that captured
price movements and spreads across multiple token pairs
in a single atomic block execution.
```

## Attack Statistics by Phase

### Phase 1: Front-Running
- Attacker observes victim's pending transaction
- Identifies pool and trade direction
- Places higher-priority transaction to go first
- Moves prices in favorable direction

### Phase 2: Victim Execution  
- Victim's large order hits the pool
- Price slids significantly due to pool mechanics
- Victims get worse prices than expected
- This is the value being extracted

### Phase 3: Back-Running
- Attacker closes position(s) at new prices
- Multiple transactions may execute together
- Complex routing across pools

### Phase 4: Profit Realization
- Net profit = (exploited price difference) - (transaction costs)
- Success depends on:
  - Pool liquidity
  - Victim transaction size
  - Competition from other MEV bots
  - Network congestion

## Protection Mechanisms (For Developers)

1. **Slippage limits** - Reject trades if prices move >X%
2. **Time locks** - Delay large transactions
3. **MEV-resistant pools** - Fair ordering protocols
4. **Intent-based routing** - Don't broadcast transaction details
5. **Encrypted mempools** - Private transaction ordering

## Validation Checklist

✅ Data loaded successfully
✅ Profit calculations verified
✅ Attack classifications checked
✅ Attacker addresses identified
✅ Validator relationships mapped
✅ Pool vulnerabilities detected

## Common Questions

### Q: How do attackers actually "run" these attacks?
A: They run validators or connect to validators, observe pending transactions, submit higher-fee transactions to get ordered first, and execute atomic multi-swap sequences.

### Q: Why is 1-10% cost so cheap for such large profits?
A: Solana's transaction fees are inherently low (~0.00025 SOL per signature), and attackers only pay priority tips, not compute costs.

### Q: Can victims detect these attacks?
A: Partially. Smart contracts can limit slippage (reject if price moves >X%), but atomic transactions hide the true flow until finalization.

### Q: Why aren't these attacks blocked?
A: Solana's design prioritizes speed/throughput over MEV prevention. This is an ongoing research area.

### Q: How do attackers choose which transactions to attack?
A: Monitor: transaction size (>1M units), token pair, pool, expected price impact. Larger transactions = bigger profit opportunities.

## Data Sources

- `../02_mev_detection/filtered_output/top20_profit_fat_sandwich.csv` - MEV attack data
- `../01_data_cleaning/outputs/pamm_clean_final.parquet` - Pool data

## Next Steps

1. **Run the analysis scripts** to see detailed breakdowns
2. **Read MEV_PROFIT_MECHANISMS.md** for conceptual understanding
3. **Examine the CSV outputs** for specific attack examples
4. **Cross-reference validator_contagion_graph.json** from 04_validator_analysis for validator patterns

## File Size Reference
- MEV data: ~2KB (top 20 cases)
- Clean data: ~100MB (full dataset)
- Analysis runtime: ~2-5 seconds

---

**Last Updated:** February 2026
**Status:** Ready for analysis
