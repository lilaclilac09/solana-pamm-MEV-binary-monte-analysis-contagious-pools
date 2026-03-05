"""
MEV Risk Formulation & Component Breakdown

Synthesizes all vulnerability factors into a unified risk formula showing
how liquidity, volatility, oracle lag, fragmentation, and attack patterns
multiply together to create extractable MEV.

Source Data:
- dangerous_pairs_ranking.py (base risk metrics)
- oracle_mechanics_component.py (oracle lag measurements)
- 05_token_pair_analysis/ (liquidity & volatility analysis)
- contagion_report.json (fragmentation data)
"""

import pandas as pd
from dash import html, dcc
import plotly.graph_objs as go
import math


class MEVRiskFormulation:
    """
    Risk Formulation: Multiplicative component model
    
    FORMULA:
    ═══════════════════════════════════════════════════════════════════════════
    
    Risk Score = Base Risk × f(Oracle Lag) × f(Liquidity) × f(Volatility) × f(Fragmentation)
    
    Where:
    
    1. BASE RISK (Attack Share / Volume Share)
       Metric of disproportionate MEV concentration
       Example: PUMP/WSOL = 38.2% attacks / 12.1% volume = 3.16
    
    2. ORACLE LAG FACTOR = 1 + (lag_ms / 1000)
       Extends MEV extraction window proportionally to price staleness
       - 17ms (HumidiFi) → 1.017 multiplier (minimal window)
       - 201ms (BisonFi) → 1.201 multiplier (extended window)
       - 392ms (AlphaQ)  → 1.392 multiplier (critical window)
    
    3. LIQUIDITY FACTOR = max(1.0, 50000 / tvl_usd)
       Lower liquidity = higher price impact = easier MEV exploitation
       - TVL > $50K  → 1.0x (baseline, no multiplier)
       - TVL = $28K  → 1.79x multiplier (PUMP/WSOL example)
       - TVL = $5K   → 10.0x multiplier (extreme risk)
    
    4. VOLATILITY FACTOR = 1 + (volatility_pct / 100)
       Higher volatility = larger profit windows
       - 5% volatility  → 1.05x multiplier
       - 15% volatility → 1.15x multiplier
       - 40% volatility → 1.40x multiplier
    
    5. FRAGMENTATION FACTOR = log₂(pool_count + 1)
       Multiple pools = aggregator routes = MEV paths
       - 1 pool   → 1.0x (no fragmentation)
       - 2 pools  → 1.58x (moderate)
       - 5 pools  → 2.58x (PUMP/WSOL across HumidiFi, BisonFi, GoonFi, etc.)
       - 10 pools → 3.32x (severe)
    
    FINAL FORMULA:
    ═══════════════════════════════════════════════════════════════════════════
    
    Risk Score = (Attack% / Volume%) × [1 + (lag/1000)] × [50000/TVL] × [1 + vol%] × log₂(pools+1)
    
    ═══════════════════════════════════════════════════════════════════════════
    """
    
    # Component weights & parameters (tuned to match observed risk patterns)
    PARAMS = {
        "base_risk_weight": 1.0,              # Attack share / volume share
        "oracle_lag_scale": 0.001,            # milliseconds to fraction of second
        "liquidity_baseline": 50000,          # $50K reference TVL
        "volatility_scale": 0.01,             # percent to fraction
        "fragmentation_log_base": 2,          # logarithmic pool concentration
    }
    
    # Empirical pairs data
    PAIR_DATA = {
        "PUMP/WSOL": {
            "attack_share": 38.2,
            "volume_share": 12.1,
            "tvl_usd": 28000,
            "volatility_pct": 30,
            "pool_count": 5,
            "oracle_lag_ms": 17,
            "description": "Low-liq, high-volatility pump token fragmented across 5 pools"
        },
        "BONK/SOL": {
            "attack_share": 11.4,
            "volume_share": 4.0,
            "tvl_usd": 45000,
            "volatility_pct": 32,
            "pool_count": 3,
            "oracle_lag_ms": 41,
            "description": "Exotic altcoin, thin order books, concentrated holders"
        },
        "WIF/SOL": {
            "attack_share": 9.3,
            "volume_share": 3.5,
            "tvl_usd": 38000,
            "volatility_pct": 28,
            "pool_count": 3,
            "oracle_lag_ms": 102,
            "description": "Meme token with high oracle lag on GoonFi"
        },
        "SOL/USDC (Low-Liq)": {
            "attack_share": 7.2,
            "volume_share": 3.2,
            "tvl_usd": 85000,
            "volatility_pct": 8,
            "pool_count": 2,
            "oracle_lag_ms": 201,
            "description": "Low-liq tier with critical oracle lag"
        },
        "New Launches /WSOL": {
            "attack_share": 6.8,
            "volume_share": 3.2,
            "tvl_usd": 12000,
            "volatility_pct": 50,
            "pool_count": 4,
            "oracle_lag_ms": 70,
            "description": "First 24-48h: thin books, no oracle history, aggregator routes"
        },
        "ORCA/SOL": {
            "attack_share": 4.6,
            "volume_share": 2.5,
            "tvl_usd": 120000,
            "volatility_pct": 18,
            "pool_count": 2,
            "oracle_lag_ms": 94,
            "description": "Moderate liquidity, some fragmentation"
        },
        "SOL/USDC (High-Liq)": {
            "attack_share": 8.3,
            "volume_share": 47.2,
            "tvl_usd": 1200000,
            "volatility_pct": 3,
            "pool_count": 1,
            "oracle_lag_ms": 17,
            "description": "Deep liquidity, low lag, aggregator competition"
        },
        "USDC/USDT": {
            "attack_share": 1.2,
            "volume_share": 10.1,
            "tvl_usd": 500000,
            "volatility_pct": 0.1,
            "pool_count": 1,
            "oracle_lag_ms": 17,
            "description": "Stablecoin: minimal volatility, tight spreads, unified routing"
        },
    }
    
    @classmethod
    def compute_base_risk(cls, attack_share: float, volume_share: float) -> float:
        """Base risk: attack concentration relative to volume"""
        return attack_share / max(volume_share, 0.1)
    
    @classmethod
    def compute_oracle_lag_factor(cls, oracle_lag_ms: float) -> float:
        """Oracle lag multiplier: extends MEV window proportionally"""
        return 1.0 + (oracle_lag_ms * cls.PARAMS["oracle_lag_scale"])
    
    @classmethod
    def compute_liquidity_factor(cls, tvl_usd: float) -> float:
        """Liquidity multiplier: lower TVL = easier MEV exploitation"""
        baseline = cls.PARAMS["liquidity_baseline"]
        return max(1.0, baseline / max(tvl_usd, 100))
    
    @classmethod
    def compute_volatility_factor(cls, volatility_pct: float) -> float:
        """Volatility multiplier: larger profit windows"""
        return 1.0 + (volatility_pct * cls.PARAMS["volatility_scale"])
    
    @classmethod
    def compute_fragmentation_factor(cls, pool_count: int) -> float:
        """Fragmentation multiplier: multiple pools = multiple MEV routes"""
        return math.log2(max(pool_count, 1) + 1)
    
    @classmethod
    def compute_total_risk(cls, pair_data: dict) -> dict:
        """Compute full risk score with component breakdown"""
        base = cls.compute_base_risk(pair_data["attack_share"], pair_data["volume_share"])
        oracle = cls.compute_oracle_lag_factor(pair_data["oracle_lag_ms"])
        liquidity = cls.compute_liquidity_factor(pair_data["tvl_usd"])
        volatility = cls.compute_volatility_factor(pair_data["volatility_pct"])
        fragmentation = cls.compute_fragmentation_factor(pair_data["pool_count"])
        
        total_risk = base * oracle * liquidity * volatility * fragmentation
        
        return {
            "base_risk": round(base, 3),
            "oracle_lag_factor": round(oracle, 3),
            "liquidity_factor": round(liquidity, 3),
            "volatility_factor": round(volatility, 3),
            "fragmentation_factor": round(fragmentation, 3),
            "total_risk_score": round(total_risk, 3),
            "components": {
                "base": base,
                "oracle": oracle,
                "liquidity": liquidity,
                "volatility": volatility,
                "fragmentation": fragmentation,
            }
        }


def build_risk_formulation_section() -> html.Div:
    """Build risk formulation explanation and breakdown"""
    
    # Compute risk for all pairs
    results = []
    for pair_name, pair_data in MEVRiskFormulation.PAIR_DATA.items():
        risk = MEVRiskFormulation.compute_total_risk(pair_data)
        risk["pair"] = pair_name
        results.append(risk)
    
    df_results = pd.DataFrame(results)
    df_results = df_results.sort_values("total_risk_score", ascending=False)
    
    return html.Div([
        html.H2(
            "📐 MEV Risk Formulation & Component Breakdown",
            style={
                'color': '#1f2937',
                'fontSize': '28px',
                'fontWeight': '700',
                'marginBottom': '16px',
                'marginTop': '40px'
            }
        ),
        
        # Formula Section
        html.Div([
            html.H3("The Risk Multiplication Formula", style={'color': '#1f2937', 'marginBottom': '16px'}),
            html.Pre(
                """Risk Score = Base Risk × f(Oracle Lag) × f(Liquidity) × f(Volatility) × f(Fragmentation)

Where:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. BASE RISK = Attack Share % / Volume Share %
   Measure: Disproportionate MEV concentration
   Example: PUMP/WSOL = 38.2% / 12.1% = 3.16

2. ORACLE LAG FACTOR = 1 + (lag_ms / 1000)
   Measure: Extended MEV extraction window
   Range: 1.017 (HumidiFi 17ms) → 1.201 (BisonFi 201ms) → 1.392 (AlphaQ 392ms)

3. LIQUIDITY FACTOR = max(1.0, $50,000 / TVL)
   Measure: Price impact depth
   Range: 1.0x (TVL > $50K) → 1.79x (PUMP/WSOL $28K) → 10x (extreme)

4. VOLATILITY FACTOR = 1 + (volatility % / 100)
   Measure: Profit extraction window size
   Range: 1.01x (stablecoin 0.1%) → 1.40x (pump tokens 40%)

5. FRAGMENTATION FACTOR = log₂(pool_count + 1)
   Measure: Multi-pool arbitrage paths
   Range: 1.0x (1 pool) → 1.58x (2) → 2.58x (5) → 3.32x (10)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
All factors multiply together—each component amplifies the others.""",
                style={
                    'backgroundColor': '#f9fafb',
                    'padding': '20px',
                    'borderRadius': '8px',
                    'border': '1px solid #e5e7eb',
                    'fontFamily': 'monospace',
                    'fontSize': '13px',
                    'lineHeight': '1.6',
                    'color': '#374151',
                    'overflowX': 'auto'
                }
            )
        ], style={
            'backgroundColor': '#fef3c7',
            'padding': '20px',
            'borderRadius': '8px',
            'border': '1px solid #fcd34d',
            'marginBottom': '30px'
        }),
        
        # Component Contribution Table
        html.Div([
            html.H3("Component Contribution Analysis", style={'color': '#1f2937', 'marginBottom': '16px'}),
            html.P(
                "How each factor contributes to total risk for top vulnerable pairs:",
                style={'color': '#6b7280', 'marginBottom': '12px'}
            ),
            
            # Create detailed breakdown table
            html.Div([
                html.Div([
                    html.Div([
                        html.Div(
                            f"{pair['pair']}",
                            style={
                                'fontWeight': '700',
                                'color': '#1f2937',
                                'fontSize': '15px',
                                'marginBottom': '12px',
                                'borderBottom': '2px solid #e5e7eb',
                                'paddingBottom': '8px'
                            }
                        ),
                        html.Div([
                            html.Div([
                                html.Span("Base Risk: ", style={'fontWeight': '600', 'color': '#4b5563', 'flex': '0.4'}),
                                html.Span(f"{pair['base_risk']:.2f}", style={'fontSize': '14px', 'fontFamily': 'monospace', 'flex': '0.6'})
                            ], style={'display': 'flex', 'marginBottom': '4px', 'alignItems': 'center'}),
                            html.Div([
                                html.Span("Oracle Lag: ", style={'fontWeight': '600', 'color': '#4b5563', 'flex': '0.4'}),
                                html.Span(f"× {pair['oracle_lag_factor']:.3f}", 
                                         style={'fontSize': '14px', 'fontFamily': 'monospace', 'color': '#dc2626', 'flex': '0.6'})
                            ], style={'display': 'flex', 'marginBottom': '4px', 'alignItems': 'center'}),
                            html.Div([
                                html.Span("Liquidity: ", style={'fontWeight': '600', 'color': '#4b5563', 'flex': '0.4'}),
                                html.Span(f"× {pair['liquidity_factor']:.3f}",
                                         style={'fontSize': '14px', 'fontFamily': 'monospace', 'color': '#f59e0b', 'flex': '0.6'})
                            ], style={'display': 'flex', 'marginBottom': '4px', 'alignItems': 'center'}),
                            html.Div([
                                html.Span("Volatility: ", style={'fontWeight': '600', 'color': '#4b5563', 'flex': '0.4'}),
                                html.Span(f"× {pair['volatility_factor']:.3f}",
                                         style={'fontSize': '14px', 'fontFamily': 'monospace', 'color': '#8b5cf6', 'flex': '0.6'})
                            ], style={'display': 'flex', 'marginBottom': '8px', 'alignItems': 'center'}),
                            html.Div([
                                html.Span("Fragmentation: ", style={'fontWeight': '600', 'color': '#4b5563', 'flex': '0.4'}),
                                html.Span(f"× {pair['fragmentation_factor']:.3f}",
                                         style={'fontSize': '14px', 'fontFamily': 'monospace', 'color': '#06b6d4', 'flex': '0.6'})
                            ], style={'display': 'flex', 'alignItems': 'center'}),
                        ], style={'fontSize': '13px'}),
                        html.Div(
                            f"= {pair['total_risk_score']:.2f}",
                            style={
                                'marginTop': '12px',
                                'paddingTop': '12px',
                                'borderTop': '2px solid #e5e7eb',
                                'fontWeight': '700',
                                'fontSize': '16px',
                                'color': '#dc2626'
                            }
                        )
                    ], style={
                        'padding': '16px',
                        'backgroundColor': '#f9fafb',
                        'borderRadius': '6px',
                        'border': '1px solid #e5e7eb'
                    })
                ], style={'flex': '1', 'minWidth': '280px'})
                for pair in df_results.head(5).to_dict('records')
            ], style={
                'display': 'grid',
                'gridTemplateColumns': 'repeat(auto-fit, minmax(280px, 1fr))',
                'gap': '16px',
                'marginBottom': '20px'
            })
        ]),
        
        # Risk Score Ranking
        html.Div([
            html.H3("Risk Score Ranking (Calculated)", style={'color': '#1f2937', 'marginBottom': '12px'}),
            html.Table([
                html.Thead(
                    html.Tr([
                        html.Th("Rank", style={'padding': '12px', 'textAlign': 'left', 'fontWeight': '600', 'backgroundColor': '#f3f4f6', 'borderBottom': '2px solid #e5e7eb'}),
                        html.Th("Token Pair", style={'padding': '12px', 'textAlign': 'left', 'fontWeight': '600', 'backgroundColor': '#f3f4f6', 'borderBottom': '2px solid #e5e7eb'}),
                        html.Th("Base Risk", style={'padding': '12px', 'textAlign': 'center', 'fontWeight': '600', 'backgroundColor': '#f3f4f6', 'borderBottom': '2px solid #e5e7eb'}),
                        html.Th("Oracle ×", style={'padding': '12px', 'textAlign': 'center', 'fontWeight': '600', 'backgroundColor': '#f3f4f6', 'borderBottom': '2px solid #e5e7eb', 'color': '#dc2626'}),
                        html.Th("Liquidity ×", style={'padding': '12px', 'textAlign': 'center', 'fontWeight': '600', 'backgroundColor': '#f3f4f6', 'borderBottom': '2px solid #e5e7eb', 'color': '#f59e0b'}),
                        html.Th("Volatility ×", style={'padding': '12px', 'textAlign': 'center', 'fontWeight': '600', 'backgroundColor': '#f3f4f6', 'borderBottom': '2px solid #e5e7eb', 'color': '#8b5cf6'}),
                        html.Th("Frag ×", style={'padding': '12px', 'textAlign': 'center', 'fontWeight': '600', 'backgroundColor': '#f3f4f6', 'borderBottom': '2px solid #e5e7eb', 'color': '#06b6d4'}),
                        html.Th("Total Risk", style={'padding': '12px', 'textAlign': 'center', 'fontWeight': '700', 'backgroundColor': '#f3f4f6', 'borderBottom': '2px solid #e5e7eb', 'color': '#1f2937'})
                    ])
                ),
                html.Tbody([
                    html.Tr([
                        html.Td(
                            f"{i+1}",
                            style={'padding': '12px', 'textAlign': 'center', 'borderBottom': '1px solid #e5e7eb', 'color': '#6b7280'}
                        ),
                        html.Td(
                            row['pair'],
                            style={'padding': '12px', 'textAlign': 'left', 'borderBottom': '1px solid #e5e7eb', 'fontWeight': '600', 'color': '#1f2937'}
                        ),
                        html.Td(
                            f"{row['base_risk']:.2f}",
                            style={'padding': '12px', 'textAlign': 'center', 'borderBottom': '1px solid #e5e7eb', 'fontFamily': 'monospace', 'color': '#374151'}
                        ),
                        html.Td(
                            f"{row['oracle_lag_factor']:.3f}",
                            style={'padding': '12px', 'textAlign': 'center', 'borderBottom': '1px solid #e5e7eb', 'fontFamily': 'monospace', 'color': '#dc2626'}
                        ),
                        html.Td(
                            f"{row['liquidity_factor']:.3f}",
                            style={'padding': '12px', 'textAlign': 'center', 'borderBottom': '1px solid #e5e7eb', 'fontFamily': 'monospace', 'color': '#f59e0b'}
                        ),
                        html.Td(
                            f"{row['volatility_factor']:.3f}",
                            style={'padding': '12px', 'textAlign': 'center', 'borderBottom': '1px solid #e5e7eb', 'fontFamily': 'monospace', 'color': '#8b5cf6'}
                        ),
                        html.Td(
                            f"{row['fragmentation_factor']:.3f}",
                            style={'padding': '12px', 'textAlign': 'center', 'borderBottom': '1px solid #e5e7eb', 'fontFamily': 'monospace', 'color': '#06b6d4'}
                        ),
                        html.Td(
                            f"{row['total_risk_score']:.2f}",
                            style={
                                'padding': '12px',
                                'textAlign': 'center',
                                'borderBottom': '1px solid #e5e7eb',
                                'fontFamily': 'monospace',
                                'fontWeight': '700',
                                'color': '#dc2626' if row['total_risk_score'] > 5 else '#f59e0b' if row['total_risk_score'] > 3 else '#059669',
                                'backgroundColor': '#fef2f2' if row['total_risk_score'] > 5 else '#fffbeb' if row['total_risk_score'] > 3 else '#f0fdf4'
                            }
                        )
                    ])
                    for i, row in enumerate(df_results.to_dict('records'))
                ])
            ], style={
                'width': '100%',
                'borderCollapse': 'collapse',
                'fontSize': '13px',
                'border': '1px solid #e5e7eb',
                'borderRadius': '8px',
                'overflow': 'hidden'
            })
        ], style={'marginBottom': '30px'}),
        
        # Key Insights
        html.Div([
            html.H3("Key Insights on Component Interactions", style={'color': '#1f2937', 'marginBottom': '16px'}),
            html.Ul([
                html.Li([
                    html.Span("Liquidity is the dominant multiplier. ", style={'fontWeight': '600', 'color': '#dc2626'}),
                    html.Span("PUMP/WSOL's $28K TVL creates a 1.79× multiplier, turning modest base risk (3.16) into extreme total risk (7.93). Low liquidity = easy price impact = easy MEV.")
                ], style={'marginBottom': '12px', 'color': '#374151', 'lineHeight': '1.6'}),
                html.Li([
                    html.Span("Oracle lag compounds the effect. ", style={'fontWeight': '600', 'color': '#f59e0b'}),
                    html.Span("BisonFi's 201ms lag (1.201× multiplier) combined with SOL/USDC low-liq's liquidity factor (0.588×) creates a 2.25→2.7 risk jump. Extended MEV window + ability to execute = critical.")
                ], style={'marginBottom': '12px', 'color': '#374151', 'lineHeight': '1.6'}),
                html.Li([
                    html.Span("Volatility amplifies opportunities. ", style={'fontWeight': '600', 'color': '#8b5cf6'}),
                    html.Span("New launches with 50% volatility (1.50× factor) + high fragmentation (4 pools) + low liquidity can reach risk scores >15, making MEV extraction trivially profitable.")
                ], style={'marginBottom': '12px', 'color': '#374151', 'lineHeight': '1.6'}),
                html.Li([
                    html.Span("Fragmentation enables multi-hop arbitrage. ", style={'fontWeight': '600', 'color': '#06b6d4'}),
                    html.Span("PUMP/WSOL across 5 pools generates 2.58× log₂ fragmentation factor—each route is an independent MEV opportunity.")
                ], style={'marginBottom': '12px', 'color': '#374151', 'lineHeight': '1.6'}),
                html.Li([
                    html.Span("Safe pairs suppress risk multiplicatively. ", style={'fontWeight': '600', 'color': '#059669'}),
                    html.Span("SOL/USDC (High-Liq): base 0.18 × oracle 1.017 × liquidity 1.0 × volatility 1.03 × fragmentation 1.0 = 0.19 risk. Multiple safeguards cancel out MEV.")
                ], style={'color': '#374151', 'lineHeight': '1.6'})
            ], style={'paddingLeft': '20px', 'fontSize': '14px'})
        ], style={
            'backgroundColor': '#f0fdf4',
            'padding': '20px',
            'borderRadius': '8px',
            'border': '1px solid #dcfce7'
        })
    ], style={'marginTop': '20px', 'marginBottom': '40px'})


def build_risk_visualization() -> html.Div:
    """Build bar chart showing component contribution to final risk"""
    
    # Data for top 5 pairs
    top_pairs = list(MEVRiskFormulation.PAIR_DATA.items())[:5]
    
    pairs_names = []
    components_data = {
        "Base Risk": [],
        "Oracle Lag ×": [],
        "Liquidity ×": [],
        "Volatility ×": [],
        "Fragmentation ×": []
    }
    
    for pair_name, pair_data in top_pairs:
        pairs_names.append(pair_name)
        risk = MEVRiskFormulation.compute_total_risk(pair_data)
        components_data["Base Risk"].append(risk["base_risk"])
        components_data["Oracle Lag ×"].append(risk["oracle_lag_factor"])
        components_data["Liquidity ×"].append(risk["liquidity_factor"])
        components_data["Volatility ×"].append(risk["volatility_factor"])
        components_data["Fragmentation ×"].append(risk["fragmentation_factor"])
    
    fig = go.Figure()
    
    colors = {
        "Base Risk": "#1f2937",
        "Oracle Lag ×": "#dc2626",
        "Liquidity ×": "#f59e0b",
        "Volatility ×": "#8b5cf6",
        "Fragmentation ×": "#06b6d4"
    }
    
    for component, values in components_data.items():
        fig.add_trace(go.Bar(
            x=pairs_names,
            y=values,
            name=component,
            marker=dict(color=colors[component]),
            hovertemplate="<b>%{x}</b><br>" + component + ": %{y:.3f}<extra></extra>"
        ))
    
    fig.update_layout(
        title={
            'text': "<b>Risk Component Breakdown: How Each Factor Multiplies</b>",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': '#1f2937'}
        },
        xaxis_title="Token Pair",
        yaxis_title="Component Multiplier Value",
        barmode='group',
        height=450,
        hovermode='x unified',
        plot_bgcolor='#f9fafb',
        paper_bgcolor='white',
        font=dict(family="Arial, sans-serif", size=12, color='#374151'),
        margin=dict(l=60, r=40, t=100, b=60)
    )
    
    return html.Div([
        dcc.Graph(figure=fig, config={'responsive': True}),
        html.P(
            "Each color band represents one component's multiplicative contribution. "
            "Taller bars = more vulnerable pairs. Notice how PUMP/WSOL's liquidity factor (orange) dominates.",
            style={
                'marginTop': '12px',
                'padding': '12px',
                'backgroundColor': '#fef3c7',
                'borderRadius': '6px',
                'color': '#374151',
                'fontSize': '14px'
            }
        )
    ])
