#!/usr/bin/env python3
"""
🎨 MEV Dashboard Chart Examples
Shows exactly how each chart type was created
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import networkx as nx

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
