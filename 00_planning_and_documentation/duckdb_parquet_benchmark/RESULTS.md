# DuckDB + Parquet vs pandas + CSV — Benchmark Results

Environment: pandas 3.0.2, duckdb 1.5.2, pyarrow, Linux 6.18.5.
Script: `benchmark.py` — 5 repeats per op, median reported.

## File size (on disk, snappy compression)

| Dataset | CSV | Parquet | Ratio |
|---|---|---|---|
| `oracle_slot_patterns` (659K rows × 4 cols) | 28.9 MB | 2.3 MB | **12.6x smaller** |
| `monte_carlo_harmony` (100K rows × 10 cols) | 10.0 MB | 1.0 MB | **10.0x smaller** |

## oracle_slot_patterns (03_oracle_analysis hot path)

| Operation | pandas+CSV | pandas+Parquet | DuckDB+Parquet |
|---|---:|---:|---:|
| full read | 306.1 ms | 29.0 ms (**10.6x**) | 228.4 ms (1.3x) |
| column subset (2/4 cols) | 166.6 ms | 9.3 ms (**17.9x**) | 14.5 ms (11.5x) |
| filter `oracle_count > 5` | 323.7 ms | 34.1 ms (**9.5x**) | 110.5 ms (2.9x) |
| groupby `amm_oracle` SUM | 320.5 ms | 48.4 ms (6.6x) | 12.0 ms (**26.8x**) |

## monte_carlo_harmony (08_monte_carlo_risk hot path)

| Operation | pandas+CSV | pandas+Parquet | DuckDB+Parquet |
|---|---:|---:|---:|
| full read | 97.1 ms | 9.0 ms (**10.8x**) | 49.0 ms (2.0x) |
| groupby `scenario_name` agg | 106.6 ms | 17.4 ms (6.1x) | 6.9 ms (**15.5x**) |
| filter + groupby | 107.3 ms | 13.0 ms (8.3x) | 5.2 ms (**20.7x**) |

## Takeaways

1. **Disk savings are real and large**: ~10-13x on typical numeric-heavy MEV data. Deployments pulling files from Vercel/S3 shrink proportionally.
2. **pandas + Parquet is the best drop-in replacement for `pd.read_csv`**: 9-18x faster across the board, requires minimal code change (just `.to_parquet` once + swap `read_csv` → `read_parquet`).
3. **DuckDB wins on aggregations / filters that return small results**: 15-27x on groupby-agg. Worth using when the downstream code only needs aggregated numbers (e.g. `12_validator_contagion_analysis`, dashboard cards).
4. **DuckDB loses to pandas+Parquet on full-table reads** because `.df()` conversion has overhead. So: use DuckDB when you can keep the result in SQL-shape; use pandas+Parquet when you need the whole DataFrame in memory anyway.

## Recommended migration strategy (low risk)

1. Add one-time CSV→Parquet conversion step at the end of each pipeline stage that emits a >5 MB CSV (03_oracle_analysis, 08_monte_carlo_risk, 04_validator_analysis).
2. Keep CSV outputs for now (humans, Excel, diffability) — write **both** .csv and .parquet.
3. In downstream consumers, swap `pd.read_csv(path)` → `pd.read_parquet(path.with_suffix('.parquet'))`.
4. For the 4-5 heaviest `groupby`/`merge` call sites, rewrite as `duckdb.sql(...).df()` on the Parquet file.
5. Leave small CSVs (<1 MB, configs, dashboard JSON) untouched.

## Reproduce

```bash
pip install pandas duckdb pyarrow
python3 00_planning_and_documentation/duckdb_parquet_benchmark/benchmark.py
```
