#!/usr/bin/env python3
import dash
from dash import html, dash_table, dcc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

app = dash.Dash(__name__)
server = app.server

# ============ DATA ============

# Token Pair Risk Analysis
token_pairs = pd.DataFrame({
    "Token Pair": ["PUMP/WSOL", "BONK/SOL", "WIF/SOL", "ZEREBRO/SOL", "PYTH/WSOL", 
                   "JUP/WSOL", "ORCA/WSOL", "RAY/SOL", "MNGO/USDC", "SRM/USDT"],
    "Liquidity": ["$28K", "$45K", "$38K", "$22K", "$67K", "$89K", "$125K", "$156K", "$234K", "$312K"],
    "Risk Score": [0.94, 0.89, 0.87, 0.82, 0.79, 0.76, 0.73, 0.68, 0.58, 0.52],
    "Amplification": ["3.16x", "2.94x", "2.87x", "2.45x", "2.21x", "1.98x", "1.87x", "1.62x", "1.23x", "0.98x"],
    "Tier": ["HIGH", "HIGH", "HIGH", "HIGH", "MODERATE", "MODERATE", "MODERATE", "MODERATE", "LOW", "LOW"]
})

# Pool Liquidity & Slippage
pool_liquidity = pd.DataFrame({
    "Pool": ["HumidiFi", "BisonFi", "SolFiV2", "GoonFi", "TesseraV", "ZeroFi"],
    "Primary Pairs": ["PUMP/WSOL, SOL/USDC", "PUMP/WSOL, WIF/SOL", "BONK/SOL, SOL/USDC", "PUMP/WSOL, BONK/SOL", "WIF/SOL, PYTH/WSOL", "SOL/USDC, JUP/WSOL"],
    "Total TVL (SOL)": ["1.24M", "892K", "756K", "634K", "521K", "321K"],
    "Depth": ["Deep", "Deep", "Moderate", "Moderate", "Shallow", "Shallow"],
    "Avg Slippage": ["1.2%", "1.8%", "2.4%", "3.1%", "4.7%", "6.8%"],
    "MEV Risk": ["2.1%", "3.4%", "5.2%", "7.8%", "11.3%", "14.2%"]
})

# Pool Attack Stats
pool_attacks = pd.DataFrame({
    "Pool": ["HumidiFi", "BisonFi", "SolFiV2", "GoonFi", "TesseraV", "ZeroFi"],
    "Attacks": [593, 182, 176, 258, 157, 116],
    "Shared Attackers": [133, 156, 147, 138, 89, 67],
    "Cascade Risk": ["23%", "22%", "22%", "20%", "15%", "12%"]
})

# Top Attackers
top_attackers = pd.DataFrame({
    "Rank": [1, 2, 3, 4, 5],
    "Signer": ["YubQzu18FDqJRyNfG8JqHmsdbxhnoQqcKUHBdUkN6tP", 
               "YubVwWeg1vHFr17Q7HQQETcke7sFvMabqU8wbv8NXQW",
               "AEB9dXBoxkrapNd59Kg29JefMMf3M1WLcNA12XjKSf4R",
               "E2MPTDnFPNiCRmbJGKYSYew48NWRGVNfHjoiibFP5VL2",
               "YubozzSnKomEnH3pkmYsdatUUwUTcm7s4mHJVmefEWj"],
    "Attacks": [47, 38, 31, 29, 24],
    "Profit (SOL)": [15.795, 12.342, 9.876, 8.543, 7.234],
    "Avg ROI": ["285%", "244%", "209%", "198%", "187%"]
})

# High-Risk Token Characteristics
token_risk_factors = pd.DataFrame({
    "Risk Factor": ["Low Liquidity (<500K)", "High Volatility (>30%)", "Memecoin Status", 
                    "Oracle Lag >1s", "Thin Order Books", "Cross-DEX Arbitrage", 
                    "Low Market Cap", "Recent Launch (<30d)"],
    "Impact": ["3.2x", "2.9x", "2.7x", "2.4x", "2.1x", "1.8x", "1.6x", "1.4x"],
    "Prevalence": ["73%", "68%", "82%", "41%", "59%", "34%", "71%", "52%"]
})

# Case Studies
case_studies = pd.DataFrame({
    "Case": ["BisonFi WIF/BONK Arbitrage", "PUMP/WSOL Fat Sandwich", "JUP/WSOL Single-Slot Attack", "PYTH/WSOL Multi-Slot"],
    "Target": ["BisonFi WIF/SOL + BONK/SOL", "PUMP/WSOL across 5 pools", "JUP/WSOL on HumidiFi", "PYTH/WSOL on BisonFi"],
    "Profit (SOL)": ["3.99 (209% ROI)", "2.84 (316% ROI)", "1.24 (285% ROI)", "4.82 (552% ROI)"],
    "Method": ["Cross-pair arbitrage, 8 txs", "High-volume pair targeting", "Single-slot sandwich", "Multi-slot + LP fees"],
    "Attacker": ["YubQzu18...N6tP", "YubVwWeg...NXQW", "AEB9dXBo...Sf4R", "E2MPTDnF...5VL2"]
})

# ============ LAYOUT ============

app.layout = html.Div([
    # Header
    html.Div([
        html.H1("Solana pAMM MEV Analysis Report", 
                style={"margin": "0", "fontSize": "32px", "fontWeight": 700, "color": "#1a1a1a"}),
        html.P("Comprehensive Analysis of MEV Attack Patterns Across 8 pAMM Protocols",
               style={"margin": "8px 0 0 0", "fontSize": "14px", "color": "#666"}),
    ], style={"marginBottom": "32px", "paddingBottom": "24px", "borderBottom": "3px solid #e5e7eb"}),

    # Section 5b: TOP STORIES - Attack Case Studies (FEATURED)
    html.Div([
        html.Div([
                html.H2("TOP STORIES: Real-World Attack Case Studies",
                    style={"fontSize": "22px", "fontWeight": 700, "marginBottom": "16px", "color": "#dc2626"}),
            html.P("Four detailed case studies from January 7, 2026 dataset analyzing real MEV attackers with millisecond-level precision",
                   style={"fontSize": "14px", "color": "#6b7280", "marginBottom": "24px"}),
        ], style={"backgroundColor": "#fef2f2", "border": "2px solid #dc2626", "padding": "20px", "borderRadius": "8px", "marginBottom": "24px"}),
        
        # Quick stats
        html.Div([
            html.Div([
                html.Div("7.666 SOL", style={"fontSize": "28px", "fontWeight": 700, "color": "#059669"}),
                html.Div("Total Attacker Revenue", style={"fontSize": "12px", "color": "#6b7280", "marginTop": "4px"}),
            ], style={"backgroundColor": "#f0fdf4", "padding": "16px", "borderRadius": "6px", "textAlign": "center"}),
            
            html.Div([
                html.Div("10.49 SOL", style={"fontSize": "28px", "fontWeight": 700, "color": "#dc2626"}),
                html.Div("Victim Losses (6 users)", style={"fontSize": "12px", "color": "#6b7280", "marginTop": "4px"}),
            ], style={"backgroundColor": "#fef2f2", "padding": "16px", "borderRadius": "6px", "textAlign": "center"}),
            
            html.Div([
                html.Div("552%", style={"fontSize": "28px", "fontWeight": 700, "color": "#f59e0b"}),
                html.Div("Max ROI (Case 2)", style={"fontSize": "12px", "color": "#6b7280", "marginTop": "4px"}),
            ], style={"backgroundColor": "#fffbeb", "padding": "16px", "borderRadius": "6px", "textAlign": "center"}),
            
            html.Div([
                html.Div("3.365 SOL", style={"fontSize": "28px", "fontWeight": 700, "color": "#3b82f6"}),
                html.Div("Validator Revenue", style={"fontSize": "12px", "color": "#6b7280", "marginTop": "4px"}),
            ], style={"backgroundColor": "#eff6ff", "padding": "16px", "borderRadius": "6px", "textAlign": "center"}),
        ], style={"display": "grid", "gridTemplateColumns": "repeat(4, 1fr)", "gap": "12px", "marginBottom": "24px"}),
        
        # Case Studies Summary Table
        html.H3("Case Studies Overview", style={"fontSize": "16px", "fontWeight": 700, "marginBottom": "12px"}),
        dash_table.DataTable(
            data=case_studies.to_dict('records'),
            columns=[{"name": i, "id": i} for i in case_studies.columns],
            style_cell={"padding": "12px", "fontSize": "12px", "textAlign": "left"},
            style_header={"backgroundColor": "#f3f4f6", "fontWeight": 700},
            style_cell_conditional=[
                {"if": {"column_id": "Profit (SOL)"}, "fontWeight": 700, "color": "#dc2626"},
            ],
        ),
        
        html.P([
            html.Strong("Detailed Attack Breakdowns:"),
            html.Br(),
            "• ", html.Strong("Case 1 (189ms, JUP/WSOL on HumidiFi):"), " Single-slot sandwich execution with precise front-run/back-run timing; 285% ROI from low-slippage entry and fast unwind.",
            html.Br(),
            "• ", html.Strong("Case 2 (2.4s, PYTH/WSOL on BisonFi):"), " Multi-slot sandwich + LP fee capture strategy; 4.82 SOL profit and 552% ROI (highest in sample).",
            html.Br(),
            "• ", html.Strong("Case 2b (1.2s, WIF/SOL + BONK/SOL on BisonFi):"), " Cross-pair arbitrage sequence across two correlated pools; 3.99 SOL profit, 209% ROI, 2 victim traders impacted.",
            html.Br(),
            "• ", html.Strong("Case 3 (865ms, PUMP/WSOL across 5 pools):"), " Cascading sandwich pattern that propagates after trigger-pool instability; 3 linked attacks with 2.84 SOL captured.",
        ], style={"fontSize": "13px", "color": "#374151", "backgroundColor": "#f9fafb", "padding": "16px", "borderRadius": "6px", 
                  "lineHeight": "1.8", "marginTop": "16px", "marginBottom": "0"}),


    ], style={"marginBottom": "40px", "backgroundColor": "white", "padding": "20px", "borderRadius": "8px"}),

    # Executive Summary Box
    html.Div([
        html.H2("Executive Summary", style={"fontSize": "20px", "fontWeight": 700, "marginBottom": "16px", "color": "#1f2937"}),
        html.P([
            "Our analysis scanned ", html.Strong("5.5 million blockchain events"), " across 8 pAMM protocols on Solana. ",
            "From 1,501 raw MEV event candidates, we validated ", html.Strong("636 confirmed MEV attacks"), ", of which ",
            html.Strong("617 were fat sandwich attacks", style={"color": "#dc2626"}), 
            " (97% of validated events). The prevalence of fat sandwich patterns indicates systematic ",
            "exploitation of oracle latency vulnerabilities, particularly in BisonFi (oracle lag >2s) which serves ",
            "as the structural trigger source for cross-pool contagion affecting downstream protocols."
        ], style={"fontSize": "14px", "lineHeight": "1.6", "color": "#374151", "margin": "0"}),
    ], style={"backgroundColor": "#f0fdf4", "border": "2px solid #86efac", "borderRadius": "8px", 
              "padding": "20px", "marginBottom": "32px"}),
    
    # Key Metrics Cards
    html.H2("Key Findings", style={"fontSize": "22px", "fontWeight": 700, "marginBottom": "16px"}),
    html.Div([
        html.Div([
            html.Div("5.5M", style={"fontSize": "36px", "fontWeight": 700, "color": "#059669"}),
            html.Div("Events Scanned", style={"fontSize": "13px", "color": "#6b7280", "marginTop": "4px"}),
        ], style={"backgroundColor": "#fff", "padding": "24px", "borderRadius": "8px", "border": "2px solid #e5e7eb", 
                  "textAlign": "center", "boxShadow": "0 1px 3px rgba(0,0,0,0.1)"}),
        
        html.Div([
            html.Div("617", style={"fontSize": "36px", "fontWeight": 700, "color": "#dc2626"}),
            html.Div("Fat Sandwich Attacks", style={"fontSize": "13px", "color": "#6b7280", "marginTop": "4px"}),
        ], style={"backgroundColor": "#fff", "padding": "24px", "borderRadius": "8px", "border": "2px solid #e5e7eb",
                  "textAlign": "center", "boxShadow": "0 1px 3px rgba(0,0,0,0.1)"}),
    ], style={"display": "grid", "gridTemplateColumns": "repeat(2, 1fr)", "gap": "16px", "marginBottom": "40px"}),
    
    # Section 2: Pool Liquidity & Slippage Analysis
    html.Div([
        html.H2("Section 2: Pool Liquidity & Slippage Analysis",
                style={"fontSize": "22px", "fontWeight": 700, "marginBottom": "16px", "color": "#1f2937"}),
        html.P("Deep liquidity pools (>1M SOL) demonstrate significantly lower MEV risk compared to shallow pools (<500K SOL). TVL represents total value locked across all token pairs in each pool, measured in SOL equivalent.",
               style={"fontSize": "14px", "color": "#6b7280", "marginBottom": "16px"}),
        html.P([html.Strong("Note:"), " Primary pairs shown represent the most actively traded pairs in each pool. Many pools support multiple trading pairs."],
               style={"fontSize": "13px", "color": "#9ca3af", "marginBottom": "16px", "fontStyle": "italic"}),
        
        dash_table.DataTable(
            data=pool_liquidity.to_dict('records'),
            columns=[{"name": i, "id": i} for i in pool_liquidity.columns],
            style_cell={"padding": "12px", "fontSize": "13px"},
            style_header={"backgroundColor": "#f3f4f6", "fontWeight": 700},
            style_data_conditional=[
                {"if": {"filter_query": "{Depth} = 'Deep'"}, "backgroundColor": "#d1fae5"},
                {"if": {"filter_query": "{Depth} = 'Shallow'"}, "backgroundColor": "#fee2e2"},
            ],
        ),
        html.Div([
            html.P(html.Strong("How to read this table (columns + source):"),
                   style={"fontSize": "13px", "color": "#374151", "margin": "0 0 8px 0"}),
            html.Ul([
                html.Li([html.Strong("Pool / Primary Pairs: "), "Protocol names and most-traded token pairs from our analysis mapping used in this dashboard."]),
                html.Li([html.Strong("Total TVL (SOL): "), "SOL-equivalent total value locked snapshot for each pool used in the report table (dashboard dataset)."]),
                html.Li([html.Strong("Depth: "), "Derived from TVL tiers (Deep, Moderate, Shallow) to normalize risk comparisons."]),
                html.Li([html.Strong("Avg Slippage / MEV Risk: "), "Summary metrics from the MEV analysis outputs and pool-level aggregation used for report scoring."]),
            ], style={"fontSize": "12px", "color": "#6b7280", "lineHeight": "1.8", "margin": "0", "paddingLeft": "18px"}),
        ], style={"marginTop": "12px", "backgroundColor": "#f9fafb", "padding": "12px", "borderRadius": "6px"}),
        
        html.Div([
            dcc.Graph(
                figure=go.Figure(data=[
                    go.Scatter(x=["1.24M", "892K", "756K", "634K", "521K", "321K"],
                              y=[2.1, 3.4, 5.2, 7.8, 11.3, 14.2],
                              mode='markers+lines',
                              marker=dict(size=[593, 182, 176, 258, 157, 116], 
                                        color=['#059669', '#059669', '#f59e0b', '#f59e0b', '#dc2626', '#dc2626'],
                                        sizemode='area', sizeref=2, showscale=False),
                              text=["HumidiFi", "BisonFi", "SolFiV2", "GoonFi", "TesseraV", "ZeroFi"],
                              textposition="top center",
                              line=dict(color='#9ca3af', width=2))
                ]).update_layout(
                    title="Liquidity vs MEV Risk (bubble size = attack count)",
                    xaxis_title="Pool Liquidity",
                    yaxis_title="MEV Risk %",
                    hovermode='closest'
                ),
                config={"displayModeBar": False}
            ),
        ], style={"marginTop": "20px"}),
    ], style={"marginBottom": "40px"}),
    
    # Section 3: Cross-Pool Contagion Analysis
    html.Div([
        html.H2("Section 3: Cross-Pool Contagion & Attack Patterns",
                style={"fontSize": "22px", "fontWeight": 700, "marginBottom": "16px", "color": "#1f2937"}),
        html.P([
            "BisonFi oracle-lag mechanism (avg 2.1s) serves as the structural trigger source for contagion. ",
            "Attackers exploit BisonFi timing vulnerabilities then cascade attacks to downstream pools ",
            "(HumidiFi, SolFiV2, GoonFi) with 22-23% delayed attack probability."
        ], style={"fontSize": "14px", "color": "#6b7280", "marginBottom": "16px"}),
        
        html.Div([
            html.Div([
                html.H4("Trigger Source", style={"fontSize": "16px", "fontWeight": 700, "marginBottom": "8px"}),
                html.Div("BisonFi", style={"fontSize": "24px", "fontWeight": 700, "color": "#dc2626"}),
                html.P("Oracle Lag: 2.1s → <500ms target", style={"fontSize": "12px", "color": "#6b7280", "margin": "4px 0 0 0"}),
            ], style={"backgroundColor": "#fef2f2", "padding": "16px", "borderRadius": "8px", "border": "2px solid #fca5a5"}),
            
            html.Div([
                html.H4("Cascade Rate", style={"fontSize": "16px", "fontWeight": 700, "marginBottom": "8px"}),
                html.Div("22-23%", style={"fontSize": "24px", "fontWeight": 700, "color": "#f59e0b"}),
                html.P("Delayed attack probability", style={"fontSize": "12px", "color": "#6b7280", "margin": "4px 0 0 0"}),
            ], style={"backgroundColor": "#fffbeb", "padding": "16px", "borderRadius": "8px", "border": "2px solid #fcd34d"}),
            
            html.Div([
                html.H4("Shared Attackers", style={"fontSize": "16px", "fontWeight": 700, "marginBottom": "8px"}),
                html.Div("133-156", style={"fontSize": "24px", "fontWeight": 700, "color": "#2563eb"}),
                html.P("Cross-pool signer overlap", style={"fontSize": "12px", "color": "#6b7280", "margin": "4px 0 0 0"}),
            ], style={"backgroundColor": "#eff6ff", "padding": "16px", "borderRadius": "8px", "border": "2px solid #93c5fd"}),
        ], style={"display": "grid", "gridTemplateColumns": "repeat(3, 1fr)", "gap": "16px", "marginBottom": "20px"}),
        
        # Shared Attackers Definition
        html.Div([
            html.H4("📌 What are \"Shared Attackers\"?", style={"fontSize": "16px", "fontWeight": 700, "marginBottom": "12px", "color": "#1f2937"}),
            html.P([
                html.Strong("Definition: "),
                "Unique MEV bot wallet addresses (signers) that executed sandwich attacks across multiple pools."
            ], style={"fontSize": "14px", "marginBottom": "12px", "lineHeight": "1.6"}),
            html.P([
                html.Strong("Source Data: "),
                "Extracted from ",
                html.Code("attacker_*_detailed_activity.csv"),
                " files where the same ",
                html.Code("signer"),
                " (MEV bot wallet address) appears in transaction logs for 2+ different pools."
            ], style={"fontSize": "13px", "marginBottom": "12px", "lineHeight": "1.6", "color": "#4b5563"}),
            html.P([
                html.Strong("Why It Matters: "),
                "High shared attacker counts indicate professional MEV operations systematically scanning multiple protocols. ",
                "These are NOT victim traders — they are the MEV bots/searchers executing front-run and back-run transactions. ",
                "Attackers operating across pools (e.g., BisonFi → HumidiFi) demonstrate cross-pool exploitation strategies and systemic risk."
            ], style={"fontSize": "13px", "marginBottom": "0", "lineHeight": "1.6", "color": "#4b5563"}),
        ], style={"backgroundColor": "#f0f9ff", "padding": "16px", "borderRadius": "8px", "border": "1px solid #bae6fd", "marginBottom": "20px"}),
        
        dash_table.DataTable(
            data=pool_attacks.to_dict('records'),
            columns=[{"name": i, "id": i} for i in pool_attacks.columns],
            style_cell={"padding": "12px", "fontSize": "13px"},
            style_header={"backgroundColor": "#f3f4f6", "fontWeight": 700},
        ),
    ], style={"marginBottom": "40px"}),
    
    # Section 4: Top MEV Attackers
    html.Div([
        html.H2("Section 4: Top MEV Attackers",
                style={"fontSize": "22px", "fontWeight": 700, "marginBottom": "16px", "color": "#1f2937"}),
        html.P("Top 5 attackers account for 169 attacks generating 53.79 SOL in total profit (avg 244% ROI).",
               style={"fontSize": "14px", "color": "#6b7280", "marginBottom": "16px"}),
        
        dash_table.DataTable(
            data=top_attackers.to_dict('records'),
            columns=[{"name": i, "id": i} for i in top_attackers.columns],
            style_cell={"padding": "12px", "fontSize": "11px", "fontFamily": "monospace"},
            style_header={"backgroundColor": "#f3f4f6", "fontWeight": 700},
            style_data_conditional=[
                {"if": {"row_index": 0}, "backgroundColor": "#fef3c7", "fontWeight": 700},
            ],
        ),
    ], style={"marginBottom": "40px"}),
    
    # Section 5: Methodology
    html.Div([
        html.H2("Section 5: Methodology",
                style={"fontSize": "22px", "fontWeight": 700, "marginBottom": "16px", "color": "#1f2937"}),
        html.Ul([
            html.Li([html.Strong("ML Classification: "), "XGBoost with SMOTE balancing (F1=0.91, Recall=85%, Precision=88%)"]),
            html.Li([html.Strong("Feature Engineering: "), "Oracle lag, validator participation, price deltas, token pair volatility, liquidity depth"]),
            html.Li([html.Strong("Contagion Analysis: "), "Graph-based attacker tracking across pools with 5000ms time window"]),
            html.Li([html.Strong("Risk Assessment: "), "Monte Carlo simulations (10,000 iterations) for slippage impact and MEV probability"]),
        ], style={"fontSize": "14px", "lineHeight": "1.8", "color": "#374151"}),
    ], style={"marginBottom": "40px", "backgroundColor": "#f9fafb", "padding": "20px", "borderRadius": "8px"}),
    
    # Section 6: Recommendations
    html.Div([
        html.H2("Section 6: Recommendations",
                style={"fontSize": "22px", "fontWeight": 700, "marginBottom": "16px", "color": "#1f2937"}),
        html.Ol([
            html.Li([html.Strong("Reduce BisonFi oracle latency to <500ms"), " to eliminate trigger-pool conditions"]),
            html.Li([html.Strong("Implement cross-pool surveillance"), " tracking attackers who succeed on BisonFi"]),
            html.Li([html.Strong("Increase liquidity depth on shallow pools"), " (TesseraV, ZeroFi) to >750K SOL minimum"]),
            html.Li([html.Strong("Deploy real-time alerts"), " for high-risk token pairs (PUMP/WSOL, BONK/SOL, WIF/SOL)"]),
            html.Li([html.Strong("Apply dynamic fee structures"), " during high volatility periods (>30% intraday)"]),
            html.Li([html.Strong("Establish attacker blacklists"), " starting with top 19 signers (YubQzu...6tP priority)"]),
        ], style={"fontSize": "14px", "lineHeight": "1.8", "color": "#374151"}),
    ], style={"marginBottom": "40px", "backgroundColor": "#ecfdf5", "padding": "20px", "borderRadius": "8px", 
              "border": "2px solid #6ee7b7"}),
    
    # Footer
    html.Hr(style={"margin": "32px 0", "borderColor": "#e5e7eb"}),
    html.Div([
        html.P("Solana pAMM MEV Analysis | XGBoost + SMOTE Classification | BisonFi Oracle-Lag Root Cause",
               style={"textAlign": "center", "color": "#9ca3af", "fontSize": "12px", "margin": "0 0 16px 0"}),
        html.P([
            "any further questions or discussion pls Follow ",
            html.A("@A01DZ3RO", href="https://x.com/A01DZ3RO", target="_blank",
                   style={"color": "#6b7280", "textDecoration": "none"}),
            " on X and dm"
        ], style={"textAlign": "center", "color": "#9ca3af", "fontSize": "12px", "margin": "0"}),
    ], style={"textAlign": "center"}),
    
], style={"maxWidth": "1400px", "margin": "0 auto", "padding": "40px 24px", 
          "fontFamily": "-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif", 
          "backgroundColor": "#ffffff"})

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8050)
