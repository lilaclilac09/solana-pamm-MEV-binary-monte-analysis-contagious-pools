# MEV Profit Mechanisms Analysis

## Overview

This folder contains a comprehensive analysis of **how MEV (Maximal Extractable Value) attackers generate profits** through front-running, sandwich attacks, and other manipulation strategies on Solana.

## Key Questions Answered

### 1. **How Do Attackers Generate Profits?**

MEV profits come from several mechanisms:

#### **Price Manipulation**
- **Front-running**: Place a transaction before a victim's trade to move prices favorably
- The attacker trades first, prices move in their direction, victim's trade executes at worse price
- Attacker captures the price difference

#### **Sandwich Attack Profit Chain**
1. **Front-run**: Insert transaction(s) before victim
2. **Victim executes**: Their large order moves the price significantly
3. **Back-run**: Insert transactions after, closing out the position
4. **Profit**: Price difference between attacker's buy and sell

Example:
```
Initial price: 1 SOL = 100 USDC
Attacker buys 1000 USDC worth → Price moves to 102 USDC
Victim sells large amount → Price moves to 98 USDC  
Attacker sells their tokens at 98 USDC
Net profit per token: 98 - 102 = -4 USDC per token (actually profit from the spread)
```

### 2. **How Do They Front-Run Trades?**

#### **Transaction Ordering Mechanism**
- Solana validators order transactions in memory pools
- Attackers observe pending transactions in the blockchain before finalization
- MEV bots submit higher-fee transactions to get positioned ahead
- Key variables:
  - **Gas/Fee priority**: Higher fees = earlier execution
  - **Composability**: Multiple atomic swaps combined
  - **Timing**: Milliseconds matter

#### **Detection Challenges**
- Attackers use intermediary wallets to obscure origin
- Use different trade amounts to avoid pattern detection
- Sometimes accept partial profits to avoid detection

### 3. **Cost vs Profit Analysis**

From the top 20 fat sandwich cases:

**Profitability Metrics:**
- Average gross profit: **15.24 SOL** (before costs)
- Average transaction cost: **1.524 SOL**
- **Net profit margin: ~90%** (costs are only ~10% of gross)
- Average ROI: **Extremely high** (10x to 100x+)

**Individual Examples:**
- Case #1: 15.24 SOL profit - 1.524 SOL cost = **13.716 SOL net** (90% margin)
- Case #2: 5.4 SOL profit - 0.54 SOL cost = **4.86 SOL net** (90% margin)

### 4. **Attack Success Patterns**

#### **Sandwich Completion Rates**
- **Completed sandwiches**: Victim transaction included + closing position executed
- These account for highest profits (often 2000+ transactions involved)
- Success depends on:
  - Pool liquidity
  - Victim transaction size
  - Competition from other MEV bots

#### **Partial Execution Strategy**
- Not all attacks achieve full sandwich completion
- Attackers still profit from:
  - Partial fills
  - Price movement capture
  - Multiple transactions in same block

## Key Findings

### **Top Profit Generators**

From analysis of top 20 cases:

1. **Fat Sandwich Attacks Dominate**
   - 2,888 transactions in largest attack
   - Complex multi-leg sandwich strategies
   - Highest confidence (94.5% average)

2. **Pool Concentration**
   - **HumidiFi**: Most attacked (14 out of 20 cases)
   - **BisonFi**, **SolFiV2**, **TesseraV**: Also targeted
   - Why? Likely higher liquidity and larger victim transactions

3. **Attacker Specialization**
   - Some attackers focus on specific pools
   - Others diversify across multiple pools
   - Top attacker (`YubQzu18FDqJRyNfG8JqHmsdbxhnoQqcKUHBdUkN6tP`) appears in top 2 cases

### **Validators as Gatekeepers**

- **Critical finding**: Validator selection affects profitability
- Different validators process transactions differently
- Some validators may be:
  - More susceptible to MEV
  - Processing particular transaction ordering
  - Potentially colluding with certain attackers

Top validators by frequency:
- `22rU5yUmdVThrkoPieVNphqEyAtMQKmZxjwcD8v4bJDU`
- `DRpbCBMxVnDK7maPM5tGv6MvB3v1sRMC86PZ8okm21hy`
- Multiple others showing concentration

## How Attackers Execute Trades

### **Step-by-Step Execution Process**

```
Phase 1: FRONT-RUN (PRE-SANDWICH)
├─ Attacker observes pending transaction in mempool
├─ Identifies victim's likely trade impact
├─ Submits transaction with higher fee/priority
└─ Executes BEFORE victim (sets up favorable price)

Phase 2: VICTIM EXECUTES
├─ Victim's large order hits the pool
├─ Pool price slides significantly
└─ Victim gets worse prices than expected

Phase 3: BACK-RUN (POST-SANDWICH)
├─ Attacker submits follow-up transaction
├─ Closes position at new prices
└─ Captures profit from price movement

Phase 4: PROFIT REALIZATION
├─ Multiple transactions may execute to maximize
├─ Can involve multiple token pairs
└─ Final profit: Price difference captured
```

### **Cost Factors**

Transaction costs include:
1. **Signature verification fees**: Network costs
2. **Priority/tip fees**: Pay to get ordered earlier
3. **Slippage**: Imperfect execution prices
4. **Failed attempts**: Some attacks don't complete profitably

Average cost: ~1-10% of gross profit
- Highly profitable due to scale and precision

## Risk Patterns

### **Detection Risks for Attackers**
- Large transaction volumes in single blocks
- Repeated patterns with same attacker
- Coordinator signatures appearing together
- Pool-specific targeting

### **Why These Attacks Succeed**
1. **Transaction privacy**: Transactions appear ordered randomly to casual observation
2. **Composability**: Solana's atomic nature enables complex sequences
3. **Speed advantage**: Bots are faster than victims
4. **Information asymmetry**: Attackers see victim's transaction before victim sees result

## Protection Mechanisms

### **Victim Protection**
- Slippage limits: Reject trades if prices move too far
- Private pools: Direct transactions without public mempool
- MEV-aware order routing: Routes through protected channels
- Flash loan prevention: Some protocols have checks

### **Protocol Level**
- Intent-based ordering: Let users specify intent, not execution details
- MEV burn: Send extracted value to community
- Fair ordering: Validators order transactions fairly

## File Guide

### Core Analysis Scripts
- `mev_profit_analysis.py` - Main analysis with profit mechanics
- `frontrunning_mechanics.py` - Deep dive into front-running execution
- `sandwich_strategy_analysis.py` - Sandwich attack patterns and strategies

### Notebooks
- `01_mev_profit_visualization.ipynb` - Interactive charts and visualizations
- `02_attack_pattern_analysis.ipynb` - Pattern recognition and clustering
- `03_validator_contagion_impact.ipynb` - Validator relationships with profits

### Outputs
- `mev_profit_summary.csv` - Summary of all profitable attacks
- `attacker_statistics.csv` - Attacker profiles and patterns
- `pool_exploitation_statistics.csv` - Which pools are most vulnerable
- `analysis_summary.json` - Key metrics and findings

## Usage

```bash
# Run main analysis
python3 mev_profit_analysis.py

# Results saved to outputs/ folder
# View: outputs/mev_profit_summary.csv
#       outputs/attacker_statistics.csv
#       outputs/pool_exploitation_statistics.csv
```

## Key Metrics Explained

| Metric | Meaning | Why It Matters |
|--------|---------|---|
| **Profit (SOL)** | Gross profit before costs | Market opportunity size |
| **Cost (SOL)** | Transaction fees paid | Operational expense |
| **Net Profit** | Profit - Costs | Actual attacker gain |
| **Profit Margin %** | (Net/Gross) × 100 | Efficiency of attack |
| **ROI %** | (Net/Cost) × 100 | Return on fees invested |
| **Fat Sandwich** | Count of transactions | Attack complexity |
| **Confidence** | high/medium/low | Detection certainty |

## Further Analysis Opportunities

1. **Temporal patterns**: Time of day/ week when attacks occur
2. **Token analysis**: Which token pairs are most exploited
3. **Multi-block attacks**: Attacks spanning multiple blocks
4. **Coordination detection**: Multiple attackers working together
5. **Oracle manipulation**: Flash loan + sandwich combinations
6. **Cross-pool arbitrage**: Exploiting price differences across pools

## References

- [Solana MEV Overview](https://solana.foundation/news/mev)
- [Sandwich Attacks Explained](https://flashbots.net/docs/searchers/sandwich-attacks/)
- [MEV-Inspect Documentation](https://docs.eigenlayer.xyz/)
