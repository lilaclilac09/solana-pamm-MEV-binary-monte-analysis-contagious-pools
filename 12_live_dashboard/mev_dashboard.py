#!/usr/bin/env python3
"""
Enhanced Interactive MEV Dashboard for Solana pAMM Analysis
Based on Comprehensive Analysis of Maximum Extractable Value (MEV) in Solana pAMMs
Updated: February 27, 2026
Research by Aileen | aileen.xyz
"""

import dash
from dash import dcc, html, dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import networkx as nx
import numpy as np
from dash.dependencies import Input, Output

# ========== DATA PREPARATION ==========

# Protocols and MEV Profits (SOL) - Extended with oracle latency
protocols_data = {
    'Protocol': ['HumidiFi', 'BisonFi', 'GoonFi', 'SolFiV2', 'TesseraV', 'ZeroFi', 'SolFi', 'ObricV2'],
    'MEV Profit (SOL)': [75.1, 11.232, 7.899, 6.5, 5.5, 3.2, 2.5, 0.497],
    'Attacks': [593, 182, 258, 176, 157, 93, 116, 42],
    'Attackers': [14, 256, 589, 157, 115, 50, 171, 9],
    'Oracle Latency (s)': [2.1, 1.2, 1.5, 0.8, 1.0, 1.8, 1.3, 2.5],
    'Update Frequency (updates/sec)': [55.9, 12.4, 18.7, 9.3, 7.1, 4.2, 11.6, 3.1]
}
df_protocols = pd.DataFrame(protocols_data)

# Top Attackers
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
    'Metric': [
        'Total Events Analyzed', 
        'Validated Fat Sandwich Attacks', 
        'Total MEV Profit (SOL)', 
        'Unique Attackers', 
        'Validators Involved', 
        'Immediate Cascade Rate', 
        'Delayed Contagion Rate'
    ],
    'Value': ['5,506,090', '617', '112.428', '179', '742', '0%', '22%']
})

# Oracle Data
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
    'Attacks %': [38.2, 15.4, 12.1, 10.3, 8.3],
    'Liquidity ($K)': [28, 75, 52, 67, 850]
})

# ML Models
ml_data = pd.DataFrame({
    'Model': ['XGBoost', 'SVM', 'Logistic Regression', 'Random Forest'],
    'F1-Score': [0.91, 0.89, 0.82, 0.79],
    'ROC-AUC': [0.97, 0.96, 0.94, 0.94]
})

# Feature Importance from ML Models
feature_importance = pd.DataFrame({
    'Feature': ['Profit-to-Cost Ratio', 'Victim Interaction Rate', 'Oracle Update Proximity', 'Transaction Timing', 'Pool Liquidity'],
    'Importance': [0.32, 0.24, 0.18, 0.15, 0.11]
})

# Monte Carlo
mc_data = pd.DataFrame({
    'Scenario': ['Median Sandwich Risk', 'HumidiFi Risk', 'BisonFi Risk', 'Expected Loss (SOL)', '95th % Loss (SOL)'],
    'Value': [8.7, 24.3, 6.1, 0.023, 0.341]
})

# P&L Distribution (BPS - basis points)
pnl_data = pd.DataFrame({
    'BPS': [10, 20, 30, 50, 100, 150, 200, 250],
    'Frequency': [200, 150, 100, 80, 50, 30, 20, 10]
})

# Event Type Distribution
event_types = pd.DataFrame({
    'Type': ['ORACLE UPDATE', 'TRADE'],
    'Count': [4817358, 688732],  # Approximate from 5.5M total
    'Percentage': [87.5, 12.5]
})

# Events Per Minute (simulated time series showing burst patterns)
time_data = pd.DataFrame({
    'Minute': list(range(60)),  # 1 hour sample
    'Events': np.random.choice([800, 1200, 5000, 1000, 4500, 900, 5200, 1100, 4800, 950, 5100], size=60)
})

# Validator Bot Ratios
validator_data = pd.DataFrame({
    'Validator': ['J6etcxDdY...', 'ETuPS3kRf...', 'sTEVErNNw...', '4mzLWNgBX...', 'Others'],
    'Bot Ratio': [0.92, 0.92, 0.94, 0.92, 0.34],
    'MEV Events': [55997, 2708, 803, 1009, 1425]
})

# Case Studies Data
case_studies = pd.DataFrame({
    'Case': [
        'BisonFi WIF/BONK Arbitrage', 
        'B91 Sandwich Bot (Web Case)', 
        'Vpe Program (Helius Report)', 
        'Fat Sandwich Specialists'
    ],
    'Target': [
        'BisonFi WIF/SOL + BONK/SOL cross-pair', 
        '82,000 attacks, 78,800 victims', 
        'Half of Solana sandwiches', 
        'PUMP/WSOL high-volume pairs'
    ],
    'Profit': [
        '2.752 SOL (209% ROI, 8 txs, 3 slots)', 
        '7,800 SOL in 30 days', 
        '65,880 SOL in 30 days, 0.0425 SOL avg', 
        '38.2% of attacks, 2.1x avg ROI'
    ],
    'Method': [
        'Multi-pool arbitrage + dual sandwich', 
        'Classic sandwich on vulnerable pairs', 
        '1.55M attacks, 0.5x Solana sandwich volume', 
        'High-volume pair targeting, oracle timing'
    ]
})

# ========== APP INITIALIZATION ==========

app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server

# Aileen's personal brand colors
colors = {
    'primary': '#6C63FF',
    'secondary': '#FF6584',
    'accent': '#4ECDC4',
    'dark': '#1A1A2E',
    'light': '#F8F9FA',
    'text': '#2D3436',
    'gradient1': '#667EEA',
    'gradient2': '#764BA2',
}

# ========== LAYOUT ==========

app.layout = html.Div([
    # Gradient Header
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
    }),
    
    # Tabs
    dcc.Tabs(
        style={
            'fontFamily': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
        },
        children=[
        
        # ========== TAB 1: OVERVIEW ==========
        dcc.Tab(
            label='📊 Overview',
            style={'padding': '12px', 'fontWeight': 'bold'},
            selected_style={'padding': '12px', 'fontWeight': 'bold', 'borderTop': f'3px solid {colors["primary"]}'},
            children=[
                html.Div([
                    html.H3('📈 Key Statistics', 
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
                            'textAlign': 'left',
                            'padding': '12px',
                            'fontFamily': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto',
                            'fontSize': '14px'
                        },
                        style_header={
                            'backgroundColor': colors['primary'],
                            'color': 'white',
                            'fontWeight': 'bold',
                            'textAlign': 'left',
                            'border': 'none'
                        },
                        style_data={
                            'backgroundColor': 'white',
                            'color': colors['text'],
                            'border': '1px solid #e0e0e0'
                        },
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
                })
            ]
        ),
        
        # ========== TAB 2: MEV DISTRIBUTION ==========
        dcc.Tab(
            label='💰 MEV Distribution',
            style={'padding': '12px', 'fontWeight': 'bold'},
            selected_style={'padding': '12px', 'fontWeight': 'bold', 'borderTop': f'3px solid {colors["secondary"]}'},
            children=[
                html.Div([
                    dcc.Graph(
                        figure=px.bar(
                            df_protocols, 
                            x='Protocol', 
                            y='MEV Profit (SOL)', 
                            title='MEV Profit by Protocol',
                            color='MEV Profit (SOL)',
                            color_continuous_scale='Purples'
                        ).update_layout(
                            plot_bgcolor='white',
                            paper_bgcolor='white',
                            font={'family': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto', 'color': colors['text']},
                            title_font_size=18,
                            title_font_color=colors['text']
                        )
                    ),
                    dcc.Graph(
                        figure=px.pie(
                            df_protocols, 
                            values='MEV Profit (SOL)', 
                            names='Protocol', 
                            title='Profit Share Distribution',
                            hole=0.4,
                            color_discrete_sequence=px.colors.sequential.RdPu
                        ).update_layout(
                            paper_bgcolor='white',
                            font={'family': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto', 'color': colors['text']}
                        )
                    ),
                    dcc.Graph(
                        figure=px.bar(
                            df_protocols, 
                            x='Protocol', 
                            y='Attacks', 
                            title='Attack Count by Protocol',
                            color='Attacks',
                            color_continuous_scale='Sunset'
                        ).update_layout(
                            plot_bgcolor='white',
                            paper_bgcolor='white',
                            font={'family': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto', 'color': colors['text']}
                        )
                    )
                ], style={
                    'padding': '30px',
                    'backgroundColor': 'white',
                    'borderRadius': '15px',
                    'boxShadow': '0 2px 10px rgba(0,0,0,0.08)',
                    'margin': '20px'
                })
            ]
        ),
        
        # ========== TAB 3: TOP ATTACKERS ==========
        dcc.Tab(
            label='🎯 Top Attackers',
            style={'padding': '12px', 'fontWeight': 'bold'},
            selected_style={'padding': '12px', 'fontWeight': 'bold', 'borderTop': f'3px solid {colors["accent"]}'},
            children=[
                html.Div([
                    dcc.Graph(
                        figure=px.bar(
                            df_attackers, 
                            x='Attacker', 
                            y='Profit (SOL)', 
                            title='Top 5 Attackers by Total Profit',
                            text='Profit (SOL)',
                            color='Profit (SOL)',
                            color_continuous_scale='Plasma'
                        ).update_layout(
                            plot_bgcolor='white',
                            paper_bgcolor='white',
                            font={'family': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto', 'color': colors['text']}
                        ).update_traces(texttemplate='%{text:.2f}', textposition='outside')
                    ),
                    html.H4('Attacker Details', style={'color': colors['text'], 'marginTop': '30px', 'marginBottom': '15px'}),
                    dash_table.DataTable(
                        df_attackers.to_dict('records'),
                        [{"name": i, "id": i} for i in df_attackers.columns],
                        style_cell={
                            'textAlign': 'left',
                            'padding': '12px',
                            'fontFamily': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto',
                            'fontSize': '14px',
                            'overflow': 'hidden',
                            'textOverflow': 'ellipsis',
                            'maxWidth': 0
                        },
                        style_header={
                            'backgroundColor': colors['primary'],
                            'color': 'white',
                            'fontWeight': 'bold',
                            'textAlign': 'left'
                        },
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
                })
            ]
        ),
        
        # ========== TAB 4: CONTAGION ANALYSIS ==========
        dcc.Tab(
            label='🔗 Contagion Analysis',
            style={'padding': '12px', 'fontWeight': 'bold'},
            selected_style={'padding': '12px', 'fontWeight': 'bold', 'borderTop': f'3px solid {colors["primary"]}'},
            children=[
                html.Div([
                    html.H3('Cross-Pool Attacker Overlap', style={'color': colors['text'], 'marginBottom': '20px'}),
                    dcc.Graph(
                        figure=px.imshow(
                            contagion_matrix, 
                            text_auto=True, 
                            title='Attacker Overlap Heatmap',
                            color_continuous_scale='RdPu',
                            labels=dict(x="Target Pool", y="Source Pool", color="Shared Attackers")
                        ).update_layout(
                            paper_bgcolor='white',
                            plot_bgcolor='white',
                            font={'family': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto', 'color': colors['text']}
                        )
                    ),
                    html.H3('Pool Coordination Network', style={'color': colors['text'], 'marginTop': '30px', 'marginBottom': '20px'}),
                    dcc.Graph(id='network-graph')
                ], style={
                    'padding': '30px',
                    'backgroundColor': 'white',
                    'borderRadius': '15px',
                    'boxShadow': '0 2px 10px rgba(0,0,0,0.08)',
                    'margin': '20px'
                })
            ]
        ),
        
        # ========== TAB 5: VALIDATOR BEHAVIOR ==========
        dcc.Tab(
            label='⚡ Validator Behavior',
            style={'padding': '12px', 'fontWeight': 'bold'},
            selected_style={'padding': '12px', 'fontWeight': 'bold', 'borderTop': f'3px solid {colors["secondary"]}'},
            children=[
                html.Div([
                    html.H3('Validator Bot Activity Ratios', style={'color': colors['text'], 'marginBottom': '15px'}),
                    html.P('Analysis of top validators by MEV bot transaction ratio (approximate from report)', 
                           style={'color': colors['text'], 'marginBottom': '25px'}),
                    dcc.Graph(
                        figure=px.bar(
                            x=['J6etcxDdY...', 'ETuPS3kRf...', 'sTEVErNNw...', '4mzLWNgBX...'], 
                            y=[0.92, 0.92, 0.94, 0.92], 
                            title='Bot Transaction Ratio by Validator',
                            labels={'x': 'Validator', 'y': 'Bot Ratio'},
                            text=[0.92, 0.92, 0.94, 0.92],
                            color_discrete_sequence=[colors['primary']]
                        ).update_layout(
                            plot_bgcolor='white',
                            paper_bgcolor='white',
                            font={'family': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto', 'color': colors['text']}
                        ).update_traces(texttemplate='%{text:.2f}', textposition='outside')
                    ),
                    html.P('Note: Values from validator latency metrics analysis showing high correlation with MEV activity',
                           style={'color': colors['text'], 'fontStyle': 'italic', 'marginTop': '20px'})
                ], style={
                    'padding': '30px',
                    'backgroundColor': 'white',
                    'borderRadius': '15px',
                    'boxShadow': '0 2px 10px rgba(0,0,0,0.08)',
                    'margin': '20px'
                })
            ]
        ),
        
        # ========== TAB 6: ORACLE ANALYSIS ==========
        dcc.Tab(
            label='🔮 Oracle Analysis',
            style={'padding': '12px', 'fontWeight': 'bold'},
            selected_style={'padding': '12px', 'fontWeight': 'bold', 'borderTop': f'3px solid {colors["accent"]}'},
            children=[
                html.Div([
                    dcc.Graph(
                        figure=px.bar(
                            df_oracle, 
                            x='Pool', 
                            y='Median Latency (s)', 
                            title='Oracle Update Latency by Pool',
                            color='Median Latency (s)',
                            color_continuous_scale='Blues'
                        ).update_layout(
                            plot_bgcolor='white',
                            paper_bgcolor='white',
                            font={'family': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto', 'color': colors['text']}
                        )
                    ),
                    dcc.Graph(
                        figure=px.bar(
                            df_oracle, 
                            x='Pool', 
                            y='Update Frequency (updates/sec)', 
                            title='Oracle Update Density (Updates/Second)',
                            color='Update Frequency (updates/sec)',
                            color_continuous_scale='Purples'
                        ).update_layout(
                            plot_bgcolor='white',
                            paper_bgcolor='white',
                            font={'family': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto', 'color': colors['text']}
                        )
                    ),
                    html.P('Oracle timing analysis reveals HumidiFi has highest update frequency (55.9/sec) correlating with 66.8% MEV share',
                           style={'color': colors['text'], 'marginTop': '20px', 'padding': '15px', 'backgroundColor': colors['light'], 'borderRadius': '8px'})
                ], style={
                    'padding': '30px',
                    'backgroundColor': 'white',
                    'borderRadius': '15px',
                    'boxShadow': '0 2px 10px rgba(0,0,0,0.08)',
                    'margin': '20px'
                })
            ]
        ),
        
        # ========== TAB 7: TOKEN PAIR RISK ==========
        dcc.Tab(
            label='🎲 Token Pair Risk',
            style={'padding': '12px', 'fontWeight': 'bold'},
            selected_style={'padding': '12px', 'fontWeight': 'bold', 'borderTop': f'3px solid {colors["primary"]}'},
            children=[
                html.Div([
                    html.H3('Token Pair Vulnerability Analysis', style={'color': colors['text'], 'marginBottom': '20px'}),
                    dash_table.DataTable(
                        token_pairs.to_dict('records'), 
                        [{"name": i, "id": i} for i in token_pairs.columns],
                        style_cell={
                            'textAlign': 'left',
                            'padding': '12px',
                            'fontFamily': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto',
                            'fontSize': '14px'
                        },
                        style_header={
                            'backgroundColor': colors['primary'],
                            'color': 'white',
                            'fontWeight': 'bold',
                            'textAlign': 'left'
                        },
                        style_data_conditional=[
                            {
                                'if': {'row_index': 'odd'},
                                'backgroundColor': colors['light']
                            },
                            {
                                'if': {'filter_query': '{Risk Tier} = "High"'},
                                'backgroundColor': '#FFE5E5',
                                'fontWeight': 'bold'
                            }
                        ]
                    ),
                    dcc.Graph(
                        figure=px.bar(
                            token_pairs, 
                            x='Pair', 
                            y='Attacks %', 
                            color='Risk Tier', 
                            title='Attack Distribution by Token Pair',
                            color_discrete_map={'High': colors['secondary'], 'Low': colors['accent']}
                        ).update_layout(
                            plot_bgcolor='white',
                            paper_bgcolor='white',
                            font={'family': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto', 'color': colors['text']}
                        )
                    )
                ], style={
                    'padding': '30px',
                    'backgroundColor': 'white',
                    'borderRadius': '15px',
                    'boxShadow': '0 2px 10px rgba(0,0,0,0.08)',
                    'margin': '20px'
                })
            ]
        ),
        
        # ========== TAB 8: ML MODELS ==========
        dcc.Tab(
            label='🤖 ML Models',
            style={'padding': '12px', 'fontWeight': 'bold'},
            selected_style={'padding': '12px', 'fontWeight': 'bold', 'borderTop': f'3px solid {colors["secondary"]}'},
            children=[
                html.Div([
                    dcc.Graph(
                        figure=px.bar(
                            ml_data, 
                            x='Model', 
                            y='F1-Score', 
                            title='Model F1-Score Comparison',
                            text='F1-Score',
                            color='F1-Score',
                            color_continuous_scale='Purples'
                        ).update_layout(
                            plot_bgcolor='white',
                            paper_bgcolor='white',
                            font={'family': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto', 'color': colors['text']}
                        ).update_traces(texttemplate='%{text:.2f}', textposition='outside')
                    ),
                    dcc.Graph(
                        figure=px.scatter(
                            ml_data, 
                            x='F1-Score', 
                            y='ROC-AUC', 
                            text='Model',
                            size=[100, 90, 80, 70],
                            title='Model Performance: F1 vs ROC-AUC',
                            color='Model',
                            color_discrete_sequence=px.colors.sequential.RdPu
                        ).update_layout(
                            plot_bgcolor='white',
                            paper_bgcolor='white',
                            font={'family': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto', 'color': colors['text']}
                        ).update_traces(textposition='top center')
                    ),
                    html.P('XGBoost achieves best performance: F1=0.91, ROC-AUC=0.97 for MEV bot classification',
                           style={'color': colors['text'], 'marginTop': '20px', 'padding': '15px', 'backgroundColor': colors['light'], 'borderRadius': '8px', 'fontWeight': '500'})
                ], style={
                    'padding': '30px',
                    'backgroundColor': 'white',
                    'borderRadius': '15px',
                    'boxShadow': '0 2px 10px rgba(0,0,0,0.08)',
                    'margin': '20px'
                })
            ]
        ),
        
        # ========== TAB 9: MONTE CARLO RISK ==========
        dcc.Tab(
            label='📈 Monte Carlo Risk',
            style={'padding': '12px', 'fontWeight': 'bold'},
            selected_style={'padding': '12px', 'fontWeight': 'bold', 'borderTop': f'3px solid {colors["accent"]}'},
            children=[
                html.Div([
                    html.H3('Monte Carlo Simulation Results', style={'color': colors['text'], 'marginBottom': '20px'}),
                    dash_table.DataTable(
                        mc_data.to_dict('records'), 
                        [{"name": i, "id": i} for i in mc_data.columns],
                        style_cell={
                            'textAlign': 'left',
                            'padding': '12px',
                            'fontFamily': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto',
                            'fontSize': '14px'
                        },
                        style_header={
                            'backgroundColor': colors['primary'],
                            'color': 'white',
                            'fontWeight': 'bold',
                            'textAlign': 'left'
                        },
                        style_data_conditional=[
                            {
                                'if': {'row_index': 'odd'},
                                'backgroundColor': colors['light']
                            }
                        ]
                    ),
                    html.H4('Risk Distribution', style={'color': colors['text'], 'marginTop': '30px', 'marginBottom': '15px'}),
                    html.Div([
                        html.P('📊 Median sandwich risk: 8.7% | HumidiFi elevated risk: 24.3%', style={'marginBottom': '10px'}),
                        html.P('💰 Expected loss per vulnerable transaction: 0.023 SOL', style={'marginBottom': '10px'}),
                        html.P('⚠️ 95th percentile loss (high-risk scenarios): 0.341 SOL', style={'marginBottom': '10px'}),
                    ], style={'padding': '20px', 'backgroundColor': colors['light'], 'borderRadius': '8px', 'color': colors['text']}),
                    html.P('Note: Simulations based on 10,000 iterations across historical attack patterns',
                           style={'color': colors['text'], 'fontStyle': 'italic', 'marginTop': '20px'})
                ], style={
                    'padding': '30px',
                    'backgroundColor': 'white',
                    'borderRadius': '15px',
                    'boxShadow': '0 2px 10px rgba(0,0,0,0.08)',
                    'margin': '20px'
                })
            ]
        )
    ])
], style={
    'fontFamily': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
    'backgroundColor': '#f5f7fa',
    'minHeight': '100vh',
    'padding': '0',
    'margin': '0'
})

# ========== CALLBACK: NETWORK GRAPH ==========

@app.callback(
    Output('network-graph', 'figure'),
    Input('network-graph', 'id')
)
def update_network(_):
    """Generate interactive network graph showing pool coordination via shared attackers"""
    pos = nx.spring_layout(G, k=0.5, iterations=50)
    
    edge_x = []
    edge_y = []
    
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y, 
        line=dict(width=2, color='#E0E0E0'), 
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
            size=35, 
            color=colors['primary'],
            line=dict(width=2, color='white')
        ), 
        text=list(G.nodes()),
        textposition="top center",
        textfont=dict(size=11, color=colors['text'], family='-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto')
    )

    fig = go.Figure(
        data=[edge_trace, node_trace], 
        layout=go.Layout(
            title='Pool Coordination Network (Shared Attackers)',
            title_font=dict(size=18, color=colors['text'], family='-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto'),
            showlegend=False,
            hovermode='closest',
            margin=dict(b=0,l=0,r=0,t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
    )
    return fig


# ========== RUN SERVER ==========

if __name__ == '__main__':
    print("🚀 Starting Solana pAMM MEV Dashboard...")
    print("📊 Access the dashboard at: http://127.0.0.1:8050/")
    print("🌐 Or from network devices at: http://0.0.0.0:8050/")
    print("📝 Use Ctrl+C to stop the server")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=8050)
