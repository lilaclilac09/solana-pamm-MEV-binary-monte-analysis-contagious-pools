#!/usr/bin/env python3
"""
Simple visualization script for MEV pool results.
Generates PNGs into `02_mev_detection/visualizations/`.
"""
import os
import sys
import math
import pandas as pd
import matplotlib.pyplot as plt

OUTDIR = '02_mev_detection/visualizations'
os.makedirs(OUTDIR, exist_ok=True)

def safe_read_csv(path):
    if not os.path.exists(path):
        print(f"ERROR: missing file: {path}")
        return None
    return pd.read_csv(path)

def plot_pool_net_profit(pool_df):
    path = os.path.join(OUTDIR, 'pool_net_profit.png')
    df = pool_df.sort_values('net_profit_sol', ascending=False)
    plt.figure(figsize=(9,5))
    plt.bar(df['pool'], df['net_profit_sol'], color='C2')
    plt.ylabel('Net profit (SOL)')
    plt.title('Net MEV Profit by Pool')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"Saved: {path}")

def plot_pool_mev_types(pool_df):
    path = os.path.join(OUTDIR, 'pool_mev_type_counts.png')
    df = pool_df.set_index('pool')
    types = ['total_fat_sandwiches', 'total_sandwiches', 'total_front_runs', 'total_back_runs']
    # ensure types exist
    for t in types:
        if t not in df.columns:
            df[t] = 0
    df[types].plot(kind='bar', stacked=True, figsize=(10,5), colormap='tab20')
    plt.ylabel('Count')
    plt.title('MEV Type Counts by Pool')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"Saved: {path}")

def plot_top_attackers(attacker_df, top_n=20):
    path = os.path.join(OUTDIR, 'top_attackers_by_net_profit.png')
    agg = attacker_df.groupby('attacker_key')['net_profit'].sum().abs().sort_values(ascending=False).head(top_n)
    plt.figure(figsize=(10,6))
    agg.plot(kind='bar', color='C3')
    plt.ylabel('Net profit (SOL)')
    plt.title(f'Top {top_n} Attackers by Net Profit')
    plt.xticks(rotation=65, ha='right')
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"Saved: {path}")

def plot_validator_heatmap(val_pool_df, top_validators=20):
    path = os.path.join(OUTDIR, 'validator_pool_heatmap.png')
    # pivot validators x pool with net_profit
    pivot = val_pool_df.pivot_table(index='validator', columns='pool', values='net_profit', aggfunc='sum', fill_value=0)
    # take top validators by total net profit
    pivot['total'] = pivot.sum(axis=1)
    pivot = pivot.sort_values('total', ascending=False).head(top_validators)
    pivot = pivot.drop(columns=['total'])
    data = pivot.values
    plt.figure(figsize=(10,6))
    plt.imshow(data, aspect='auto', cmap='Reds')
    plt.colorbar(label='Net profit (SOL)')
    plt.yticks(range(len(pivot.index)), [p[:10] + '...' if len(p)>10 else p for p in pivot.index])
    plt.xticks(range(len(pivot.columns)), pivot.columns, rotation=45, ha='right')
    plt.title(f'Top {top_validators} Validators: Net Profit by Pool')
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"Saved: {path}")

def plot_contagion_network(attacker_df, pool_df, top_attacker_n=50):
    try:
        import networkx as nx
    except Exception:
        print('networkx not available; skipping network plot')
        return
    path = os.path.join(OUTDIR, 'pool_attacker_network.png')
    # choose top attackers overall
    agg = attacker_df.groupby('attacker_key')['net_profit'].sum().abs().sort_values(ascending=False).head(top_attacker_n)
    top_attackers = set(agg.index)
    G = nx.Graph()
    # add pools
    for p in pool_df['pool']:
        G.add_node(p, bipartite=0)
    # add attacker nodes and edges weighted by net_profit
    for _, row in attacker_df.iterrows():
        if row['attacker_key'] in top_attackers:
            G.add_node(row['attacker_key'], bipartite=1)
            w = abs(row['net_profit']) if not math.isnan(row['net_profit']) else 0.0
            if w > 0:
                G.add_edge(row['attacker_key'], row['pool'], weight=w)
    if G.number_of_edges() == 0:
        print('No edges for network plot; skipping')
        return
    plt.figure(figsize=(12,10))
    pos = nx.spring_layout(G, k=0.6, iterations=50)
    # draw nodes
    pools = [n for n,d in G.nodes(data=True) if d.get('bipartite')==0]
    attackers = [n for n,d in G.nodes(data=True) if d.get('bipartite')==1]
    nx.draw_networkx_nodes(G, pos, nodelist=pools, node_color='C0', node_size=300, label='Pools')
    nx.draw_networkx_nodes(G, pos, nodelist=list(attackers), node_color='C1', node_size=80, label='Attackers')
    # edges with widths
    weights = [d['weight'] for (u,v,d) in G.edges(data=True)]
    maxw = max(weights)
    widths = [max(0.5, 4*w/maxw) for w in weights]
    nx.draw_networkx_edges(G, pos, width=widths, alpha=0.7)
    # labels for pools only (avoid clutter)
    labels = {n:n for n in pools}
    nx.draw_networkx_labels(G, pos, labels, font_size=9)
    plt.title('Pool-Attacker Network (top attackers)')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"Saved: {path}")


def main():
    pool_path = '02_mev_detection/POOL_SUMMARY.csv'
    val_pool_path = '02_mev_detection/VALIDATOR_POOL_PARTICIPATION.csv'
    attacker_path = '02_mev_detection/ATTACKER_KEYS_BY_POOL.csv'

    pool_df = safe_read_csv(pool_path)
    val_pool_df = safe_read_csv(val_pool_path)
    attacker_df = safe_read_csv(attacker_path)

    if pool_df is None:
        sys.exit(1)

    # Ensure numeric columns
    for col in ['net_profit_sol','total_profit_sol','total_cost_sol']:
        if col in pool_df.columns:
            pool_df[col] = pd.to_numeric(pool_df[col], errors='coerce').fillna(0)
    # plot
    plot_pool_net_profit(pool_df)
    plot_pool_mev_types(pool_df)

    if attacker_df is not None:
        # ensure numeric
        if 'net_profit' not in attacker_df.columns and 'net_profit' in attacker_df.columns:
            attacker_df['net_profit'] = pd.to_numeric(attacker_df['net_profit'], errors='coerce').fillna(0)
        # some outputs use net_profit or net_profit_sol naming
        if 'net_profit' not in attacker_df.columns and 'net_profit_sol' in attacker_df.columns:
            attacker_df['net_profit'] = pd.to_numeric(attacker_df['net_profit_sol'], errors='coerce').fillna(0)
        else:
            attacker_df['net_profit'] = pd.to_numeric(attacker_df.get('net_profit', 0), errors='coerce').fillna(0)
        plot_top_attackers(attacker_df)
        plot_contagion_network(attacker_df, pool_df)

    if val_pool_df is not None:
        # ensure numeric
        val_pool_df['net_profit'] = pd.to_numeric(val_pool_df.get('net_profit', 0), errors='coerce').fillna(0)
        plot_validator_heatmap(val_pool_df)

    print('\nAll visualizations saved to:', OUTDIR)

if __name__ == '__main__':
    main()
