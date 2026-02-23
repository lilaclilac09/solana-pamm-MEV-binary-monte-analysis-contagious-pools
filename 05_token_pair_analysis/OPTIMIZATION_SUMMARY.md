# Optimization Summary: 05_token_pair_analysis.ipynb Deep Analysis

## New Content

Added **Step 8.5: Deep Root Cause Analysis** between Step 8 and Step 9, containing the following deep analysis:

### 1. Sandwich Profit Estimation & Success Rate Statistics
- **Function**: Detect all A-B-A sandwich patterns and estimate profits
- **Output**:
  - Total sandwich count
  - Total estimated profit (SOL)
  - Average profit per sandwich
  - Top 10 fat sandwiches profit
  - Success rate statistics (100%, because dataset only contains successful trades)

### 2. Multi-Pool Coordination Network Analysis
- **Function**: Use NetworkX to build attacker-pool coordination network graph
- **Output**:
  - Network statistics (node count, edge count, coordinated attacker count)
  - Top 10 multi-pool attackers list
  - Network visualization graph (`coordination_network.png`)
    - Red nodes = multi-pool attackers
    - Cyan nodes = single-pool attackers
    - Edge weight = sandwich count

### 3. Root Cause Analysis: Liquidity vs Attack Rate
- **Function**: Analyze why certain pools are heavily attacked
- **Output**:
  - Top 10 high attack rate pools (low liquidity = high attack rate)
  - Pool attack analysis CSV (`pool_attack_analysis.csv`)

### 4. Enhanced Monte Carlo: Victim Loss Simulation
- **Function**: Simulate victim loss distribution
- **Output**:
  - Loss statistics from 10,000 simulations
  - Average loss, 95th percentile loss
  - Loss distribution histogram (`victim_loss_distribution.png`)

### 5. Root Cause Summary
- **Function**: Systematically summarize why PUMP/WSOL is heavily attacked
- **Output**:
  - 6 major root cause analyses (Meme Token popularity, PropAMM vulnerability, Validator concentration, etc.)
  - Key statistics
  - Recommended measures
  - Markdown report (`root_cause_analysis.md`)

## Output Files

All newly generated files are saved in `derived/deep_dive_analysis/`:

1. `coordination_network.png` - Coordination network visualization
2. `pool_attack_analysis.csv` - Pool attack rate analysis
3. `victim_loss_distribution.png` - Victim loss distribution
4. `root_cause_analysis.md` - Root cause analysis report

## Running Instructions

1. **Prerequisites**: Ensure previous cells have been run (data loading, MEV analysis, Monte Carlo, etc.)
2. **Dependencies**: Need to install `networkx` (if not installed, run `pip install networkx`)
3. **Run**: Simply run Step 8.5's code cell

## Code Features

- **Adaptive**: Automatically detects available columns (`ms_time` vs `time`, `account_trade` vs `amm_trade`)
- **Fault-tolerant**: If certain columns are missing, displays warnings but won't crash
- **Visualization**: Generates high-quality charts (300 DPI)
- **Data Export**: All analysis results saved as CSV/Markdown

## Key Findings

Based on these optimization analyses, can answer:

1. **Profit Quantification**: How much SOL did bots earn from sandwiches?
2. **Coordination Patterns**: Which attackers coordinate attacks across multiple pools?
3. **Root Cause Identification**: Why are certain pools/pairs heavily attacked? (low liquidity, slow oracle, concentrated validator)
4. **Victim Impact**: How much SOL do users lose on average?
5. **Systemic Vulnerabilities**: What are the fundamental problems with Solana MEV?

## Next Steps

After running the code, viewing outputs and generated files, can:
- Identify most active attackers
- Find most vulnerable pools
- Quantify MEV impact on users
- Provide data support for protective measures
