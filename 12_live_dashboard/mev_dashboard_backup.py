#!/usr/bin/env python3
"""
Interactive MEV Dashboard for Solana pAMM Analysis
Based on Comprehensive Analysis of Maximum Extractable Value (MEV) in Solana pAMMs
Updated: February 2026
"""

import dash
from dash import dcc, html, dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import networkx as nx
from dash.dependencies import Input, Output

# Hardcoded data from the report (updated values)
# Protocols and MEV Profits (SOL)
protocols_data = {
    'Protocol': ['HumidiFi', 'BisonFi', 'GoonFi', 'SolFiV2', 'TesseraV', 'ZeroFi', 'SolFi', 'ObricV2'],
    'MEV Profit (SOL)': [75.1, 11.232, 7.899, 6.5, 5.5, 3.2, 2.5, 0.497],
    'Attacks': [593, 182, 258, 176, 157, 93, 116, 42],  # Approximate from report
    'Attackers': [14, 256, 589, 157, 115, 50, 171, 9]  # From initial analysis, updated total 179 unique
}
df_protocols = pd.DataFrame(protocols_data)

# Top Attackers (corrected profits)
attackers_data = {
    'Attacker': ['YubQzu18FDqJRyNfG8JqHmsdbxhnoQqcKUHBdUkN6tP', 'YubVwWeg1vHFr17Q7HQQ...', 'AEB9dXBoxkrapNd59Kg2...', 'YubozzSnKomEnH3pkmYs...', 'CatyeC3LgBxub7HcpW2n...'],
    'Profit (SOL)': [16.731, 4.860, 3.888, 2.916, 2.691],
    'Attacks': [2, 63, 864, 632, 592]
}
df_attackers = pd.DataFrame(attackers_data)

# Contagion Data (attacker overlap heatmap)
contagion_matrix = pd.DataFrame({
    'HumidiFi': [167, 44, 43, 42, 40],
    'BisonFi': [44, 182, 42, 41, 39],
    'GoonFi': [43, 42, 258, 40, 38],
    'SolFiV2': [42, 41, 40, 176, 37],
    'TesseraV': [40, 39, 38, 37, 157]
}, index=['HumidiFi', 'BisonFi', 'GoonFi', 'SolFiV2', 'TesseraV'])

# Network graph for pool coordination
G = nx.Graph()
for protocol in protocols_data['Protocol']:
    G.add_node(protocol)
# Add edges based on overlap (approximate weights)
edges = [
    ('HumidiFi', 'BisonFi', 44),
    ('HumidiFi', 'GoonFi', 43),
    ('HumidiFi', 'SolFiV2', 42),
    ('HumidiFi', 'TesseraV', 40),
    ('BisonFi', 'GoonFi', 42),
    ('BisonFi', 'SolFiV2', 41),
    ('BisonFi', 'TesseraV', 39),
    ('GoonFi', 'SolFiV2', 40),
    ('GoonFi', 'TesseraV', 38),
    ('SolFiV2', 'TesseraV', 37),
]
for u, v, w in edges:
    G.add_edge(u, v, weight=w)

# Key Stats for Overview
key_stats = pd.DataFrame({
    'Metric': ['Total Events Analyzed', 'Validated Fat Sandwich Attacks', 'Total MEV Profit (SOL)', 'Unique Attackers', 'Validators Involved', 'Immediate Cascade Rate', 'Delayed Contagion Rate'],
    'Value': ['5,506,090', '617', '112.428', '179', '742', '0%', '22%']
})

# Oracle Data (approximate)
oracle_data = {
    'Pool': ['HumidiFi', 'BisonFi', 'GoonFi', 'SolFiV2', 'TesseraV'],
    'Median Latency (s)': [2.1, 1.2, 1.5, 0.8, 1.0],
    'Update Frequency (updates/sec)': [55.9, 12.4, 18.7, 9.3, 7.1]
}
df_oracle = pd.DataFrame(oracle_data)

# Token Pairs (risk tiers)
token_pairs = pd.DataFrame({
    'Pair': ['PUMP/WSOL', 'SOL/USDC (low liq)', 'BONK/SOL', 'WIF/SOL', 'SOL/USDC (high liq)'],
    'Risk Tier': ['High', 'High', 'High', 'High', 'Low'],
    'Attacks %': [38.2, 15.4, 12.1, 10.3, 8.3]
})

# ML Models
ml_data = pd.DataFrame({
    'Model': ['XGBoost', 'SVM', 'Logistic Regression', 'Random Forest'],
    'F1-Score': [0.91, 0.89, 0.82, 0.79],
    'ROC-AUC': [0.97, 0.96, 0.94, 0.94]
})

# Monte Carlo (approximate distributions)
mc_data = pd.DataFrame({
    'Scenario': ['Median Sandwich Risk', 'HumidiFi Risk', 'Expected Loss (SOL)', '95th % Loss (SOL)'],
    'Value': [8.7, 24.3, 0.023, 0.341]
})

# Initialize Dash app with custom styling
app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server  # Expose server for deployment (Heroku, Gunicorn, etc.)

# Custom CSS styling - Aileen's personal brand colors
colors = {
    'primary': '#6C63FF',      # Modern purple
    'secondary': '#FF6584',    # Coral pink
    'accent': '#4ECDC4',       # Teal
    'dark': '#1A1A2E',         # Deep navy
    'light': '#F8F9FA',        # Off-white
    'text': '#2D3436',         # Dark gray
    'gradient1': '#667EEA',    # Purple gradient
    'gradient2': '#764BA2',    # Deep purple
}

app.layout = html.Div([
    # Header with gradient background
    html.Div([
        html.Div([
            html.H1('🚀 Solana MEV Intelligence', 
                   style={
                       'color': 'white',
                       'marginBottom': '5px',
                       'fontWeight': '700',
                       'letterSpacing': '-1px',
                       'fontSize': '42px'
                   }),
            html.P('Advanced Analysis of Maximum Extractable Value in Solana pAMMs', 
                   style={
                       'color': 'rgba(255,255,255,0.9)',
                       'fontSize': '16px',
                       'marginBottom': '5px'
                   }),
            html.P('Research by Aileen | aileen.xyz', 
                   style={
                       'color': 'rgba(255,255,255,0.7)',
                       'fontSize': '14px',
                       'fontStyle': 'italic'
                   }),
        ], style={
            'textAlign': 'center',
            'padding': '40px 20px',
            'background': f'linear-gradient(135deg, {colors["gradient1"]}, {colors["gradient2"]})',
            'borderRadius': '0 0 20px 20px',
            'boxShadow': '0 4px 20px rgba(0,0,0,0.1)',
            'marginBottom': '30px'
        })
    ]),
    
    # Tabs with custom styling
    dcc.Tabs(
        style={
            'fontFamily':📈 Key Statistics', 
                       style={
                           'color': colors['text'],
                           'borderLeft': f'4px solid {colors["primary"]}',
                           'paddingLeft': '15px',
                           'marginBottom': '25px',
                           'fontWeight': '600'
                       }),
                dash_table.DataTable(
                    key_stats.to_dict('records'), 
                    [{"name": i, "id": i} for i in key_stats.columns],
                    style_cell={
               style={'padding': '12px', 'fontWeight': 'bold'},
               selected_style={'padding': '12px', 'fontWeight': 'bold', 'borderTop': f'3px solid {colors["secondary"]}'},
               children=[
            html.Div([
                dcc.Graph(
                    figure=px.bar(df_protocols, x='Protocol', y='MEV Profit (SOL)', 
                                       title='MEV Profit by Protocol',
                                       color='MEV Profit (SOL)',
                                       color_continuous_scale='Purples').update_layout(
                                           plot_bgcolor='white',
                                           paper_bgcolor='white',
                                           font={'family': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto', 'color': colors['text']},
                                           title_font_size=18,
                                           title_font_color=colors['text']
                                       
                    style_header={
                        'backgroundColor': colors['primary'],
                        'color': 'white',
                        'f
                    figure=px.pie(df_protocols, values='MEV Profit (SOL)', names='Protocol', 
                                       title='Profit Share Distribution',
                                       hole=0.4,
                                       color_discrete_sequence=px.colors.sequential.RdPu).update_layout(
                                           paper_bgcolor='white',
                                           font={'family': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto', 'color': colors['text']}
                                       )),
                dcc.Graph(
                    figure=px.bar(df_protocols, x='Protocol', y='Attacks', 
                                       ti
               style={'padding': '12px', 'fontWeight': 'bold'},
               selected_style={'padding': '12px', 'fontWeight': 'bold', 'borderTop': f'3px solid {colors["accent"]}'},
              tle='Attack Count by Protocol',
                                       color='Attacks',
                                       color_continuous_scale='Sunset').update_layout(
                                           plot_bgcolor='white',
                                           paper_bgcolor='white',
                                           font={'family': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto', 'color': colors['text']}
                                       ))
            ], style={
                'padding': '30px',
                'backgroundColor': 'white',
                'borderRadius': '15px',
                'boxShadow': '0 2px 10px rgba(0,0,0,0.08)',
                'margin': '20px'
            
                    style_data_conditional=[
                        {
                            'if': {'row_index': 'odd'},
                            'backgroundColor': colors['light']
                        }
                    ]
                )
            ], style={
                'padding': '30px',
                'backgroundColor': 'white',
                'borderRadius': '15px',
                'boxShadow': '0 2px 10px rgba(0,0,0,0.08)',
                'margin': '20px'
            
               style={'padding': '12px', 'fontWeight': 'bold'},
               selected_style={'padding': '12px', 'fontWeight': 'bold', 'borderTop': f'3px solid {colors["primary"]}'},
               children=[
            html.Div([
                html.H3('Key Statistics'),
                dash_table.DataTable(
                    key_stats.to_dict('records'), 
                    [{"name": i, "id": i} for i in key_stats.columns],
                    style_cell={'textAlign': 'left', 'padding': '10px'},
                    style_header={'backgroundColor': '#2c3e50', 'color': 'white', 'fontWeight': 'bold'},
                    style_data={'backgroundColor': '#ecf0f1'}
                )
            ], style={'padding': '20px'})
        ]),
        
        dcc.Tab(label='💰 MEV Distribution', children=[
            html.Div([
                dcc.Graph(figure=px.bar(df_protocols, x='Protocol', y='MEV Profit (SOL)', 
                                       title='MEV Profit by Protocol',
                                       color='MEV Profit (SOL)',
                                       color_continuous_scale='Viridis')),
                dcc.Graph(figure=px.pie(df_protocols, values='MEV Profit (SOL)', names='Protocol', 
                                       title='Profit Share Distribution',
                                       hole=0.3)),
                dcc.Graph(figure=px.bar(df_protocols, x='Protocol', y='Attacks', 
                                       title='Attack Count by Protocol',
                                       color='Attacks',
                                       color_continuous_scale='Reds'))
            ], style={'padding': '20px'})
        ]),
        
        dcc.Tab(label='🎯 Top Attackers', children=[
            html.Div([
                dcc.Graph(figure=px.bar(df_attackers, x='Attacker', y='Profit (SOL)', 
                                       title='Top 5 Attackers by Total Profit',
                                       text='Profit (SOL)',
                                       color='Profit (SOL)',
                                       color_continuous_scale='Plasma')),
                html.H4('Attacker Details'),
                dash_table.DataTable(
                    df_attackers.to_dict('records'),
                    [{"name": i, "id": i} for i in df_attackers.columns],
                    style_cell={'textAlign': 'left', 'padding': '10px'},
                    style_header={'backgroundColor': '#e74c3c', 'color': 'white', 'fontWeight': 'bold'},
                )
            ], style={'padding': '20px'})
        ]),
        
        dcc.Tab(label='🔗 Contagion Analysis', children=[
            html.Div([
                html.H3('Cross-Pool Attacker Overlap'),
                dcc.Graph(figure=px.imshow(contagion_matrix, 
                                          text_auto=True, 
                                          title='Attacker Overlap Heatmap',
                                          color_continuous_scale='RdYlBu_r',
                                          labels=dict(x="Target Pool", y="Source Pool", color="Shared Attackers"))),
                html.H3('Pool Coordination Network'),
                dcc.Graph(id='network-graph')
            ], style={'padding': '20px'})
        ]),
        
        dcc.Tab(label='⚡ Validator Behavior', children=[
            html.Div([
                html.H3('Validator Bot Activity Ratios'),
                html.P('Analysis of top validators by MEV bot transaction ratio (approximate from report)'),
                dcc.Graph(figure=px.bar(
                    x=['J6etcxDdY...', 'ETuPS3kRf...', 'sTEVErNNw...', '4mzLWNgBX...'], 
                    y=[0.92, 0.92, 0.94, 0.92], 
                    title='Bot Transaction Ratio by Validator',
                    labels={'x': 'Validator', 'y': 'Bot Ratio'},
                    text=[0.92, 0.92, 0.94, 0.92]
                )),
                html.P('Note: Values from validator latency metrics analysis showing high correlation with MEV activity')
            ], style={'padding': '20px'})
        ]),
        
        dcc.Tab(label='🔮 Oracle Analysis', children=[
            html.Div([
                dcc.Graph(figure=px.bar(df_oracle, x='Pool', y='Median Latency (s)', 
                                       title='Oracle Update Latency by Pool',
                                       color='Median Latency (s)',
                                       color_continuous_scale='Blues')),
                dcc.Graph(figure=px.bar(df_oracle, x='Pool', y='Update Frequency (updates/sec)', 
                                       title='Oracle Update Density (Updates/Second)',
                                       color='Update Frequency (updates/sec)',
                                       color_continuous_scale='Greens')),
                html.P('Oracle timing analysis reveals HumidiFi has highest update frequency (55.9/sec) correlating with 66.8% MEV share')
            ], style={'padding': '20px'})
        ]),
        
        dcc.Tab(label='🎲 Token Pair Risk', children=[
            html.Div([
                html.H3('Token Pair Vulnerability Analysis'),
                dash_table.DataTable(
                    token_pairs.to_dict('records'), 
                    [{"name": i, "id": i} for i in token_pairs.columns],
                    style_cell={'textAlign': 'left', 'padding': '10px'},
                    style_header={'backgroundColor': '#e67e22', 'color': 'white', 'fontWeight': 'bold'},
                    style_data_conditional=[
                        {
                            'if': {'filter_query': '{Risk Tier} = "High"'},
                            'backgroundColor': '#f39c12',
                            'color': 'white',
                        }
                    ]
                ),
                dcc.Graph(figure=px.bar(token_pairs, x='Pair', y='Attacks %', color='Risk Tier', 
                                       title='Attack Distribution by Token Pair',
                                       color_discrete_map={'High': '#e74c3c', 'Low': '#27ae60'}))
            ], style={'padding': '20px'})
        ]),
        
        dcc.Tab(label='🤖 ML Models', children=[
            html.Div([
          
    'fontFamily': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
    'backgroundColor': '#f5f7fa',
    'minHeight': '100vh',
    'padding': '0',
    'margin': '0'
,
                dcc.Graph(figure=px.bar(ml_data, x='Model', y='F1-Score', 
                                       title='Model F1-Score Comparison',
                                       text='F1-Score',
                                       color='F1-Score',
                                       color_continuous_scale='GnBu')),
                dcc.Graph(figure=px.scatter(ml_data, x='F1-Score', y='ROC-AUC', 
                                           text='Model',
                                           size=[100, 90, 80, 70],
                                           title='Model Performance: F1 vs ROC-AUC',
                                           color='Model')),
                html.P('XGBoost achieves best performance: F1=0.91, ROC-AUC=0.97 for MEV bot classification')
            ], style={'padding': '20px'})
        ]),
        
        dcc.Tab(label='📈 Monte Carlo Risk', children=[
            html.Div([
                html.H3('Monte Carlo Simulation Results'),
                dash_table.DataTable(
                    mc_data.to_dict('records'), 
                    [{"name": i, "id": i} for i in mc_data.columns],
                    style_cell={'textAlign': 'left', 'padding': '10px'},
                    style_header={'backgroundColor': '#9b59b6', 'color': 'white', 'fontWeight': 'bold'},
                ),
                html.H4('Risk Distribution'),
                html.P('Median sandwich risk: 8.7% | HumidiFi elevated risk: 24.3%'),
                html.P('Expected loss per vulnerable transaction: 0.023 SOL'),
                html.P('95th percentile loss (high-risk scenarios): 0.341 SOL'),
                html.Br(),
                html.P('Note: Simulations based on 10,000 iterations across historical attack patterns')
            ], style={'padding': '20px'})
        ]),
        
        dcc.Tab(label='🔴 Live Data', children=[
            html.Div([
                html.H3('Live Solana MEV Monitoring'),
                html.P('Real-time data integration placeholder - Ready for Helius/Jito API connection'),
                html.Hr(),
                html.H4('Sample Integration Code:'),
                html.Pre('''# Example: Fetch recent transactions via Helius RPC
from solana.rpc.api import Client
import os

client = Client(os.getenv("HELIUS_RPC_URL"))
recent_blocks = client.get_recent_blockhash()

# Parse for pAMM events and update dashboards
# Filter for MEV patterns: sandwich attacks, oracle back-running
# Update DataFrames and trigger Dash callbacks
''', style={'backgroundColor': '#2c3e50', 'color': '#ecf0f1', 'padding': '15px', 'borderRadius': '5px'}),
                html.Hr(),
                html.H4('API Integration Checklist:'),
                html.Ul([
                    html.Li('✅ Helius RPC for transaction streaming'),
                    html.Li('✅ Jito Block Engine for MEV bundle monitoring'),
                    html.Li('✅ Webhook setup for real-time pool updates'),
                    html.Li('⏳ Interval components for auto-refresh (5-60s)'),
                    html.Li('⏳ Live contagion analysis with rolling windows'),
                ])
            ], style={'padding': '20px'})
        ])
    ])
], style={'fontFamily': 'Arial, sans-serif', 'margin': '20px'})

# Callback for network graph
@app.callback(
    Output('network-graph', 'figure'),
    Input('network-graph', 'id')
)
def update_network(_):
    pos = nx.spring_layout(G, k=0.5, iterations=50)
    
    edge_x = []
    edge_y = []
    edge_text = []
    
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y, 
        line=dict(width=2, color='#95a5a6'), 
        hoverinfo='none', 
        mode='lines'
    )

    node_x = [pos[node][0] for node in G.nodes()]
    node_y = [pos[node][1] for node in G.nodes()]
    
    node_trace = go.Scatter(
        x=node_x, y=node_y, 
        mode='markers+text', 
        hoverinfo='text', 
        marker=dict(
            size=30, 
            color='#3498db',
            line=dict(width=2, color='#2c3e50')
        ), 
        text=list(G.nodes()),
        textposition="top center",
        textfont=dict(size=10, color='#2c3e50')
    )

    fig = go.Figure(
        data=[edge_trace, node_trace], 
        layout=go.Layout(
            title='Pool Coordination Network (Shared Attackers)',
            showlegend=False,
            hovermode='closest',
            margin=dict(b=0,l=0,r=0,t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='#ecf0f1'
        )
    )
    return fig


if __name__ == '__main__':
    print("🚀 Starting Solana pAMM MEV Dashboard...")
    print("📊 Access the dashboard at: http://127.0.0.1:8050/")
    print("📝 Use Ctrl+C to stop the server")
    app.run(debug=True, host='0.0.0.0', port=8050)
