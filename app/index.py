#!/usr/bin/env python3
import dash
from dash import html, dash_table, dcc
import pandas as pd
import plotly.express as px

app = dash.Dash(__name__)
server = app.server

# Data
stats = pd.DataFrame({
    "Metric": ["Raw Events", "Validated", "Fat Sandwich", "Multi-Hop"],
    "Value": [1501, 636, 617, 19]
})

pools = pd.DataFrame({
    "Pool": ["HumidiFi", "BisonFi", "SolFiV2", "GoonFi", "TesseraV", "ZeroFi"],
    "Attacks": [593, 182, 176, 258, 157, 116],
    "Risk": ["HIGH", "MODERATE", "MODERATE", "HIGH", "MODERATE", "MODERATE"]
})

patterns = pd.DataFrame({
    "Type": ["Fat Sandwich", "Multi-Hop"],
    "Count": [617, 19]
})

app.layout = html.Div([
    html.H1("Solana pAMM MEV Analysis", style={"paddingBottom": "20px", "borderBottom": "2px solid #eee"}),
    
    html.Div([
        html.Div([html.Div("1,501", style={"fontSize": "32px", "fontWeight": 700}), html.Div("Raw Events")], 
                style={"padding": "16px", "border": "1px solid #eee", "borderRadius": "6px", "textAlign": "center"}),
        html.Div([html.Div("636", style={"fontSize": "32px", "fontWeight": 700, "color": "#059669"}), html.Div("Validated")], 
                style={"padding": "16px", "border": "1px solid #eee", "borderRadius": "6px", "textAlign": "center"}),
        html.Div([html.Div("617", style={"fontSize": "32px", "fontWeight": 700, "color": "#dc2626"}), html.Div("Fat Sandwich")], 
                style={"padding": "16px", "border": "1px solid #eee", "borderRadius": "6px", "textAlign": "center"}),
        html.Div([html.Div("19", style={"fontSize": "32px", "fontWeight": 700, "color": "#7c3aed"}), html.Div("Multi-Hop")], 
                style={"padding": "16px", "border": "1px solid #eee", "borderRadius": "6px", "textAlign": "center"}),
    ], style={"display": "grid", "gridTemplateColumns": "repeat(4, 1fr)", "gap": "16px", "marginBottom": "32px"}),
    
    html.H2("Attack Pattern Distribution", style={"fontSize": "18px", "fontWeight": 700, "marginBottom": "12px"}),
    dcc.Graph(figure=px.bar(patterns, x="Type", y="Count", color_discrete_sequence=["#dc2626", "#7c3aed"]),
              config={"displayModeBar": False}),
    
    html.H2("Pool Vulnerability Analysis", style={"fontSize": "18px", "fontWeight": 700, "marginBottom": "12px"}),
    dash_table.DataTable(
        data=pools.to_dict('records'),
        columns=[{"name": i, "id": i} for i in pools.columns],
        style_cell={"padding": "10px", "fontSize": "12px"},
        style_header={"backgroundColor": "#f3f4f6", "fontWeight": 600},
    ),
    
    html.Hr(style={"margin": "32px 0"}),
    html.P("Solana pAMM MEV | XGBoost + SMOTE | BisonFi Oracle Lag Root Cause | 2026-03-02",
           style={"textAlign": "center", "color": "#999", "fontSize": "11px"}),
], style={"maxWidth": "1200px", "margin": "0 auto", "padding": "24px", "fontFamily": "sans-serif", "backgroundColor": "#fff"})

if __name__ == "__main__":
    app.run_server(debug=False, host="0.0.0.0", port=8050)
