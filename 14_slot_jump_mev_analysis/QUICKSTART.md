# Slot Jump MEV Analysis - Quick Start Guide

## Overview
This module analyzes how slot jumps (skipped slots) in Solana's consensus mechanism create MEV opportunities, with special focus on DobleZero validator behavior.

## Prerequisites

### Data Requirements
You'll need the following data:
1. **Slot history** - Block production records showing produced/skipped slots
2. **MEV transactions** - From `02_mev_detection` module
3. **Oracle updates** - Price oracle update history (Pyth, Switchboard, etc.)
4. **Validator information** - Validator pubkeys and stake data

### Python Dependencies
```bash
pip install pandas numpy scipy matplotlib seaborn
```

## Step-by-Step Analysis

### Step 1: Detect Slot Jumps
First, identify all slot jump events and profile validator behavior:

```bash
python slot_jump_detector.py \
  --input-file data/slot_history.json \
  --output data/slot_jump_analysis.json
```

**Output:**
- `data/slot_jump_analysis.json` - Complete slot jump analysis
- Console report showing jump statistics and validator profiles

**What it does:**
- Identifies skipped slots in the blockchain
- Classifies jumps as single, consecutive, or burst
- Profiles each validator's skip behavior
- Calculates skip pattern entropy

### Step 2: Correlate MEV with Slot Jumps
Analyze correlation between slot jumps and MEV extraction:

```bash
python mev_slot_correlation.py \
  --slot-data data/slot_jump_analysis.json \
  --mev-data ../02_mev_detection/outputs/mev_transactions.json \
  --output data/mev_slot_correlation.json
```

**Output:**
- `data/mev_slot_correlation.json` - Correlation analysis
- Statistical test results (t-tests, correlation coefficients)

**What it does:**
- Maps MEV events to nearby slot jumps
- Calculates correlation strength for each MEV-jump pair
- Compares MEV activity before/during/after jumps
- Performs statistical significance tests

### Step 3: Identify DobleZero Validators
Profile validators to identify DobleZero behavior patterns:

```bash
python doblezero_validator_profiler.py \
  --validator-profiles data/slot_jump_analysis.json \
  --mev-data ../02_mev_detection/outputs/mev_transactions.json \
  --output data/doblezero_profiles.json \
  --min-confidence 0.5
```

**Output:**
- `data/doblezero_profiles.json` - DobleZero candidate profiles
- Top candidates with confidence scores

**What it does:**
- Identifies validators with intentional skip patterns
- Calculates economic profitability of skip strategies
- Assigns confidence scores to DobleZero candidates
- Flags specific behavioral indicators

### Step 4: Analyze Oracle Staleness
Examine how slot jumps create oracle staleness and liquidation opportunities:

```bash
python oracle_staleness_analyzer.py \
  --slot-jumps data/slot_jump_analysis.json \
  --oracle-updates data/oracle_updates.json \
  --mev-events ../02_mev_detection/outputs/mev_transactions.json \
  --output data/oracle_staleness_analysis.json
```

**Output:**
- `data/oracle_staleness_analysis.json` - Oracle staleness events
- Liquidation window identification

**What it does:**
- Detects oracle price update delays during jumps
- Measures price deviation after staleness
- Identifies liquidation opportunity windows
- Correlates staleness with liquidation MEV

## Understanding the Results

### Key Metrics

#### Slot Jump Metrics
- **Jump Size**: Number of consecutive skipped slots
- **Jump Type**: Single (1), Consecutive (2-5), Burst (>5)
- **Skip Rate**: Percentage of assigned slots a validator skips

#### DobleZero Indicators
- **Pattern Entropy**: Low entropy = predictable (intentional) skips
- **MEV Correlation**: How much MEV occurs around validator's blocks
- **Profitability Ratio**: MEV profit vs missed block rewards
- **Confidence Score**: Overall likelihood of DobleZero behavior (0-1)

#### Oracle Staleness Metrics
- **Staleness Duration**: Time since last oracle update (in slots/ms)
- **Price Deviation**: Price change when oracle finally updates
- **MEV Burst**: MEV activity during/after staleness window

### Interpreting Confidence Scores

**DobleZero Confidence Score:**
- **0.8 - 1.0**: High confidence DobleZero behavior
  - Regular skip patterns
  - High MEV correlation
  - Economically profitable
  
- **0.5 - 0.8**: Moderate confidence
  - Some DobleZero indicators
  - May be accidental or strategic
  
- **< 0.5**: Low confidence
  - Likely accidental skips or poor validator performance

## Example Workflow

### Complete Analysis Pipeline
```bash
# 1. Fetch and prepare data
# (Assuming you have Solana RPC access)

# 2. Detect slot jumps
python slot_jump_detector.py \
  --start-epoch 500 \
  --end-epoch 505 \
  --output data/slot_jump_analysis.json

# 3. Correlate with MEV
python mev_slot_correlation.py \
  --slot-data data/slot_jump_analysis.json \
  --mev-data ../02_mev_detection/outputs/mev_transactions.json \
  --output data/mev_slot_correlation.json

# 4. Profile DobleZero validators
python doblezero_validator_profiler.py \
  --validator-profiles data/slot_jump_analysis.json \
  --mev-data ../02_mev_detection/outputs/mev_transactions.json \
  --output data/doblezero_profiles.json

# 5. Analyze oracle staleness
python oracle_staleness_analyzer.py \
  --slot-jumps data/slot_jump_analysis.json \
  --oracle-updates data/oracle_updates.json \
  --mev-events ../02_mev_detection/outputs/mev_transactions.json \
  --output data/oracle_staleness_analysis.json
```

## Data Format Specifications

### Slot History Format
```json
[
  {
    "slot": 123456789,
    "epoch": 285,
    "leader": "ValidatorPubkey...",
    "produced": true,
    "timestamp": "2026-03-03T12:34:56Z",
    "block_time": 0.412
  }
]
```

### MEV Events Format
```json
[
  {
    "signature": "TransactionSignature...",
    "slot": 123456790,
    "mev_type": "sandwich|arbitrage|liquidation",
    "profit_usd": 123.45,
    "attacker": "AttackerPubkey...",
    "block_leader": "ValidatorPubkey...",
    "oracle_account": "OraclePubkey..."
  }
]
```

### Oracle Updates Format
```json
[
  {
    "slot": 123456789,
    "oracle_account": "OraclePubkey...",
    "oracle_type": "pyth|switchboard|chainlink",
    "asset_symbol": "SOL/USD",
    "price": 25.67,
    "timestamp": "2026-03-03T12:34:56Z"
  }
]
```

## Research Questions Answered

This module helps answer:

1. **Do slot jumps increase MEV opportunities?**
   - Compare MEV value pre-jump vs post-jump
   - Statistical significance tests included

2. **Is DobleZero a profitable strategy?**
   - Economic analysis of skip strategy
   - MEV gains vs missed block rewards

3. **How does oracle staleness enable MEV?**
   - Staleness duration correlation with liquidations
   - Price deviation impact on arbitrage

4. **Can we identify DobleZero validators?**
   - Behavioral profiling with confidence scores
   - Pattern analysis and economic modeling

## Next Steps

After running the analysis:

1. **Review the reports** - Each script generates a human-readable report
2. **Check statistical tests** - Verify significance of findings
3. **Visualize results** - Use the visualization generator (coming soon)
4. **Integrate findings** - Feed results into `11_report_generation`

## Troubleshooting

### Common Issues

**"No data found"**
- Ensure data files exist and are properly formatted
- Check file paths are correct

**"Insufficient data for statistical tests"**
- Need minimum 30 data points for reliable statistics
- Try analyzing a larger epoch range

**"Low DobleZero confidence scores"**
- May indicate lack of DobleZero behavior in dataset
- Or insufficient MEV correlation data

## Academic Context

This research builds on:
- Flash Boys 2.0 (Daian et al.)
- MEV in Proof-of-Stake systems
- Validator economics and incentive design
- Oracle manipulation attacks

## Citations

If using this research, please cite:
```
Solana PAMM MEV Analysis - Slot Jump Impact Study
14_slot_jump_mev_analysis module
March 2026
```

## Contact

For questions or issues:
- Review the main project README
- Check existing analysis outputs in `outputs/`
- Consult the comprehensive report in `11_report_generation/`
