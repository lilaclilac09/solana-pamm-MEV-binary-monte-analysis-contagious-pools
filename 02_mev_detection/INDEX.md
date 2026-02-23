
# ============================================================================
# POOL DATA CONSOLIDATION - COMPLETE INDEX
# ============================================================================
# Generated from: per_pamm_all_mev_with_validator.csv
# Total MEV Events: 1,501
# Analysis Pools: 8
# Total Validators: 299
# Total Unique Attackers: 880

## FILES GENERATED

### 1. POOL_SUMMARY.csv
   - Pool-level statistics
   - Columns: pool, unique_attackers, unique_validators, total_mev_events, 
             total_fat_sandwiches, total_sandwiches, total_front_runs, 
             total_back_runs, total_profit_sol, total_cost_sol, 
             net_profit_sol, avg_profit_per_event, high_confidence_events, 
             medium_confidence_events
   - Rows: 8

### 2. VALIDATOR_POOL_PARTICIPATION.csv
   - Validator activity broken down by pool
   - Columns: pool, validator, attacker_count, total_profit, net_profit, fat_sandwiches
   - Rows: 637

### 3. ATTACKER_KEYS_BY_POOL.csv
   - All attacker addresses with per-pool performance
   - Columns: pool, attacker_key, event_count, total_profit, net_profit
   - Rows: 1501

### 4. VALIDATOR_KEYS.txt
   - Complete list of unique validator addresses
   - Count: 299

## POOL BREAKDOWN


### BisonFi
   - MEV Events: 182
   - Unique Attackers: 182
   - Unique Validators: 92
   - Fat Sandwiches: 2595
   - Total Profit: 12.4800 SOL
   - Net Profit: 11.2320 SOL

### GoonFi
   - MEV Events: 258
   - Unique Attackers: 258
   - Unique Validators: 106
   - Fat Sandwiches: 1892
   - Total Profit: 8.7800 SOL
   - Net Profit: 7.8990 SOL

### HumidiFi
   - MEV Events: 593
   - Unique Attackers: 593
   - Unique Validators: 189
   - Fat Sandwiches: 16828
   - Total Profit: 83.4820 SOL
   - Net Profit: 75.1290 SOL

### ObricV2
   - MEV Events: 13
   - Unique Attackers: 13
   - Unique Validators: 6
   - Fat Sandwiches: 34
   - Total Profit: 0.1200 SOL
   - Net Profit: 0.1080 SOL

### SolFi
   - MEV Events: 6
   - Unique Attackers: 6
   - Unique Validators: 5
   - Fat Sandwiches: 3
   - Total Profit: 0.0000 SOL
   - Net Profit: 0.0000 SOL

### SolFiV2
   - MEV Events: 176
   - Unique Attackers: 176
   - Unique Validators: 84
   - Fat Sandwiches: 1733
   - Total Profit: 8.3500 SOL
   - Net Profit: 7.5120 SOL

### TesseraV
   - MEV Events: 157
   - Unique Attackers: 157
   - Unique Validators: 83
   - Fat Sandwiches: 1815
   - Total Profit: 8.7000 SOL
   - Net Profit: 7.8300 SOL

### ZeroFi
   - MEV Events: 116
   - Unique Attackers: 116
   - Unique Validators: 72
   - Fat Sandwiches: 690
   - Total Profit: 3.0880 SOL
   - Net Profit: 2.7780 SOL
