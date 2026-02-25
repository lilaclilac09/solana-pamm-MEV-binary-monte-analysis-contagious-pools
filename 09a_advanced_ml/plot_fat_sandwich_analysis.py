import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set(style="whitegrid")

ROOT = os.path.dirname(os.path.dirname(__file__)) if __file__ else '.'
OUT_DIR = os.path.join(ROOT, '02_mev_detection', 'filtered_output', 'plots')
os.makedirs(OUT_DIR, exist_ok=True)

# Candidate input files (relative to workspace root)
all_class_file = os.path.join(ROOT, '02_mev_detection', 'filtered_output', 'all_mev_with_classification.csv')
fat_file = os.path.join(ROOT, '02_mev_detection', 'filtered_output', 'all_fat_sandwich_only.csv')
# Fallback location used in some runs
fallback_dir = os.path.join(ROOT, '13_mev_comprehensive_analysis', 'outputs', 'from_02_mev_detection')
all_class_file_fallback = os.path.join(fallback_dir, 'all_mev_with_classification.csv')
fat_file_fallback = os.path.join(fallback_dir, 'all_fat_sandwich_only.csv')

# Fallback if files not found
if not os.path.exists(all_class_file) and os.path.exists(all_class_file_fallback):
    all_class_file = all_class_file_fallback
if not os.path.exists(fat_file) and os.path.exists(fat_file_fallback):
    fat_file = fat_file_fallback
if not os.path.exists(all_class_file) and not os.path.exists(fat_file):
    print('ERROR: input files not found. Expected at least one of:')
    print('  -', all_class_file)
    print('  -', fat_file)
    print('Fallback checked:', all_class_file_fallback, fat_file_fallback)
    sys.exit(2)

# Load datasets if available
all_df = None
fat_df = None
if os.path.exists(all_class_file):
    all_df = pd.read_csv(all_class_file)
else:
    print('Warning: all_mev_with_classification.csv not found, will infer from fat file only')

if os.path.exists(fat_file):
    fat_df = pd.read_csv(fat_file)
else:
    print('Warning: all_fat_sandwich_only.csv not found')

# Helper: find likely column names
def find_col(df, candidates):
    for c in candidates:
        if c in df.columns:
            return c
    # try case-insensitive
    cols_lower = {col.lower(): col for col in df.columns}
    for c in candidates:
        if c.lower() in cols_lower:
            return cols_lower[c.lower()]
    return None

# Plot 1: Classification breakdown (if all_df available)
if all_df is not None:
    # detect classification column
    class_col = find_col(all_df, ['classification', 'class', 'label']) or 'classification'
    if class_col not in all_df.columns:
        all_df[class_col] = 'UNKNOWN'
    counts = all_df[class_col].value_counts().rename_axis('classification').reset_index(name='count')
    plt.figure(figsize=(7,4))
    sns.barplot(y='classification', x='count', data=counts, palette='Set2')
    plt.title('MEV Classification Breakdown')
    plt.tight_layout()
    out_path = os.path.join(OUT_DIR, 'classification_breakdown.png')
    plt.savefig(out_path, dpi=150)
    print('Wrote', out_path)
    plt.close()

# Plot 2: Fat sandwich distribution by AMM
if fat_df is not None:
    amm_col = find_col(fat_df, ['amm', 'amm_trade', 'protocol', 'amm_name']) or 'amm'
    profit_col = find_col(fat_df, ['net_profit_sol', 'profit_sol', 'net_profit']) or 'net_profit_sol'
    # Ensure profit exists
    if profit_col not in fat_df.columns:
        fat_df[profit_col] = 0.0

    # Aggregations
    agg = fat_df.groupby(amm_col).agg(
        cases = (profit_col, 'count'),
        total_profit = (profit_col, 'sum'),
        avg_profit = (profit_col, 'mean'),
        max_profit = (profit_col, 'max')
    ).reset_index().sort_values('cases', ascending=False)

    plt.figure(figsize=(9,5))
    sns.barplot(x='cases', y=amm_col, data=agg, palette='Spectral')
    plt.title('Fat Sandwich Cases by AMM (count)')
    plt.tight_layout()
    out_path = os.path.join(OUT_DIR, 'fat_sandwich_by_amm_counts.png')
    plt.savefig(out_path, dpi=150)
    print('Wrote', out_path)
    plt.close()

    plt.figure(figsize=(9,5))
    sns.barplot(x='total_profit', y=amm_col, data=agg, palette='mako')
    plt.title('Fat Sandwich Total Profit by AMM (SOL)')
    plt.tight_layout()
    out_path = os.path.join(OUT_DIR, 'fat_sandwich_by_amm_profit.png')
    plt.savefig(out_path, dpi=150)
    print('Wrote', out_path)
    plt.close()

    # Plot 3: Profit scatter over time/slot if slot or timestamp exists
    slot_col = find_col(fat_df, ['slot', 'block_slot', 'slot_number'])
    ts_col = find_col(fat_df, ['timestamp', 'time', 'block_time'])
    if slot_col and slot_col in fat_df.columns:
        plt.figure(figsize=(10,4))
        sns.scatterplot(x=slot_col, y=profit_col, hue=amm_col, data=fat_df, s=30, alpha=0.8)
        plt.title('Fat Sandwich Profit vs Slot (colored by AMM)')
        plt.legend(bbox_to_anchor=(1.02,1), loc='upper left')
        plt.tight_layout()
        out_path = os.path.join(OUT_DIR, 'profit_vs_slot_scatter.png')
        plt.savefig(out_path, dpi=150)
        print('Wrote', out_path)
        plt.close()
    elif ts_col and ts_col in fat_df.columns:
        # parse timestamp if needed
        try:
            fat_df[ts_col] = pd.to_datetime(fat_df[ts_col])
            plt.figure(figsize=(10,4))
            sns.scatterplot(x=ts_col, y=profit_col, hue=amm_col, data=fat_df, s=30, alpha=0.8)
            plt.title('Fat Sandwich Profit vs Time (colored by AMM)')
            plt.legend(bbox_to_anchor=(1.02,1), loc='upper left')
            plt.tight_layout()
            out_path = os.path.join(OUT_DIR, 'profit_vs_time_scatter.png')
            plt.savefig(out_path, dpi=150)
            print('Wrote', out_path)
            plt.close()
        except Exception:
            pass

    # Plot 4: Top 20 profit cases
    try:
        top20 = fat_df.sort_values(profit_col, ascending=False).head(20)
        plt.figure(figsize=(9,6))
        sns.barplot(x=profit_col, y=amm_col, data=top20, palette='flare')
        plt.title('Top 20 Fat Sandwich Cases (Profit by AMM)')
        plt.tight_layout()
        out_path = os.path.join(OUT_DIR, 'top20_by_amm_profit.png')
        plt.savefig(out_path, dpi=150)
        print('Wrote', out_path)
        plt.close()
    except Exception as e:
        print('Failed to plot top20:', e)

# Plot 5: Multi-hop removed summary (if all_df exists)
if all_df is not None:
    ch = find_col(all_df, ['classification', 'class', 'label']) or 'classification'
    if ch in all_df.columns:
        mh = all_df[all_df[ch].str.contains('MULTI', na=False)]
        if not mh.empty:
            ammcol = find_col(mh, ['amm', 'amm_trade', 'protocol']) or None
            if ammcol and ammcol in mh.columns:
                agg_mh = mh[ammcol].value_counts().reset_index()
                agg_mh.columns = [ammcol, 'count']
                plt.figure(figsize=(7,4))
                sns.barplot(x='count', y=ammcol, data=agg_mh, palette='cool')
                plt.title('Removed: Multi-Hop Cases by AMM')
                plt.tight_layout()
                out_path = os.path.join(OUT_DIR, 'removed_multihop_by_amm.png')
                plt.savefig(out_path, dpi=150)
                print('Wrote', out_path)
                plt.close()

# Write a small summary txt with criteria used
criteria_txt = os.path.join(OUT_DIR, 'filtering_criteria.txt')
with open(criteria_txt, 'w') as fh:
    fh.write('Filtering / Classification Criteria\n')
    fh.write('\nFAT_SANDWICH when:\n')
    fh.write(' - net_profit_sol > 0\n')
    fh.write(' - sandwich pattern verified (front-run, victim, back-run)\n')
    fh.write(' - same signer for front and back run where applicable\n')
    fh.write('\nFAILED_SANDWICH when:\n')
    fh.write(' - net_profit_sol == 0 (no profit)\n')
    fh.write(' - no victim transaction between front and back run\n')
    fh.write('\nMULTI_HOP_ARBITRAGE when:\n')
    fh.write(' - multiple distinct pools/token pairs in one transaction\n')
    fh.write(' - aggregator routing patterns detected\n')

print('Wrote', criteria_txt)
print('\nAll plots saved to:', OUT_DIR)
