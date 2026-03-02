#!/usr/bin/env python3
"""
Solana pAMM MEV Analysis Dashboard - 研究成果展示
简洁版本，聚焦核心研究数据
By Aileen | aileen.xyz
"""

import dash
from dash import dcc, html, dash_table
import plotly.express as px
import pandas as pd

# ========== 核心研究数据 ==========

# 1. 攻击模式分布 (您的关键研究成果)
attack_patterns = pd.DataFrame({
    'Attack Type': ['Fat Sandwich', 'Back-Running (DeezNode)', 'Classic Sandwich', 'Front-Running', 'Cross-Slot (2Fast)'],
    'Count': [312, 135, 95, 62, 46],
    'Percentage': [48.0, 20.8, 14.6, 9.5, 7.1]
})

# 2. 协议分析
protocols = pd.DataFrame({
    'Protocol': ['HumidiFi', 'BisonFi', 'GoonFi', 'SolFiV2', 'TesseraV', 'ZeroFi', 'SolFi', 'ObricV2'],
    'MEV Profit (SOL)': [75.1, 11.232, 7.899, 6.5, 5.5, 3.2, 2.5, 0.497],
    'Attack Count': [593, 182, 258, 176, 157, 93, 116, 42]
})

# 3. 顶级攻击者
top_attackers = pd.DataFrame({
    'Attacker Address': ['YubQzu18FDqJRyNfG8JqHmsdbxhnoQqcKUHBdUkN6tP', 
                         'YubVwWeg1vHFr17Q7HQQ...', 
                         'AEB9dXBoxkrapNd59Kg2...', 
                         'YubozzSnKomEnH3pkmYs...', 
                         'CatyeC3LgBxub7HcpW2n...'],
    'Profit (SOL)': [16.731, 4.860, 3.888, 2.916, 2.691],
    'Attacks': [2, 63, 864, 632, 592]
})

# 4. 验证器分析
validators = pd.DataFrame({
    'Validator': ['J6etcxDdY...', 'ETuPS3kRf...', 'sTEVErNNw...', '4mzLWNgBX...', 'Others'],
    'MEV Events': [55997, 2708, 803, 1009, 1425],
    'Bot Ratio': [0.92, 0.92, 0.94, 0.92, 0.34]
})

# 5. 预言机分析
oracles = pd.DataFrame({
    'Pool': ['HumidiFi', 'BisonFi', 'GoonFi', 'SolFiV2', 'TesseraV'],
    'Latency (s)': [2.1, 1.2, 1.5, 0.8, 1.0],
    'Update Freq (Hz)': [55.9, 12.4, 18.7, 9.3, 7.1]
})

# 6. 关键统计
key_stats = {
    'Total Events': '5,506,090',
    'Confirmed Attacks': 617,
    'Total MEV (SOL)': 112.428,
    'Unique Attackers': 179,
    'Impacted Validators': 742,
    'Cascade Rate': '0%',
    'Delayed Contagion': '22%'
}

# ========== 应用初始化 ==========
app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server

# ========== 简洁样式 ==========
colors = {
    'bg': '#ffffff',
    'text': '#2c3e50',
    'primary': '#3498db',
    'accent': '#e74c3c',
    'light_bg': '#f8f9fa'
}

# ========== 布局 ==========
app.layout = html.Div([
    # Header
    html.Div([
        html.H1('Solana pAMM MEV Analysis', style={
            'margin': 0, 'fontSize': '28px', 'fontWeight': 'bold', 'color': colors['text']
        }),
        html.P('Research by Aileen | aileen.xyz', style={
            'margin': '5px 0 0 0', 'fontSize': '14px', 'color': '#7f8c8d'
        })
    ], style={
        'padding': '20px 30px',
        'borderBottom': f'2px solid {colors["primary"]}',
        'marginBottom': '30px'
    }),
    
    # 主容器
    html.Div([
        # ========== 第 1 行：关键统计 ==========
        html.Div([
            html.H2('Key Statistics', style={'marginTop': 0, 'marginBottom': '20px', 'color': colors['text']}),
            html.Div([
                html.Div([
                    html.Div(key_stats['Total Events'], style={
                        'fontSize': '24px', 'fontWeight': 'bold', 'color': colors['primary']
                    }),
                    html.Div('Total Events Analyzed', style={'fontSize': '12px', 'color': '#7f8c8d', 'marginTop': '5px'})
                ], style={'textAlign': 'center', 'padding': '20px', 'backgroundColor': colors['light_bg'], 'borderRadius': '8px'}),
                
                html.Div([
                    html.Div(str(key_stats['Confirmed Attacks']), style={
                        'fontSize': '24px', 'fontWeight': 'bold', 'color': colors['accent']
                    }),
                    html.Div('Confirmed Attacks', style={'fontSize': '12px', 'color': '#7f8c8d', 'marginTop': '5px'})
                ], style={'textAlign': 'center', 'padding': '20px', 'backgroundColor': colors['light_bg'], 'borderRadius': '8px'}),
                
                html.Div([
                    html.Div(f"{key_stats['Total MEV (SOL)']}", style={
                        'fontSize': '24px', 'fontWeight': 'bold', 'color': colors['primary']
                    }),
                    html.Div('Total MEV (SOL)', style={'fontSize': '12px', 'color': '#7f8c8d', 'marginTop': '5px'})
                ], style={'textAlign': 'center', 'padding': '20px', 'backgroundColor': colors['light_bg'], 'borderRadius': '8px'}),
                
                html.Div([
                    html.Div(str(key_stats['Unique Attackers']), style={
                        'fontSize': '24px', 'fontWeight': 'bold', 'color': colors['primary']
                    }),
                    html.Div('Unique Attackers', style={'fontSize': '12px', 'color': '#7f8c8d', 'marginTop': '5px'})
                ], style={'textAlign': 'center', 'padding': '20px', 'backgroundColor': colors['light_bg'], 'borderRadius': '8px'}),
            ], style={'display': 'grid', 'gridTemplateColumns': 'repeat(4, 1fr)', 'gap': '15px'})
        ], style={'padding': '30px', 'backgroundColor': colors['bg']}),
        
        # ========== 第 2 行：攻击模式 (核心研究成果) ==========
        html.Div([
            html.H2('Attack Pattern Distribution (Your Research)', style={'marginTop': 0, 'marginBottom': '20px', 'color': colors['text']}),
            html.Div([
                html.Div([
                    dcc.Graph(
                        figure=px.bar(
                            attack_patterns.sort_values('Count', ascending=False),
                            x='Attack Type',
                            y='Count',
                            title='MEV Attack Counts by Type',
                            text='Count',
                            color='Count',
                            color_continuous_scale='Blues'
                        ).update_layout(
                            plot_bgcolor='white',
                            paper_bgcolor=colors['bg'],
                            font={'family': 'Arial, sans-serif', 'color': colors['text']},
                            title_font_size=16,
                            showlegend=False,
                            height=350
                        ).update_traces(textposition='outside'),
                        style={'width': '100%', 'height': '100%'}
                    )
                ], style={'width': '48%', 'display': 'inline-block'}),
                
                html.Div([
                    dcc.Graph(
                        figure=px.pie(
                            attack_patterns,
                            values='Count',
                            names='Attack Type',
                            title='Distribution (%)'
                        ).update_layout(
                            plot_bgcolor='white',
                            paper_bgcolor=colors['bg'],
                            font={'family': 'Arial, sans-serif', 'color': colors['text']},
                            title_font_size=16,
                            height=350
                        ),
                        style={'width': '100%', 'height': '100%'}
                    )
                ], style={'width': '48%', 'display': 'inline-block', 'marginLeft': '4%'}),
            ]),
            
            # 攻击模式表格
            html.H3('Attack Pattern Details', style={'marginTop': '20px', 'marginBottom': '15px', 'color': colors['text']}),
            dash_table.DataTable(
                data=attack_patterns.to_dict('records'),
                columns=[{"name": i, "id": i} for i in attack_patterns.columns],
                style_cell={'padding': '10px', 'fontFamily': 'Arial, sans-serif'},
                style_header={
                    'backgroundColor': colors['primary'],
                    'color': 'white',
                    'fontWeight': 'bold',
                    'textAlign': 'left'
                },
                style_data_conditional=[
                    {'if': {'row_index': 'odd'}, 'backgroundColor': colors['light_bg']}
                ]
            )
        ], style={'padding': '30px', 'backgroundColor': colors['bg'], 'marginTop': '20px'}),
        
        # ========== 第 3 行：协议分析 ==========
        html.Div([
            html.H2('Protocol Analysis', style={'marginTop': 0, 'marginBottom': '20px', 'color': colors['text']}),
            dcc.Graph(
                figure=px.bar(
                    protocols.sort_values('MEV Profit (SOL)', ascending=False),
                    x='Protocol',
                    y='MEV Profit (SOL)',
                    text='MEV Profit (SOL)',
                    title='MEV Profit Distribution Across Protocols',
                    color='MEV Profit (SOL)',
                    color_continuous_scale='Reds'
                ).update_layout(
                    plot_bgcolor='white',
                    paper_bgcolor=colors['bg'],
                    font={'family': 'Arial, sans-serif', 'color': colors['text']},
                    title_font_size=16,
                    showlegend=False,
                    height=350
                ).update_traces(textposition='outside'),
                style={'width': '100%', 'height': '100%'}
            ),
            
            html.H3('Protocol Details', style={'marginTop': '20px', 'marginBottom': '15px', 'color': colors['text']}),
            dash_table.DataTable(
                data=protocols.to_dict('records'),
                columns=[{"name": i, "id": i} for i in protocols.columns],
                style_cell={'padding': '10px', 'fontFamily': 'Arial, sans-serif'},
                style_header={
                    'backgroundColor': colors['primary'],
                    'color': 'white',
                    'fontWeight': 'bold',
                    'textAlign': 'left'
                },
                style_data_conditional=[
                    {'if': {'row_index': 'odd'}, 'backgroundColor': colors['light_bg']}
                ]
            )
        ], style={'padding': '30px', 'backgroundColor': colors['bg'], 'marginTop': '20px'}),
        
        # ========== 第 4 行：攻击者和验证器 ==========
        html.Div([
            html.Div([
                html.H2('Top Attackers', style={'marginTop': 0, 'marginBottom': '15px', 'color': colors['text']}),
                dash_table.DataTable(
                    data=top_attackers.to_dict('records'),
                    columns=[{"name": i, "id": i} for i in top_attackers.columns],
                    style_cell={'padding': '10px', 'fontFamily': 'Arial, sans-serif', 'fontSize': '12px'},
                    style_header={
                        'backgroundColor': colors['primary'],
                        'color': 'white',
                        'fontWeight': 'bold',
                        'textAlign': 'left'
                    },
                    style_data_conditional=[
                        {'if': {'row_index': 'odd'}, 'backgroundColor': colors['light_bg']}
                    ]
                )
            ], style={'width': '48%', 'display': 'inline-block'}),
            
            html.Div([
                html.H2('Validator Participation', style={'marginTop': 0, 'marginBottom': '15px', 'color': colors['text']}),
                dash_table.DataTable(
                    data=validators.to_dict('records'),
                    columns=[{"name": i, "id": i} for i in validators.columns],
                    style_cell={'padding': '10px', 'fontFamily': 'Arial, sans-serif', 'fontSize': '12px'},
                    style_header={
                        'backgroundColor': colors['primary'],
                        'color': 'white',
                        'fontWeight': 'bold',
                        'textAlign': 'left'
                    },
                    style_data_conditional=[
                        {'if': {'row_index': 'odd'}, 'backgroundColor': colors['light_bg']}
                    ]
                )
            ], style={'width': '48%', 'display': 'inline-block', 'marginLeft': '4%'})
        ], style={'padding': '30px', 'backgroundColor': colors['bg'], 'marginTop': '20px'}),
        
        # ========== 第 5 行：预言机分析 ==========
        html.Div([
            html.H2('Oracle Analysis', style={'marginTop': 0, 'marginBottom': '20px', 'color': colors['text']}),
            dash_table.DataTable(
                data=oracles.to_dict('records'),
                columns=[{"name": i, "id": i} for i in oracles.columns],
                style_cell={'padding': '10px', 'fontFamily': 'Arial, sans-serif'},
                style_header={
                    'backgroundColor': colors['primary'],
                    'color': 'white',
                    'fontWeight': 'bold',
                    'textAlign': 'left'
                },
                style_data_conditional=[
                    {'if': {'row_index': 'odd'}, 'backgroundColor': colors['light_bg']}
                ]
            )
        ], style={'padding': '30px', 'backgroundColor': colors['bg'], 'marginTop': '20px'}),
        
        # Footer
        html.Div([
            html.P('Real-time MEV Analysis Dashboard | Research by Aileen', style={
                'margin': 0, 'fontSize': '12px', 'color': '#7f8c8d', 'textAlign': 'center'
            })
        ], style={'padding': '20px', 'borderTop': '1px solid #ecf0f1', 'marginTop': '30px'})
    ], style={'maxWidth': '1200px', 'margin': '0 auto', 'padding': '0 20px'})
    
], style={'fontFamily': 'Arial, sans-serif', 'backgroundColor': colors['light_bg'], 'minHeight': '100vh'})

# ========== 启动 ==========
if __name__ == '__main__':
    print("\n🚀 Solana pAMM MEV Analysis Dashboard")
    print("📊 Access at: http://127.0.0.1:8050/")
    print("⏹️ Press Ctrl+C to stop\n")
    app.run(debug=True, host='0.0.0.0', port=8050)
