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

# Step 7: smoke-load optimized pool coordination + contagious vulnerability
# analyzers (their output is exercised against the available CSVs).
run_step "pool_coordination_optimized" \
    python3 -c "
import importlib.util, pandas as pd
spec = importlib.util.spec_from_file_location('m','06_pool_analysis/pool_coordination_network_analysis_optimized.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
df = pd.read_csv('02_mev_detection/filtered_output/per_pamm_all_mev_with_validator.csv').rename(columns={'attacker_signer':'signer','amm_trade':'pool'})
a = m.PoolCoordinationAnalyzerOptimized(); a.mev_data = df
g = a.build_attacker_pool_graph(df, min_interaction_weight=2)
print(f'  graph: {g.number_of_nodes()} nodes, {g.number_of_edges()} edges')
"

run_step "contagious_vulnerability_optimized" \
    python3 -c "
import importlib.util
spec = importlib.util.spec_from_file_location('m','13_mev_comprehensive_analysis/contagious_vulnerability_analyzer_optimized.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
a = m.ContagiousVulnerabilityAnalyzerOptimized()
a.load_mev_data('02_mev_detection/filtered_output/all_mev_with_classification.csv')
trig = a.identify_trigger_pool(a.mev_data)
print(f'  trigger pool: {trig[chr(34)+\"trigger_pool\"+chr(34)] if False else trig[\"trigger_pool\"]}')
"

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
