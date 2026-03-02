#!/usr/bin/env python3
"""
🎨 MEV Dashboard Chart Examples
Shows exactly how each chart type was created
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns

# ========================================
# 📊 CHART TYPE 1: BAR CHART
# ========================================

print("=" * 60)
print("📊 CHART 1: BAR CHART - MEV Profit by Protocol")
print("=" * 60)

# Step 1: Your data
protocols_data = {
    'Protocol': ['HumidiFi', 'BisonFi', 'GoonFi', 'SolFiV2'],
    'MEV Profit (SOL)': [75.1, 11.232, 7.899, 6.5],
    'Attacks': [593, 182, 258, 176]
}
df = pd.DataFrame(protocols_data)

# Step 2: Create the chart
bar_chart = px.bar(
    df,                           # Your data
    x='Protocol',                 # X-axis: Protocol names
    y='MEV Profit (SOL)',        # Y-axis: Profit values
    title='MEV Profit by Protocol',
    color='MEV Profit (SOL)',    # Color bars by value
    color_continuous_scale='Purples'  # Purple color scheme
)

# Step 3: Style it
bar_chart.update_layout(
    plot_bgcolor='white',         # White background
    paper_bgcolor='white',
    font={'family': 'Arial', 'color': '#2D3436'}
)

print("✅ Bar chart created!")
print(f"   X-axis: {df['Protocol'].tolist()}")
print(f"   Y-axis: {df['MEV Profit (SOL)'].tolist()}")
print()

# ========================================
# 📊 CHART TYPE 2: PIE CHART
# ========================================

print("=" * 60)
print("🥧 CHART 2: PIE CHART - Profit Distribution")
print("=" * 60)

pie_chart = px.pie(
    df,
    values='MEV Profit (SOL)',   # Size of slices
    names='Protocol',             # Labels
    title='Profit Share Distribution',
    hole=0.4,                     # Makes it a donut chart
    color_discrete_sequence=px.colors.sequential.RdPu
)

print("✅ Pie chart created!")
print(f"   Slices: {df['Protocol'].tolist()}")
print(f"   Values: {df['MEV Profit (SOL)'].tolist()}")
print()

# ========================================
# 📊 CHART TYPE 3: HEATMAP
# ========================================

print("=" * 60)
print("🔥 CHART 3: HEATMAP - Attacker Overlap")
print("=" * 60)

# Contagion matrix (shared attackers between pools)
contagion_data = pd.DataFrame({
    'HumidiFi': [167, 44, 43],
    'BisonFi': [44, 182, 42],
    'GoonFi': [43, 42, 258]
}, index=['HumidiFi', 'BisonFi', 'GoonFi'])

heatmap = px.imshow(
    contagion_data,
    text_auto=True,              # Show numbers in cells
    title='Attacker Overlap Heatmap',
    color_continuous_scale='RdPu',
    labels=dict(x="Target Pool", y="Source Pool", color="Shared Attackers")
)

print("✅ Heatmap created!")
print(f"   Matrix size: {contagion_data.shape}")
print(f"   Example: HumidiFi-BisonFi shared attackers = {contagion_data.loc['HumidiFi', 'BisonFi']}")
print()

# ========================================
# 📊 CHART TYPE 4: SCATTER PLOT
# ========================================

print("=" * 60)
print("⚡ CHART 4: SCATTER PLOT - Attacks vs Profit")
print("=" * 60)

scatter = px.scatter(
    df,
    x='Attacks',                 # X-axis
    y='MEV Profit (SOL)',       # Y-axis
    size='MEV Profit (SOL)',    # Bubble size
    color='Protocol',            # Color by protocol
    title='Attack Frequency vs MEV Profit',
    hover_data=['Protocol']      # Show on hover
)

print("✅ Scatter plot created!")
print(f"   Points: {len(df)} protocols")
print(f"   HumidiFi: {df.loc[0, 'Attacks']} attacks → {df.loc[0, 'MEV Profit (SOL)']} SOL")
print()

# ========================================
# 📊 CHART TYPE 5: NETWORK GRAPH
# ========================================

print("=" * 60)
print("🕸️ CHART 5: NETWORK GRAPH - Pool Connections")
print("=" * 60)

# Step 1: Create network
G = nx.Graph()
protocols = ['HumidiFi', 'BisonFi', 'GoonFi', 'SolFiV2']
for p in protocols:
    G.add_node(p)

# Add connections (edges)
connections = [
    ('HumidiFi', 'BisonFi', 44),   # 44 shared attackers
    ('HumidiFi', 'GoonFi', 43),
    ('BisonFi', 'GoonFi', 42),
    ('GoonFi', 'SolFiV2', 40)
]
for source, target, weight in connections:
    G.add_edge(source, target, weight=weight)

# Step 2: Calculate node positions
pos = nx.spring_layout(G, k=0.5, iterations=50)

# Step 3: Create edge lines
edge_x = []
edge_y = []
for edge in G.edges():
    x0, y0 = pos[edge[0]]
    x1, y1 = pos[edge[1]]
    edge_x.extend([x0, x1, None])  # None creates a break
    edge_y.extend([y0, y1, None])

edge_trace = go.Scatter(
    x=edge_x, y=edge_y,
    line=dict(width=2, color='#E0E0E0'),
    mode='lines',
    hoverinfo='none'
)

# Step 4: Create nodes
node_x = [pos[node][0] for node in G.nodes()]
node_y = [pos[node][1] for node in G.nodes()]

node_trace = go.Scatter(
    x=node_x, y=node_y,
    mode='markers+text',
    marker=dict(size=35, color='#6C63FF', line=dict(width=2, color='white')),
    text=list(G.nodes()),
    textposition="top center"
)

# Step 5: Combine into figure
network_graph = go.Figure(
    data=[edge_trace, node_trace],
    layout=go.Layout(
        title='Pool Coordination Network',
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor='white'
    )
)

print("✅ Network graph created!")
print(f"   Nodes: {G.number_of_nodes()} protocols")
print(f"   Edges: {G.number_of_edges()} connections")
print(f"   Example: HumidiFi ↔ BisonFi (44 shared attackers)")
print()

# ========================================
# 📊 CHART TYPE 6: DATA TABLE
# ========================================

print("=" * 60)
print("📋 CHART 6: DATA TABLE - Top Attackers")
print("=" * 60)

attackers = pd.DataFrame({
    'Attacker': ['YubQzu18...', 'YubVwWeg...', 'AEB9dXBox...'],
    'Profit (SOL)': [16.731, 4.860, 3.888],
    'Attacks': [2, 63, 864]
})

print("✅ Data table created!")
print(attackers.to_string(index=False))
print()

# ========================================
# 📊 CHART TYPE 7: CORRECTED VAL-AMM-3
# MEV Attack Pattern Comparison (Post-FP Elimination)
# ========================================

print("=" * 60)
print("🎯 CHART 7: MEV ATTACK PATTERNS - Corrected Data")
print("=" * 60)

# Corrected data after false positive elimination
# Total MEV trades = 650 (down from ~2,131)
mev_patterns_data = pd.DataFrame({
    'Pattern': ['Fat Sandwich', 'Back-Running (DeezNode)', 'Classic Sandwich', 
                'Front-Running', 'Cross-Slot (2Fast)'],
    'Count': [312, 135, 95, 62, 46],
    'Percentage': [48.0, 20.8, 14.6, 9.5, 7.1]
})

# Sort by count descending
mev_patterns_data = mev_patterns_data.sort_values('Count', ascending=False)

# Define colors (pink/red for Fat Sandwich and Front-Running, purple for Back-Running, teal/cyan for others)
color_map = {
    'Fat Sandwich': '#FF6B9D',           # Pink
    'Front-Running': '#FF4757',          # Red
    'Back-Running (DeezNode)': '#9B59B6', # Purple
    'Classic Sandwich': '#1ABC9C',       # Teal
    'Cross-Slot (2Fast)': '#3498DB'      # Cyan
}

colors = [color_map[pattern] for pattern in mev_patterns_data['Pattern']]

# Create figure with subplots (1 row, 2 columns)
fig = make_subplots(
    rows=1, cols=2,
    subplot_titles=('MEV Pattern Comparison: Trade Counts', 'MEV Pattern Distribution'),
    specs=[[{"type": "bar"}, {"type": "pie"}]],
    horizontal_spacing=0.15
)

# Add horizontal bar chart
fig.add_trace(
    go.Bar(
        y=mev_patterns_data['Pattern'],
        x=mev_patterns_data['Count'],
        orientation='h',
        marker=dict(color=colors),
        text=mev_patterns_data['Count'],
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Count: %{x}<br>Percentage: %{customdata}%<extra></extra>',
        customdata=mev_patterns_data['Percentage'],
        showlegend=False
    ),
    row=1, col=1
)

# Add pie chart
fig.add_trace(
    go.Pie(
        labels=mev_patterns_data['Pattern'],
        values=mev_patterns_data['Count'],
        marker=dict(colors=colors),
        textinfo='percent+label',
        textposition='auto',
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>',
        hole=0.3  # Make it a donut chart
    ),
    row=1, col=2
)

# Update layout
fig.update_xaxes(title_text="Number of Trades", range=[0, 350], row=1, col=1)
fig.update_yaxes(title_text="Attack Pattern", row=1, col=1)

fig.update_layout(
    title_text="Figure VAL-AMM-3: MEV Attack Pattern Comparison Across Validator-AMM Pairs (Post-FP Elimination)",
    title_font_size=14,
    showlegend=False,
    height=500,
    width=1400,
    plot_bgcolor='white',
    paper_bgcolor='white',
    font={'family': 'Arial', 'color': '#2D3436'}
)

# Alternative: Create separate matplotlib/seaborn version for saving as PNG
print("Creating matplotlib version for PNG export...")

# Set up the figure with two subplots
plt.style.use('seaborn-v0_8-darkgrid')
fig_mpl, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Left: Horizontal bar chart
bars = ax1.barh(mev_patterns_data['Pattern'], mev_patterns_data['Count'], color=colors)
ax1.set_xlabel('Number of Trades', fontsize=12, fontweight='bold')
ax1.set_ylabel('Attack Pattern', fontsize=12, fontweight='bold')
ax1.set_title('MEV Pattern Comparison: Trade Counts', fontsize=13, fontweight='bold', pad=15)
ax1.set_xlim(0, 350)
ax1.grid(axis='x', alpha=0.3, linestyle='--')

# Add value labels on bars
for i, (pattern, count) in enumerate(zip(mev_patterns_data['Pattern'], mev_patterns_data['Count'])):
    ax1.text(count + 5, i, str(count), va='center', fontsize=11, fontweight='bold')

# Right: Pie chart
wedges, texts, autotexts = ax2.pie(
    mev_patterns_data['Count'], 
    labels=mev_patterns_data['Pattern'],
    autopct='%1.1f%%',
    colors=colors,
    startangle=90,
    textprops={'fontsize': 10, 'fontweight': 'bold'},
    wedgeprops={'edgecolor': 'white', 'linewidth': 2}
)

# Make percentage text more visible
for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontsize(11)

ax2.set_title('MEV Pattern Distribution', fontsize=13, fontweight='bold', pad=15)

# Overall title
fig_mpl.suptitle(
    'Figure VAL-AMM-3: MEV Attack Pattern Comparison Across Validator-AMM Pairs\n(Post-False Positive Elimination: 650 Total MEV Trades)',
    fontsize=14,
    fontweight='bold',
    y=0.98
)

plt.tight_layout(rect=[0, 0, 1, 0.95])

# Save the figure
output_path = '/Users/aileen/Downloads/pamm/solana-pamm-analysis/solana-pamm-MEV-binary-monte-analysis-contagious-pools/12_live_dashboard/corrected_val_amm_3.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
print(f"✅ Figure saved to: {output_path}")

print()
print("📊 CORRECTED DATA SUMMARY:")
print(f"   Total MEV Trades: {mev_patterns_data['Count'].sum()}")
print(f"   Most Common Pattern: {mev_patterns_data.iloc[0]['Pattern']} ({mev_patterns_data.iloc[0]['Count']} trades, {mev_patterns_data.iloc[0]['Percentage']}%)")
print()
print("   Pattern Breakdown:")
for _, row in mev_patterns_data.iterrows():
    print(f"     • {row['Pattern']}: {row['Count']} trades ({row['Percentage']}%)")
print()

# ========================================
# 🎯 SUMMARY
# ========================================

print("=" * 60)
print("🎯 SUMMARY: How Your Dashboard Works")
print("=" * 60)
print()
print("1. 📊 BAR CHART → px.bar(df, x='col1', y='col2')")
print("   Used for: Comparing values across categories")
print()
print("2. 🥧 PIE CHART → px.pie(df, values='col', names='labels')")
print("   Used for: Showing proportions/percentages")
print()
print("3. 🔥 HEATMAP → px.imshow(matrix, text_auto=True)")
print("   Used for: Showing intensity in grid format")
print()
print("4. ⚡ SCATTER → px.scatter(df, x='col1', y='col2', size='col3')")
print("   Used for: Showing relationships between variables")
print()
print("5. 🕸️ NETWORK → go.Figure(data=[edges, nodes])")
print("   Used for: Showing connections/relationships")
print()
print("6. 📋 TABLE → dash_table.DataTable(data, columns)")
print("   Used for: Displaying raw data")
print()
print("7. 🎯 COMBINED CHARTS → make_subplots() + matplotlib")
print("   Used for: Multi-panel visualizations with corrected data")
print()

print("=" * 60)
print("🌐 YOUR LIVE DASHBOARD: https://mev.aileena.xyz")
print("=" * 60)
print()
print("The dashboard combines ALL these chart types to visualize:")
print("  ✓ 112.9 SOL in MEV profits")
print("  ✓ 1,617 attacks across 8 protocols")
print("  ✓ 179 unique attackers")
print("  ✓ 742 validators involved")
print("  ✓ Cross-pool contagion patterns")
print()
print("All data is interactive:")
print("  → Hover for details")
print("  → Click to filter")
print("  → Zoom and pan")
print()
print("=" * 60)

# ========================================
# 💡 HOW TO CREATE YOUR OWN CHART
# ========================================

print()
print("💡 QUICK RECIPE: Create Your Own Chart")
print("=" * 60)
print()
print("Step 1: Prepare your data")
print("--------")
print("my_data = {")
print("    'Category': ['A', 'B', 'C'],")
print("    'Value': [10, 20, 15]")
print("}")
print("df = pd.DataFrame(my_data)")
print()
print("Step 2: Create the chart")
print("--------")
print("chart = px.bar(df, x='Category', y='Value')")
print()
print("Step 3: Display it")
print("--------")
print("chart.show()  # Opens in browser")
print()
print("That's it! 🎉")
print()
print("=" * 60)

if __name__ == '__main__':
    print()
    print("🚀 Want to see these charts?")
    print()
    print("Option 1: Visit your live dashboard")
    print("   → https://mev.aileena.xyz")
    print()
    print("Option 2: Run locally")
    print("   → python mev_dashboard.py")
    print("   → Open http://localhost:8050")
    print()
    print("Option 3: Test individual charts")
    print("   → Uncomment the lines below:")
    print()
    print("   # bar_chart.show()")
    print("   # pie_chart.show()")
    print("   # heatmap.show()")
    print("   # scatter.show()")
    print("   # network_graph.show()")
    print()
    print("=" * 60)
