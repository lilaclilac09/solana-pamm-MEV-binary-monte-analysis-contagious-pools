# 02 Mev Detection

## Process

- Cell 1: all_detected_attackers; print; groupby
- Cell 2: group; group['total_mev']; get; groupby
- Cell 3: validator_stats; bots_per_validator; mev_types_per_validator; trades_per_validator
- Cell 4: print; attacker_trades['tx_in_slot']

## Results

### Execution Outputs

1. Using cleaned fused table for MEV Analysis #2. Total rows: 5,506,090
2. Available columns: ['slot', 'time', 'validator', 'tx_idx', 'sig', 'signer', 'kind', 'amm_oracle', 'account_updates', 'trades', 'us_since_first_shred', 'amm_trade', 'account_trade', 'is_pool_trade', 'b...
3. Sandwich patterns detected: 26223
4. Total pAMMs with MEV activity: 8
5. pAMMs found: BisonFi, GoonFi, HumidiFi, ObricV2, SolFi, SolFiV2, TesseraV, ZeroFi
6. Total Attackers: 256, Showing Top 10
7. Total Attackers: 589, Showing Top 10
8. Total Attackers: 14, Showing Top 10
9. Total Attackers: 9, Showing Top 9
10. Total Attackers: 171, Showing Top 10
11. Total Attackers: 157, Showing Top 10
12. Total Attackers: 115, Showing Top 10
13. ✓ Per pAMM Top 10 MEV stats (top 10 per pAMM) saved to: per_pamm_top10_mev_with_validator.csv
14. Top 10 Validators by Bot Count:
15. validator  trade_count  bot_count  bot_ratio_%  fat_sandwich  sandwich  front_running  back_running

### Generated Files

- No output files found. Run the notebook to generate outputs.

