"""
Interactive Plotly visualizations for Section 5c with click-to-view raw data.
"""
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import json

def load_viz_data():
    """Load visualization data from JSON file."""
    try:
        with open('visualization_data.json', 'r') as f:
            return json.load(f)
    except:
        # Fallback to default data
        return {
            "token_pair_fragility": {
                "headline_percent": 39.5,
                "pump_wsol_label": "High-Risk Pool (HumidiFi)",
            },
            "oracle_latency_window": {
                "headline_latency_seconds": 0.4,
                "headline_trade_percent": 39.5,
                "pool_latencies_us": {
                    "GoonFi": 322161,
                    "HumidiFi": 341033,
                    "SolFiV2": 350892
                }
            },
            "mev_battlefield": {
                "pool_profits_sol": {
                    "HumidiFi": 75.1,
                    "BisonFi": 11.2,
                    "GoonFi": 7.9,
                    "TesseraV": 7.8,
                    "SolFiV2": 7.5,
                    "ZeroFi": 2.8,
                    "ObricV2": 0.1
                },
                "profit_share_percent": {
                    "HumidiFi": 66.8,
                    "BisonFi": 10.0,
                    "GoonFi": 7.0,
                    "TesseraV": 7.0,
                    "SolFiV2": 6.7,
                    "ZeroFi": 2.5,
                    "ObricV2": 0.1
                }
            }
        }

def create_token_pair_fragility_interactive():
    """Create interactive scatter plot for token pair fragility."""
    data = load_viz_data()
    section = data.get("token_pair_fragility", {})
    
    fig = go.Figure()
    
    # Add scatter points
    points_data = section.get("points", {
        "pump_wsol": [1.5, 8.8],
        "safe_pair": [7.2, 3.0],
        "safe_pairs": [8.1, 2.6]
    })
    
    # High-risk pool (PUMP/WSOL)
    fig.add_trace(go.Scatter(
        x=[points_data["pump_wsol"][0]],
        y=[points_data["pump_wsol"][1]],
        mode='markers',
        marker=dict(size=40, color='#e74c3c', line=dict(width=3, color='white')),
        name=section.get("pump_wsol_label", "High-Risk Pool"),
        hovertemplate='<b>%{fullData.name}</b><br>Liquidity Depth: %{x:.1f}<br>Volatility: %{y:.1f}<br>Attack Share: 39.5%<extra></extra>',
        customdata=[["HumidiFi", 39.5, 593, 75.1]]
    ))
    
    # Safe pair
    fig.add_trace(go.Scatter(
        x=[points_data["safe_pair"][0]],
        y=[points_data["safe_pair"][1]],
        mode='markers',
        marker=dict(size=25, color='#27ae60', line=dict(width=2, color='white')),
        name=section.get("safe_pair_label", "Diversified Pools"),
        hovertemplate='<b>%{fullData.name}</b><br>Liquidity Depth: %{x:.1f}<br>Volatility: %{y:.1f}<extra></extra>',
        customdata=[["BisonFi", 10.0, 182, 11.2]]
    ))
    
    # Safe pairs cluster
    fig.add_trace(go.Scatter(
        x=[points_data["safe_pairs"][0]],
        y=[points_data["safe_pairs"][1]],
        mode='markers',
        marker=dict(size=22, color='#2ecc71', line=dict(width=2, color='white')),
        name=section.get("safe_pairs_label", "Low-Risk Pools"),
        hovertemplate='<b>%{fullData.name}</b><br>Liquidity Depth: %{x:.1f}<br>Volatility: %{y:.1f}<extra></extra>',
        customdata=[["GoonFi+Others", 50.5, 730, 26.4]]
    ))
    
    fig.update_layout(
        title=dict(
            text=f"<b>Token Pair Fragility: {section.get('headline_percent', 39.5):.1f}% Attack Concentration</b><br><sub>Click on points to view detailed pool data</sub>",
            font=dict(size=18),
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(
            title='Liquidity Depth',
            range=[0, 10],
            tickvals=[1, 9],
            ticktext=['Low', 'High']
        ),
        yaxis=dict(
            title='Volatility/Price Impact',
            range=[0, 10],
            tickvals=[1, 9],
            ticktext=['Low', 'High']
        ),
        hovermode='closest',
        height=500,
        plot_bgcolor='#f9fafb',
        paper_bgcolor='white',
        shapes=[
            # Quadrant dividers
            dict(type='line', x0=5, y0=0, x1=5, y1=10, line=dict(color='gray', width=1, dash='dash')),
            dict(type='line', x0=0, y0=5, x1=10, y1=5, line=dict(color='gray', width=1, dash='dash'))
        ]
    )
    
    return fig

def create_oracle_latency_interactive():
    """Create interactive bar chart for oracle latency."""
    data = load_viz_data()
    section = data.get("oracle_latency_window", {})
    pool_latencies = section.get("pool_latencies_us", {})
    
    # Convert to DataFrame
    df = pd.DataFrame([
        {"Pool": pool, "Latency (ms)": latency_us / 1000, "Latency (s)": latency_us / 1000000}
        for pool, latency_us in pool_latencies.items()
    ]).sort_values("Latency (ms)", ascending=False)
    
    fig = go.Figure()
    
    # Add bars with color gradient
    colors = ['#dc2626' if i == 0 else '#f59e0b' if i == 1 else '#3b82f6' for i in range(len(df))]
    
    fig.add_trace(go.Bar(
        x=df['Pool'],
        y=df['Latency (ms)'],
        marker=dict(color=colors, line=dict(width=0)),
        text=df['Latency (s)'].apply(lambda x: f"{x:.2f}s"),
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Latency: %{y:.1f}ms (%{text})<extra></extra>',
        customdata=df[['Latency (ms)', 'Latency (s)']].values
    ))
    
    fig.update_layout(
        title=dict(
            text=f"<b>Oracle Latency Window: {section.get('headline_latency_seconds', 0.4):.1f}s Max Latency</b><br><sub>Click on bars to view detailed timing data</sub>",
            font=dict(size=18),
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(title='Pool Protocol'),
        yaxis=dict(title='Median Latency (milliseconds)'),
        height=450,
        plot_bgcolor='#f9fafb',
        paper_bgcolor='white',
        showlegend=False,
        annotations=[
            dict(
                x=0.5,
                y=1.15,
                xref='paper',
                yref='paper',
                text=f'<b>{section.get("headline_trade_percent", 39.5):.1f}%</b> of trades occur within oracle update windows',
                showarrow=False,
                font=dict(size=13, color='#dc2626'),
                bgcolor='#fef2f2',
                borderpad=8
            )
        ]
    )
    
    return fig

def create_mev_battlefield_interactive():
    """Create interactive pie + bar chart for MEV battlefield."""
    data = load_viz_data()
    section = data.get("mev_battlefield", {})
    
    profits = section.get("pool_profits_sol", {})
    shares = section.get("profit_share_percent", {})
    
    # Create DataFrame
    df = pd.DataFrame({
        "Pool": list(profits.keys()),
        "Profit (SOL)": list(profits.values()),
        "Share (%)": list(shares.values())
    }).sort_values("Profit (SOL)", ascending=False)
    
    # Create subplot with pie and bar
    from plotly.subplots import make_subplots
    
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{"type": "pie"}, {"type": "bar"}]],
        subplot_titles=("Profit Share Distribution", "Total Profit by Pool"),
        column_widths=[0.45, 0.55]
    )
    
    # Pie chart
    colors = ['#dc2626', '#f59e0b', '#fbbf24', '#34d399', '#60a5fa', '#a78bfa', '#e5e7eb']
    
    fig.add_trace(
        go.Pie(
            labels=df['Pool'],
            values=df['Share (%)'],
            marker=dict(colors=colors),
            textinfo='label+percent',
            textposition='outside',
            hovertemplate='<b>%{label}</b><br>Share: %{value:.1f}%<br>Profit: %{customdata:.1f} SOL<extra></extra>',
            customdata=df['Profit (SOL)']
        ),
        row=1, col=1
    )
    
    # Bar chart
    fig.add_trace(
        go.Bar(
            x=df['Pool'],
            y=df['Profit (SOL)'],
            marker=dict(color=colors[:len(df)], line=dict(width=0)),
            text=df['Profit (SOL)'].apply(lambda x: f"{x:.1f}"),
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Profit: %{y:.1f} SOL<br>Share: %{customdata:.1f}%<extra></extra>',
            customdata=df['Share (%)']
        ),
        row=1, col=2
    )
    
    total_profit = df['Profit (SOL)'].sum()
    
    fig.update_layout(
        title=dict(
            text=f"<b>MEV Battlefield: {total_profit:.1f} SOL Total Extracted</b><br><sub>Click on segments to view detailed pool statistics</sub>",
            font=dict(size=18),
            x=0.5,
            xanchor='center'
        ),
        height=500,
        showlegend=False,
        plot_bgcolor='#f9fafb',
        paper_bgcolor='white'
    )
    
    fig.update_xaxes(title_text="Pool Protocol", row=1, col=2)
    fig.update_yaxes(title_text="Profit (SOL)", row=1, col=2)
    
    return fig

def get_pool_data_table(pool_name=None):
    """Return DataFrame with detailed pool statistics for selected pool."""
    # Load actual pool data
    try:
        pool_summary = pd.read_csv('02_mev_detection/POOL_SUMMARY.csv')
        pool_profits = pd.read_csv('13_mev_comprehensive_analysis/outputs/from_02_mev_detection/pool_mev_summary.csv')
        
        # Merge data
        df = pool_summary.merge(pool_profits, on='pool', how='left')
        
        if pool_name:
            df = df[df['pool'] == pool_name]
        
        # Select and rename columns for display
        display_df = df[[
            'pool', 'unique_attackers', 'unique_validators', 'total_mev_events',
            'total_profit', 'avg_profit', 'net_profit_sol', 'total_fat_sandwiches'
        ]].copy()
        
        display_df.columns = [
            'Pool', 'Attackers', 'Validators', 'MEV Events',
            'Profit (SOL)', 'Avg Profit', 'Net Profit', 'Fat Sandwiches'
        ]
        
        return display_df
    except Exception as e:
        # Fallback mock data
        return pd.DataFrame({
            'Pool': ['HumidiFi', 'BisonFi', 'GoonFi'],
            'Attackers': [593, 182, 258],
            'Profit (SOL)': [75.1, 11.2, 7.9],
            'MEV Events': [1434, 82, 799]
        })

def get_latency_data_table():
    """Return DataFrame with oracle latency details."""
    data = load_viz_data()
    latencies = data.get("oracle_latency_window", {}).get("pool_latencies_us", {})
    
    df = pd.DataFrame([
        {
            "Pool": pool,
            "Latency (μs)": latency,
            "Latency (ms)": round(latency / 1000, 1),
            "Latency (s)": round(latency / 1000000, 2)
        }
        for pool, latency in latencies.items()
    ]).sort_values("Latency (μs)", ascending=False)
    
    return df
