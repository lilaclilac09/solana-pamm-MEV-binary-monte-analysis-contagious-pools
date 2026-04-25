# mev_monte_carlo (Rust)

Standalone Rust port of `08_monte_carlo_risk/mev_contagion_monte_carlo.py`.
Runs the three contagion scenarios in parallel, writes per-scenario CSVs
and a summary CSV with the same column schema as the Python output.

## Build

```bash
cargo build --release --manifest-path rust_monte_carlo/Cargo.toml
```

## Run

```bash
./rust_monte_carlo/target/release/mev_monte_carlo \
    --n-sims 100000 \
    --seed 42 \
    --out-dir 08_monte_carlo_risk/outputs/rust
```

CLI flags:
- `--n-sims N` — simulations per scenario (default 100 000).
- `--seed S` — base RNG seed (default 42); per-scenario seed = `S + index`.
- `--oracle-lag-ms F` — override default oracle lag (default 180.0).
- `--scenario all|jito_baseline|bam_privacy|harmony_multibuilder` — pick
  one or run all three (default `all`).
- `--out-dir PATH` — output directory (default
  `08_monte_carlo_risk/outputs/rust`).
- `--tag NAME` — filename suffix; outputs are
  `monte_carlo_<scenario>_<tag>.csv` and `monte_carlo_summary_<tag>.csv`.

## Output schema

Per-scenario CSV columns (identical to Python):
`sim, trigger, cascades, slots_jumped, total_loss, scenario,
scenario_name, infra_gap, high_risk, oracle_lag_ms`.

Summary CSV (one row per scenario): `scenario, n_sims, attack_rate,
attack_rate_pct, mean_cascades, median_cascades, p90_cascades,
p99_cascades, mean_slots_jumped, p90_slots_jumped, p99_slots_jumped,
mean_loss, p90_loss, high_risk_rate, high_risk_pct, mean_infra_gap,
elapsed_ms`.

## Notes

- This is a re-implementation, not a bit-for-bit replay. Rust uses a
  different RNG than NumPy, so individual rows differ even with the same
  seed. The aggregate distributions (`attack_rate_pct`, `mean_loss`,
  cascade percentiles) match the Python output to within sampling noise
  (~1% at N = 100 000).
- The three scenarios are independent so they run in parallel via Rayon.
- Quantiles use linear interpolation (`pandas.Series.quantile()` default).
