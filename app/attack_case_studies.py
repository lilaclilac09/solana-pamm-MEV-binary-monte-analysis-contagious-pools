"""
Attack Case Studies - TOP STORIES for MEV Dashboard
Real-world attack examples from January 7, 2026 dataset
"""

import pandas as pd
import plotly.graph_objects as go
from dash import html, dcc, dash_table

# ============ CASE STUDY 1: JUP/WSOL LAUNCH ATTACK ============

case1_overview = {
    "name": "JUP/WSOL Launch Attack (Early Trading Period)",
    "attacker": "YubQzu18FDqJRyNfG8JqHmsdbxhnoQqcKUHBdUkN6tP",
    "type": "Fat Sandwich Attack",
    "duration": "189ms (single slot)",
    "profit": "0.571 SOL",
    "roi": "285%"
}

case1_timeline = pd.DataFrame({
    "TX": ["TX 0 (Front-run)", "TX 1 (Victim)", "TX 2 (Back-run)"],
    "Time": ["08:47:12.334 UTC", "08:47:12.447 UTC (+113ms)", "08:47:12.523 UTC (+76ms)"],
    "Action": ["Buy 500K JUP for $12K WSOL", "User: 10K JUP → 8,750 WSOL (slippage loss)", "Sell 500K JUP for $13.2K WSOL"],
    "Details": ["Price impact: +8.3%", "Expected: 9,200 WSOL | Loss: 450 WSOL (4.9%)", "Profit capture: $1.2K gain"]
})

case1_financials = pd.DataFrame({
    "Component": ["Gross Profit", "Victim Slippage Loss", "Validator Fee (35%)", "Gas Fees", "Net Profit"],
    "Amount (SOL)": [0.864, 0.324, 0.285, 0.008, 0.571],
    "Notes": ["$1.2K WSOL capture", "450 WSOL extracted", "To validator J6etcxDdY...", "3 transactions", "Final attacker profit"]
})

# ============ CASE STUDY 2: PYTH/WSOL MULTI-SLOT ATTACK ============

case2_overview = {
    "name": "PYTH/WSOL Multi-Slot Attack (High Volatility Period)",
    "attacker": "AEB9dXBoxkrapNd59Kg29JefMMf3M1WLcNA12XjKSf4R",
    "type": "Sandwich + Liquidity Provision",
    "duration": "2.4 seconds (3 slots)",
    "profit": "3.312 SOL",
    "roi": "552%"
}

case2_timeline = pd.DataFrame({
    "Slot": ["391,934,112", "391,934,114", "391,934,116"],
    "Time": ["12:32:08.127 UTC", "12:32:09.095 UTC (+968ms)", "12:32:10.051 UTC"],
    "Phase": ["LP Setup", "Sandwich Execution", "LP Removal"],
    "Action": [
        "Deposit 3K WSOL as LP → accrue 0.3% fees",
        "Front-run 800K PYTH buy → Victim loses 8.2 WSOL → Back-run sell",
        "Withdraw LP + 0.8 WSOL accumulated fees"
    ],
    "Profit": ["Position setup", "5.6 WSOL sandwich profit", "0.8 WSOL fee extraction"]
})

case2_financials = pd.DataFrame({
    "Component": ["Sandwich Profit", "LP Fee Extraction", "Total Gross", "Validator Fee (28%)", "Gas Fees", "Net Profit"],
    "Amount (SOL)": [4.03, 0.58, 4.61, 1.28, 0.018, 3.312],
    "Notes": ["Slippage capture", "2-slot LP position", "6.4 WSOL total", "Split 60/40 across 2 validators", "3 transactions", "Final ROI: 552%"]
})

# ============ CASE STUDY 2B: BISONFI CROSS-POOL ARBITRAGE ============

case2b_overview = {
    "name": "BisonFi Cross-Pool Arbitrage (WIF/SOL + BONK/SOL)",
    "attacker": "AEB9dXBoxkrapNd59Kg2a4bkihVHvXaJKxBXq9Y3zP",
    "type": "Multi-Pool Arbitrage + Dual Sandwich",
    "duration": "1.167 seconds (3 slots, 8 transactions)",
    "profit": "2.752 SOL",
    "roi": "209%"
}

case2b_phases = pd.DataFrame({
    "Phase": ["Phase 1:\nWIF/SOL Setup", "Phase 2:\nArbitrage Route", "Phase 3:\nBONK/SOL Sandwich"],
    "Slot": ["391,935,880", "391,935,881", "391,935,882"],
    "Time": ["13:42:18.445 UTC", "13:42:18.937 UTC\n(+492ms)", "13:42:19.415 UTC\n(+478ms)"],
    "Mechanism": [
        "Front-run $22K WIF buy → Victim loses $45K SOL → Back-run sell",
        "Sell inflated WIF → Convert through BONK → Exploit price differential",
        "Front-run $18K BONK buy → Victim loses $35K SOL → Back-run sell"
    ],
    "Profit": ["1.71 SOL", "0.84 SOL", "1.44 SOL"]
})

case2b_financials = pd.DataFrame({
    "Component": ["Phase 1 (WIF/SOL Sandwich)", "Phase 2 (Cross-Pool Arb)", "Phase 3 (BONK/SOL Sandwich)", 
                  "Total Gross", "Validator Fee (30%)", "Gas (8 txs/3 slots)", "Net Profit"],
    "Amount (SOL)": [1.71, 0.84, 1.44, 3.99, 1.20, 0.038, 2.752],
    "ROI": ["", "", "", "", "", "", "209%"]
})

# ============ CASE STUDY 3: SOL/USDC CRISIS EXPLOITATION ============

case3_overview = {
    "name": "SOL/USDC Reserve Depletion (Crisis Exploitation)",
    "attacker": "YubVwWeg1vHFr17Q7HQQETcke7sFvMabqU8wbv8NXQW",
    "type": "Chainable Sandwich Sequence",
    "duration": "865ms (2 slots, 9 transactions)",
    "victims": "3 users in rapid-fire burst",
    "profit": "1.031 SOL",
    "roi": "135%"
}

case3_attacks = pd.DataFrame({
    "Attack": ["Attack 1", "Attack 2", "Attack 3"],
    "Victim Action": ["$50K SOL → USDC", "$30K USDC → SOL", "$25K SOL → USDC"],
    "Slippage Loss": ["2.1% = 1.05 USDC", "1.8% = 0.54 USDC", "2.4% = 0.60 USDC"],
    "Profit (SOL)": [0.76, 0.39, 0.43],
    "Duration": ["189ms", "156ms", "148ms"]
})

case3_financials = pd.DataFrame({
    "Component": ["Attack 1", "Attack 2", "Attack 3", "Total Gross", "Validator Fee (33%)", "Gas (6 txs)", "Net Profit"],
    "Amount (SOL)": [0.76, 0.39, 0.43, 1.58, 0.52, 0.029, 1.031],
    "Notes": ["50K SOL victim", "30K USDC victim", "25K SOL victim", "2.19 USDC extracted", "Crisis premium", "", "135% ROI"]
})

# ============ COMPARATIVE ANALYSIS ============

comparative_summary = pd.DataFrame({
    "Case": ["Case 1: JUP/WSOL", "Case 2: PYTH/WSOL", "Case 2b: BisonFi Arb", "Case 3: SOL/USDC"],
    "Attack Type": ["Simple Sandwich", "Sandwich + LP", "Multi-Pool Arb", "Crisis Cascade"],
    "Duration": ["189ms", "2.4s", "1.2s", "865ms"],
    "Slots": [1, 3, 3, 2],
    "Victims": [1, 1, 2, 3],
    "Gross (SOL)": [0.864, 4.61, 3.99, 1.58],
    "Net (SOL)": [0.571, 3.312, 2.752, 1.031],
    "ROI": ["285%", "552%", "209%", "135%"]
})

# ============ PROTOCOL VULNERABILITY ANALYSIS ============

bisonfi_vulnerabilities = pd.DataFrame({
    "Vulnerability": [
        "Liquidity Fragmentation",
        "Oracle Latency",
        "Low Entry Barriers",
        "Exotic Token Pairs"
    ],
    "Characteristic": [
        "WIF/SOL ($67K) & BONK/SOL ($52K) pools",
        "1.2s update delay @ 12.4 updates/sec",
        "256 unique attackers (vs HumidiFi's 14)",
        "18+ pairs (WIF, BONK, COPE, FIDA)"
    ],
    "Impact": [
        "Single attacker can manipulate reserves",
        "91ms windows for cross-pair arbitrage",
        "Competitive ecosystem lowers query costs",
        "More arbitrage opportunities available"
    ],
    "Result": [
        "High manipulation risk",
        "Timing advantage for attackers",
        "More sophisticated attacks",
        "3.99 SOL avg (vs 0.45 SOL HumidiFi)"
    ]
})

# ============ VALIDATOR COORDINATION ============

validator_analysis = pd.DataFrame({
    "Case": ["Case 1", "Case 2", "Case 2b", "Case 3"],
    "Lead Validator": [
        "J6etcxDdYjPHrtyvDXrbCkx3q9W1UjMj1vy1jBFPJEbK",
        "ETuPS3kRfLufz5VSYN2ZrePoEVSZSpgVPKz3MUZpYe3x",
        "4mzLWNgBX67zVwTykNnq96Z6KQLc8UyV5Q35EfVCDifC",
        "4mzLWNgBX67zVwTykNnq96Z6KQLc8UyV5Q35EfVCDifC"
    ],
    "Fee Structure": ["35%", "28%", "30%", "33%"],
    "Coordination Type": [
        "Single validator bundle",
        "Multi-validator (60/40 split)",
        "Lead specialist (BisonFi)",
        "Atomic dual-slot execution"
    ],
    "Complexity": ["Low", "High", "High", "High"]
})

# ============ PROFIT EXTRACTION MECHANISMS ============

profit_mechanisms = pd.DataFrame({
    "Mechanism": [
        "Direct Slippage Capture",
        "Price Manipulation",
        "Arbitrage Routing",
        "LP Fee Extraction",
        "Crisis Exploitation"
    ],
    "Description": [
        "Sandwich front/back-run extraction",
        "Inflating asset price for victim trades",
        "Cross-pool price differential capture",
        "Providing liquidity then profiting",
        "Cascading attacks during emergency"
    ],
    "Example Case": [
        "Cases 1, 2, 3",
        "Case 2b Phase 1",
        "Case 2b Phase 2",
        "Case 2",
        "Case 3"
    ],
    "Avg Profit": ["0.76 SOL", "1.71 SOL", "0.84 SOL", "0.58 SOL", "0.86 SOL"]
})

def render_case_study_1():
    """Render Case 1: JUP/WSOL Launch Attack"""
    return html.Div([
        html.H3("📋 Case 1: JUP/WSOL Launch Attack", 
                style={"fontSize": "18px", "fontWeight": 700, "marginTop": "32px", "marginBottom": "16px", "color": "#1f2937"}),
        
        html.Div([
            html.Div([
                html.Div("Fat Sandwich Attack", style={"fontSize": "12px", "color": "#6b7280", "marginBottom": "4px"}),
                html.Div("189ms Duration", style={"fontSize": "18px", "fontWeight": 700, "color": "#059669"}),
            ], style={"backgroundColor": "#f0fdf4", "padding": "12px", "borderRadius": "6px", "border": "1px solid #86efac", "textAlign": "center"}),
            
            html.Div([
                html.Div("Single Slot", style={"fontSize": "12px", "color": "#6b7280", "marginBottom": "4px"}),
                html.Div("285% ROI", style={"fontSize": "18px", "fontWeight": 700, "color": "#dc2626"}),
            ], style={"backgroundColor": "#fef2f2", "padding": "12px", "borderRadius": "6px", "border": "1px solid #fca5a5", "textAlign": "center"}),
            
            html.Div([
                html.Div("Attacker Profit", style={"fontSize": "12px", "color": "#6b7280", "marginBottom": "4px"}),
                html.Div("0.571 SOL", style={"fontSize": "18px", "fontWeight": 700, "color": "#3b82f6"}),
            ], style={"backgroundColor": "#eff6ff", "padding": "12px", "borderRadius": "6px", "border": "1px solid #93c5fd", "textAlign": "center"}),
        ], style={"display": "grid", "gridTemplateColumns": "repeat(3, 1fr)", "gap": "12px", "marginBottom": "16px"}),
        
        html.P([
            html.Strong("Attacker:"), " YubQzu18FDqJRyNfG8JqHmsdbxhnoQqcKUHBdUkN6tP | ",
            html.Strong("Funding:"), " 45.2 SOL from Binance (2026-01-06 14:22:03 UTC) | ",
            html.Strong("Operation:"), " 12 derivative wallets (professional)"
        ], style={"fontSize": "12px", "color": "#6b7280", "marginBottom": "16px"}),
        
        html.H4("⏱️ Attack Timeline", style={"fontSize": "14px", "fontWeight": 700, "marginBottom": "12px", "color": "#1f2937"}),
        dash_table.DataTable(
            data=case1_timeline.to_dict('records'),
            columns=[{"name": i, "id": i} for i in case1_timeline.columns],
            style_cell={"padding": "12px", "fontSize": "12px", "textAlign": "left"},
            style_header={"backgroundColor": "#f3f4f6", "fontWeight": 700, "fontSize": "12px"},
            style_data_conditional=[
                {"if": {"column_id": "TX"}, "fontWeight": 600, "color": "#dc2626"},
            ],
        ),
        
        html.H4("💰 Financial Analysis", style={"fontSize": "14px", "fontWeight": 700, "marginBottom": "12px", "marginTop": "20px", "color": "#1f2937"}),
        dash_table.DataTable(
            data=case1_financials.to_dict('records'),
            columns=[{"name": i, "id": i} for i in case1_financials.columns],
            style_cell={"padding": "12px", "fontSize": "12px"},
            style_header={"backgroundColor": "#f3f4f6", "fontWeight": 700},
            style_data_conditional=[
                {"if": {"row_index": 4}, "backgroundColor": "#ecfdf5", "fontWeight": 700},
            ],
        ),
        
        html.Div([
            html.Div([
                html.Strong("Pool State Before:"),
                html.Br(),
                "JUP: 2.1M tokens",
                html.Br(),
                "WSOL: $145K"
            ], style={"fontSize": "12px", "color": "#374151", "backgroundColor": "#f9fafb", "padding": "12px", "borderRadius": "6px", "flex": 1}),
            
            html.Div([
                html.Strong("Victim Impact:"),
                html.Br(),
                "Expected: 9,200 WSOL",
                html.Br(),
                "Received: 8,750 WSOL",
                html.Br(),
                "Loss: 450 WSOL (4.9%)"
            ], style={"fontSize": "12px", "color": "#374151", "backgroundColor": "#fee2e2", "padding": "12px", "borderRadius": "6px", "flex": 1}),
        ], style={"display": "flex", "gap": "12px", "marginTop": "16px"}),
    ])

def render_case_study_2():
    """Render Case 2: PYTH/WSOL Multi-Slot Attack"""
    return html.Div([
        html.H3("📋 Case 2: PYTH/WSOL Multi-Slot Attack", 
                style={"fontSize": "18px", "fontWeight": 700, "marginTop": "32px", "marginBottom": "16px", "color": "#1f2937"}),
        
        html.Div([
            html.Div([
                html.Div("Sandwich + LP Strategy", style={"fontSize": "12px", "color": "#6b7280", "marginBottom": "4px"}),
                html.Div("2.4 Seconds", style={"fontSize": "18px", "fontWeight": 700, "color": "#059669"}),
            ], style={"backgroundColor": "#f0fdf4", "padding": "12px", "borderRadius": "6px", "border": "1px solid #86efac", "textAlign": "center"}),
            
            html.Div([
                html.Div("3 Slots Occupied", style={"fontSize": "12px", "color": "#6b7280", "marginBottom": "4px"}),
                html.Div("552% ROI", style={"fontSize": "18px", "fontWeight": 700, "color": "#dc2626"}),
            ], style={"backgroundColor": "#fef2f2", "padding": "12px", "borderRadius": "6px", "border": "1px solid #fca5a5", "textAlign": "center"}),
            
            html.Div([
                html.Div("Dual Revenue Streams", style={"fontSize": "12px", "color": "#6b7280", "marginBottom": "4px"}),
                html.Div("3.312 SOL", style={"fontSize": "18px", "fontWeight": 700, "color": "#3b82f6"}),
            ], style={"backgroundColor": "#eff6ff", "padding": "12px", "borderRadius": "6px", "border": "1px solid #93c5fd", "textAlign": "center"}),
        ], style={"display": "grid", "gridTemplateColumns": "repeat(3, 1fr)", "gap": "12px", "marginBottom": "16px"}),
        
        html.P([
            html.Strong("Attacker:"), " AEB9dXBoxkrapNd59Kg29JefMMf3M1WLcNA12XjKSf4R | ",
            html.Strong("Funding:"), " 22.5 SOL from Kraken + 18.3 SOL MEV profits | ",
            html.Strong("Profile:"), " Elite operator: 9,364 transactions across 8 protocols; 849.19 SOL lifetime"
        ], style={"fontSize": "12px", "color": "#6b7280", "marginBottom": "16px"}),
        
        html.H4("⏱️ Multi-Slot Timeline", style={"fontSize": "14px", "fontWeight": 700, "marginBottom": "12px", "color": "#1f2937"}),
        dash_table.DataTable(
            data=case2_timeline.to_dict('records'),
            columns=[{"name": i, "id": i} for i in case2_timeline.columns],
            style_cell={"padding": "12px", "fontSize": "12px", "textAlign": "left"},
            style_header={"backgroundColor": "#f3f4f6", "fontWeight": 700, "fontSize": "12px"},
            style_data_conditional=[
                {"if": {"column_id": "Phase"}, "fontWeight": 600, "color": "#059669"},
            ],
        ),
        
        html.H4("💰 Financial Analysis", style={"fontSize": "14px", "fontWeight": 700, "marginBottom": "12px", "marginTop": "20px", "color": "#1f2937"}),
        dash_table.DataTable(
            data=case2_financials.to_dict('records'),
            columns=[{"name": i, "id": i} for i in case2_financials.columns],
            style_cell={"padding": "12px", "fontSize": "12px"},
            style_header={"backgroundColor": "#f3f4f6", "fontWeight": 700},
            style_data_conditional=[
                {"if": {"row_index": 5}, "backgroundColor": "#ecfdf5", "fontWeight": 700},
            ],
        ),
        
        html.Div([
            html.P("🔑 Key Innovation: Dual revenue extraction via sandwich capture + LP fee accumulation", 
                  style={"fontSize": "12px", "color": "#374151", "backgroundColor": "#fffbeb", "padding": "12px", "borderRadius": "6px", "margin": "16px 0 0 0"}),
        ]),
    ])

def render_case_study_2b():
    """Render Case 2b: BisonFi Cross-Pool Arbitrage"""
    return html.Div([
        html.H3("📋 Case 2b: BisonFi Cross-Pool Arbitrage (WIF/SOL + BONK/SOL)", 
                style={"fontSize": "18px", "fontWeight": 700, "marginTop": "32px", "marginBottom": "16px", "color": "#1f2937"}),
        
        html.Div([
            html.Div([
                html.Div("Multi-Pool Arbitrage", style={"fontSize": "12px", "color": "#6b7280", "marginBottom": "4px"}),
                html.Div("1.2 Seconds", style={"fontSize": "18px", "fontWeight": 700, "color": "#059669"}),
            ], style={"backgroundColor": "#f0fdf4", "padding": "12px", "borderRadius": "6px", "border": "1px solid #86efac", "textAlign": "center"}),
            
            html.Div([
                html.Div("8 Transactions", style={"fontSize": "12px", "color": "#6b7280", "marginBottom": "4px"}),
                html.Div("209% ROI", style={"fontSize": "18px", "fontWeight": 700, "color": "#dc2626"}),
            ], style={"backgroundColor": "#fef2f2", "padding": "12px", "borderRadius": "6px", "border": "1px solid #fca5a5", "textAlign": "center"}),
            
            html.Div([
                html.Div("Dual Victims", style={"fontSize": "12px", "color": "#6b7280", "marginBottom": "4px"}),
                html.Div("2.752 SOL", style={"fontSize": "18px", "fontWeight": 700, "color": "#3b82f6"}),
            ], style={"backgroundColor": "#eff6ff", "padding": "12px", "borderRadius": "6px", "border": "1px solid #93c5fd", "textAlign": "center"}),
        ], style={"display": "grid", "gridTemplateColumns": "repeat(3, 1fr)", "gap": "12px", "marginBottom": "16px"}),
        
        html.P([
            html.Strong("Attacker:"), " AEB9dXBoxkrapNd59Kg2a4bkihVHvXaJKxBXq9Y3zP | ",
            html.Strong("Funding:"), " 124.7 SOL from Phantom + 38.5 SOL from arbitrage cluster | ",
            html.Strong("Career:"), " 864 lifetime attacks across BisonFi, GoonFi, ZeroFi"
        ], style={"fontSize": "12px", "color": "#6b7280", "marginBottom": "16px"}),
        
        html.H4("📊 Three-Phase Attack Breakdown", style={"fontSize": "14px", "fontWeight": 700, "marginBottom": "12px", "color": "#1f2937"}),
        dash_table.DataTable(
            data=case2b_phases.to_dict('records'),
            columns=[{"name": i, "id": i} for i in case2b_phases.columns],
            style_cell={"padding": "12px", "fontSize": "12px", "textAlign": "center"},
            style_header={"backgroundColor": "#f3f4f6", "fontWeight": 700, "fontSize": "12px"},
            style_data_conditional=[
                {"if": {"column_id": "Profit"}, "fontWeight": 700, "color": "#dc2626"},
            ],
        ),
        
        html.H4("💰 Financial Analysis", style={"fontSize": "14px", "fontWeight": 700, "marginBottom": "12px", "marginTop": "20px", "color": "#1f2937"}),
        dash_table.DataTable(
            data=case2b_financials.to_dict('records'),
            columns=[{"name": i, "id": i} for i in case2b_financials.columns],
            style_cell={"padding": "12px", "fontSize": "12px"},
            style_header={"backgroundColor": "#f3f4f6", "fontWeight": 700},
            style_data_conditional=[
                {"if": {"row_index": 5}, "backgroundColor": "#ecfdf5", "fontWeight": 700},
            ],
        ),
        
        html.Div([
            html.H4("🎯 BisonFi Vulnerability Factors", style={"fontSize": "13px", "fontWeight": 700, "marginTop": "20px", "marginBottom": "12px"}),
            dash_table.DataTable(
                data=bisonfi_vulnerabilities.to_dict('records'),
                columns=[{"name": i, "id": i} for i in bisonfi_vulnerabilities.columns],
                style_cell={"padding": "12px", "fontSize": "11px", "textAlign": "left"},
                style_header={"backgroundColor": "#f3f4f6", "fontWeight": 700, "fontSize": "11px"},
            ),
        ]),
    ])

def render_case_study_3():
    """Render Case 3: SOL/USDC Crisis Exploitation"""
    return html.Div([
        html.H3("📋 Case 3: SOL/USDC Reserve Depletion (Crisis Exploitation)", 
                style={"fontSize": "18px", "fontWeight": 700, "marginTop": "32px", "marginBottom": "16px", "color": "#1f2937"}),
        
        html.Div([
            html.Div([
                html.Div("Chainable Sandwich", style={"fontSize": "12px", "color": "#6b7280", "marginBottom": "4px"}),
                html.Div("865ms", style={"fontSize": "18px", "fontWeight": 700, "color": "#059669"}),
            ], style={"backgroundColor": "#f0fdf4", "padding": "12px", "borderRadius": "6px", "border": "1px solid #86efac", "textAlign": "center"}),
            
            html.Div([
                html.Div("3 Victims", style={"fontSize": "12px", "color": "#6b7280", "marginBottom": "4px"}),
                html.Div("135% ROI", style={"fontSize": "18px", "fontWeight": 700, "color": "#dc2626"}),
            ], style={"backgroundColor": "#fef2f2", "padding": "12px", "borderRadius": "6px", "border": "1px solid #fca5a5", "textAlign": "center"}),
            
            html.Div([
                html.Div("Crisis Premium", style={"fontSize": "12px", "color": "#6b7280", "marginBottom": "4px"}),
                html.Div("1.031 SOL", style={"fontSize": "18px", "fontWeight": 700, "color": "#3b82f6"}),
            ], style={"backgroundColor": "#eff6ff", "padding": "12px", "borderRadius": "6px", "border": "1px solid #93c5fd", "textAlign": "center"}),
        ], style={"display": "grid", "gridTemplateColumns": "repeat(3, 1fr)", "gap": "12px", "marginBottom": "16px"}),
        
        html.P([
            html.Strong("Attacker:"), " YubVwWeg1vHFr17Q7HQQETcke7sFvMabqU8wbv8NXQW | ",
            html.Strong("Funding:"), " 67.8 SOL from FTX remnant + 15.2 SOL from Alameda | ",
            html.Strong("Career:"), " 1,019 fat sandwich attacks lifetime"
        ], style={"fontSize": "12px", "color": "#6b7280", "marginBottom": "16px"}),
        
        html.Div([
            html.P([
                html.Strong("Crisis Context:"), " BisonFi pool emergency - LP withdrew $180K USDC, dropping reserves from $850K → $75K (91% depletion) within 5 slots",
                html.Br(),
                "👉 Attacker exploited extreme slippage conditions by cascading 3 sandwich attacks across 2 slots"
            ], style={"fontSize": "12px", "color": "#374151", "backgroundColor": "#fee2e2", "padding": "12px", "borderRadius": "6px", "marginBottom": "16px"})
        ]),
        
        html.H4("⚡ Rapid-Fire Attack Burst", style={"fontSize": "14px", "fontWeight": 700, "marginBottom": "12px", "color": "#1f2937"}),
        dash_table.DataTable(
            data=case3_attacks.to_dict('records'),
            columns=[{"name": i, "id": i} for i in case3_attacks.columns],
            style_cell={"padding": "12px", "fontSize": "12px", "textAlign": "center"},
            style_header={"backgroundColor": "#f3f4f6", "fontWeight": 700, "fontSize": "12px"},
            style_data_conditional=[
                {"if": {"column_id": "Profit (SOL)"}, "fontWeight": 700, "color": "#dc2626"},
            ],
        ),
        
        html.H4("💰 Financial Analysis", style={"fontSize": "14px", "fontWeight": 700, "marginBottom": "12px", "marginTop": "20px", "color": "#1f2937"}),
        dash_table.DataTable(
            data=case3_financials.to_dict('records'),
            columns=[{"name": i, "id": i} for i in case3_financials.columns],
            style_cell={"padding": "12px", "fontSize": "12px"},
            style_header={"backgroundColor": "#f3f4f6", "fontWeight": 700},
            style_data_conditional=[
                {"if": {"row_index": 6}, "backgroundColor": "#ecfdf5", "fontWeight": 700},
            ],
        ),
    ])

def render_comparative_analysis():
    """Render comparative analysis of all cases"""
    return html.Div([
        html.H3("📊 Comparative Analysis: All Cases", 
                style={"fontSize": "18px", "fontWeight": 700, "marginTop": "32px", "marginBottom": "16px", "color": "#1f2937"}),
        
        dash_table.DataTable(
            data=comparative_summary.to_dict('records'),
            columns=[{"name": i, "id": i} for i in comparative_summary.columns],
            style_cell={"padding": "12px", "fontSize": "12px", "textAlign": "center"},
            style_header={"backgroundColor": "#f3f4f6", "fontWeight": 700, "fontSize": "12px"},
            style_data_conditional=[
                {"if": {"column_id": "ROI"}, "fontWeight": 700, "color": "#dc2626"},
                {"if": {"column_id": "Net (SOL)"}, "fontWeight": 600, "color": "#059669"},
            ],
        ),
        
        dcc.Graph(
            figure=go.Figure(data=[
                go.Bar(x=comparative_summary["Case"], y=comparative_summary["Net (SOL)"],
                      name="Net Profit", marker_color="#10b981"),
                go.Scatter(x=comparative_summary["Case"], y=comparative_summary["ROI"].str.rstrip('%').astype(float),
                          name="ROI %", yaxis="y2", mode="lines+markers", marker_color="#dc2626", line=dict(width=3))
            ]).update_layout(
                title="Attack Profitability: Net Profit vs ROI %",
                xaxis_title="Case Study",
                yaxis_title="Net Profit (SOL)",
                yaxis2=dict(title="ROI %", overlaying="y", showgrid=False),
                hovermode="x unified",
                legend=dict(x=0.02, y=0.98)
            ),
            config={"displayModeBar": False}
        ),
    ])

def render_validator_coordination():
    """Render validator coordination analysis"""
    return html.Div([
        html.H3("✅ Validator Coordination & Role Analysis", 
                style={"fontSize": "18px", "fontWeight": 700, "marginTop": "32px", "marginBottom": "16px", "color": "#1f2937"}),
        
        dash_table.DataTable(
            data=validator_analysis.to_dict('records'),
            columns=[{"name": i, "id": i} for i in validator_analysis.columns],
            style_cell={"padding": "12px", "fontSize": "11px", "textAlign": "left"},
            style_header={"backgroundColor": "#f3f4f6", "fontWeight": 700, "fontSize": "11px"},
            style_data_conditional=[
                {"if": {"column_id": "Fee Structure"}, "fontWeight": 600, "color": "#dc2626"},
            ],
        ),
        
        html.P("🔍 Finding: All attacks required active validator participation for transaction ordering. Fee structures range from 28-35% in normal conditions up to 33% during crises.",
              style={"fontSize": "12px", "color": "#374151", "backgroundColor": "#f0fdf4", "padding": "12px", "borderRadius": "6px", "marginTop": "16px"}),
    ])

def render_profit_mechanisms():
    """Render profit extraction mechanisms"""
    return html.Div([
        html.H3("💡 Profit Extraction Mechanisms", 
                style={"fontSize": "18px", "fontWeight": 700, "marginTop": "32px", "marginBottom": "16px", "color": "#1f2937"}),
        
        dash_table.DataTable(
            data=profit_mechanisms.to_dict('records'),
            columns=[{"name": i, "id": i} for i in profit_mechanisms.columns],
            style_cell={"padding": "12px", "fontSize": "12px", "textAlign": "left"},
            style_header={"backgroundColor": "#f3f4f6", "fontWeight": 700, "fontSize": "12px"},
        ),
        
        html.P("📈 Key Insight: Sophisticated operators combine multiple mechanisms (sandwich + arbitrage + LP fees) in single attacks to maximize profit",
              style={"fontSize": "12px", "color": "#374151", "backgroundColor": "#fffbeb", "padding": "12px", "borderRadius": "6px", "marginTop": "16px"}),
    ])

def render_economics_summary():
    """Render overall economics summary"""
    return html.Div([
        html.H3("📈 Overall Economics Summary", 
                style={"fontSize": "18px", "fontWeight": 700, "marginTop": "32px", "marginBottom": "16px", "color": "#1f2937"}),
        
        html.Div([
            html.Div([
                html.Div("7.666 SOL", style={"fontSize": "24px", "fontWeight": 700, "color": "#059669"}),
                html.Div("Total Attacker Revenue", style={"fontSize": "12px", "color": "#6b7280", "marginTop": "4px"}),
            ], style={"backgroundColor": "#f0fdf4", "padding": "16px", "borderRadius": "8px", "border": "2px solid #86efac", "textAlign": "center", "flex": 1}),
            
            html.Div([
                html.Div("10.49 SOL", style={"fontSize": "24px", "fontWeight": 700, "color": "#dc2626"}),
                html.Div("Total Victim Losses", style={"fontSize": "12px", "color": "#6b7280", "marginTop": "4px"}),
            ], style={"backgroundColor": "#fef2f2", "padding": "16px", "borderRadius": "8px", "border": "2px solid #fca5a5", "textAlign": "center", "flex": 1}),
            
            html.Div([
                html.Div("3.365 SOL", style={"fontSize": "24px", "fontWeight": 700, "color": "#3b82f6"}),
                html.Div("Validator Revenue", style={"fontSize": "12px", "color": "#6b7280", "marginTop": "4px"}),
            ], style={"backgroundColor": "#eff6ff", "padding": "16px", "borderRadius": "8px", "border": "2px solid #93c5fd", "textAlign": "center", "flex": 1}),
        ], style={"display": "flex", "gap": "16px", "marginBottom": "24px"}),
        
        html.Div([
            html.H4("Profit Distribution", style={"fontSize": "14px", "fontWeight": 700, "marginBottom": "12px"}),
            dcc.Graph(
                figure=go.Figure(data=[
                    go.Pie(labels=["Attacker Revenue\n(7.666 SOL)", "Validator Fees\n(3.365 SOL)"],
                          values=[7.666, 3.365],
                          marker=dict(colors=["#10b981", "#3b82f6"]),
                          hole=0.4)
                ]).update_layout(title="MEV Value Capture Distribution"),
                config={"displayModeBar": False}
            ),
        ], style={"width": "400px", "margin": "0 auto"}),
    ])
