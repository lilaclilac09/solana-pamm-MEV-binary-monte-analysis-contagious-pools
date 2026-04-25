#!/usr/bin/env bash
#
# End-to-end runner for the optimized analysis pipeline:
#   1. Build and run the Rust Monte Carlo simulator.
#   2. Convert oracle CSVs -> Parquet.
#   3. Convert 02_mev_detection/filtered_output CSVs -> Parquet.
#   4. Run the Parquet+DuckDB oracle burst report generator.
#   5. Run the vectorized contagion visualizer.
#   6. Run the vectorized validator contagion analyzer.
#
# Each step is a separate file from its original; nothing is overwritten
# in place. Prints a final timing table.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_ROOT"

# Pretty timer that captures the wall-clock of a single command.
declare -A TIMINGS
declare -a STEP_ORDER

run_step() {
    local label="$1"
    shift
    echo
    echo "─── ${label} ───"
    local start
    start=$(date +%s%3N)
    "$@"
    local end
    end=$(date +%s%3N)
    local elapsed=$((end - start))
    TIMINGS[$label]=$elapsed
    STEP_ORDER+=("$label")
    echo "  → ${label}: ${elapsed} ms"
}

# Step 1: Rust Monte Carlo
run_step "rust_build" \
    cargo build --release --manifest-path rust_monte_carlo/Cargo.toml --quiet

run_step "rust_monte_carlo" \
    ./rust_monte_carlo/target/release/mev_monte_carlo \
        --n-sims 100000 --seed 42 \
        --out-dir 08_monte_carlo_risk/outputs/rust

# Step 2: oracle CSVs -> Parquet
run_step "convert_oracle_csv_to_parquet" \
    python3 03_oracle_analysis/convert_csv_to_parquet.py

# Step 3: filtered_output CSVs -> Parquet
run_step "convert_filtered_output_to_parquet" \
    python3 02_mev_detection/convert_filtered_output_to_parquet.py

# Step 4: Parquet+DuckDB oracle burst report
run_step "burst_report_parquet" \
    python3 11_report_generation/generate_oracle_burst_analysis_parquet.py

# Step 5: vectorized contagion visualizer.
# The script reads contagion_report.json from cwd, so symlink it temporarily.
ln -sf 08_monte_carlo_risk/contagion_report.json contagion_report.json
trap 'rm -f "${REPO_ROOT}/contagion_report.json"' EXIT
run_step "contagion_visualizer_optimized" \
    python3 08_monte_carlo_risk/generate_contagion_visualizations_optimized.py

# Step 6: vectorized validator contagion analyzer
run_step "validator_contagion_optimized" \
    python3 04_validator_analysis/12_validator_contagion_analysis_optimized.py

# Summary
echo
echo "════════════════════════════════════════════════════════════"
echo "TIMING SUMMARY (ms)"
echo "════════════════════════════════════════════════════════════"
local_total=0
for step in "${STEP_ORDER[@]}"; do
    printf "  %-40s %8d ms\n" "$step" "${TIMINGS[$step]}"
    local_total=$((local_total + TIMINGS[$step]))
done
printf "  %-40s %8d ms\n" "(total)" "$local_total"
echo "════════════════════════════════════════════════════════════"
