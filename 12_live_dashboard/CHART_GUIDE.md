#  MEV Dashboard - How Each Chart Was Made

##  LIVE DEMO
**Your Dashboard:** https://mev.aileena.xyz

---

##  CHART TYPE 1: BAR CHART
**Purpose:** Compare MEV profits across protocols

### Data:
```python
protocols_data = {
    'Protocol': ['HumidiFi', 'BisonFi', 'GoonFi', 'SolFiV2'],
    'MEV Profit (SOL)': [75.1, 11.232, 7.899, 6.5]
}
df = pd.DataFrame(protocols_data)
```

### Code:
```python
import plotly.express as px

chart = px.bar(
    df,
    x='Protocol',              # X-axis: Protocol names
    y='MEV Profit (SOL)',     # Y-axis: Profit amounts
    color='MEV Profit (SOL)', # Color bars by value
    color_continuous_scale='Purples'
)
```

### Result:
→ Purple bar chart showing HumidiFi dominates with 75.1 SOL

---

##  CHART TYPE 2: PIE CHART
**Purpose:** Show profit distribution as percentages

### Code:
```python
pie = px.pie(
    df,
    values='MEV Profit (SOL)',  # Size of slices
    names='Protocol',            # Labels
    hole=0.4                     # Makes it a donut
)
```

### Result:
→ Donut chart showing HumidiFi = 66.8% of total MEV

---

##  CHART TYPE 3: HEATMAP
**Purpose:** Show attacker overlap between pools

### Data:
```python
contagion = pd.DataFrame({
    'HumidiFi': [167, 44, 43],
    'BisonFi': [44, 182, 42],
    'GoonFi': [43, 42, 258]
}, index=['HumidiFi', 'BisonFi', 'GoonFi'])
```

### Code:
```python
heatmap = px.imshow(
    contagion,
    text_auto=True,          # Show numbers in cells
    color_continuous_scale='RdPu'
)
```

### Result:
→ Pink/purple grid showing HumidiFi-BisonFi share 44 attackers

---

##  CHART TYPE 4: SCATTER PLOT
**Purpose:** Show relationship between attacks and profit

### Code:
```python
scatter = px.scatter(
    df,
    x='Attacks',             # X-axis
    y='MEV Profit (SOL)',   # Y-axis
    size='MEV Profit (SOL)', # Bubble size
    color='Protocol'         # Color by protocol
)
```

### Result:
→ Bubble chart showing HumidiFi has most attacks AND profit

---

## ️ CHART TYPE 5: NETWORK GRAPH
**Purpose:** Visualize pool connections via shared attackers

### Step 1: Create network
```python
import networkx as nx

G = nx.Graph()
G.add_nodes_from(['HumidiFi', 'BisonFi', 'GoonFi'])
G.add_edge('HumidiFi', 'BisonFi', weight=44)  # 44 shared attackers
```

### Step 2: Position nodes
```python
pos = nx.spring_layout(G)
```

### Step 3: Create edges
```python
edge_x = []
edge_y = []
for edge in G.edges():
    x0, y0 = pos[edge[0]]
    x1, y1 = pos[edge[1]]
    edge_x.extend([x0, x1, None])
    edge_y.extend([y0, y1, None])
```

### Step 4: Create nodes
```python
node_x = [pos[node][0] for node in G.nodes()]
node_y = [pos[node][1] for node in G.nodes()]
```

### Step 5: Combine into graph
```python
import plotly.graph_objects as go

fig = go.Figure(
    data=[
        go.Scatter(x=edge_x, y=edge_y, mode='lines'),  # Lines
        go.Scatter(x=node_x, y=node_y, mode='markers+text')  # Nodes
    ]
)
```

### Result:
→ Interactive network showing pool interconnections

---

##  CHART TYPE 6: DATA TABLE
**Purpose:** Display attacker details

### Code:
```python
from dash import dash_table

table = dash_table.DataTable(
    data=attackers.to_dict('records'),
    columns=[{"name": i, "id": i} for i in attackers.columns],
    style_cell={'textAlign': 'left'}
)
```

### Result:
→ Sortable table of top attackers with profit/attack counts

---

##  PUTTING IT ALL TOGETHER

### Your Complete Dashboard =

```python
import dash
from dash import dcc, html
import plotly.express as px

# 1. Initialize app
app = dash.Dash(__name__)
server = app.server  # ← For Render deployment

# 2. Create layout
app.layout = html.Div([
    html.H1(' MEV Dashboard'),
    
    dcc.Tabs([
        # Tab 1
        dcc.Tab(label='Overview', children=[
            dcc.Graph(figure=bar_chart)
        ]),
        
        # Tab 2
        dcc.Tab(label='Distribution', children=[
            dcc.Graph(figure=pie_chart),
            dcc.Graph(figure=heatmap)
        ]),
        
        # ... more tabs ...
    ])
])

# 3. Run server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8050)
```

### Deployed to Render with:
```bash
# Build Command:
pip install -r 12_live_dashboard/requirements.txt

# Start Command:
cd 12_live_dashboard && gunicorn --bind 0.0.0.0:$PORT mev_dashboard:server
```

---

##  DATA FLOW

```
Your MEV Stats (Python dicts)
    ↓
pandas DataFrames
    ↓
Plotly Charts (px.bar, px.pie, etc.)
    ↓
Dash Layout (tabs + charts)
    ↓
Flask Server (app.server)
    ↓
Gunicorn (production server)
    ↓
Render (cloud hosting)
    ↓
https://mev.aileena.xyz (your live site!)
```

---

##  STYLING

### Colors Used:
```python
colors = {
    'primary': '#6C63FF',    # Purple (main color)
    'secondary': '#FF6584',  # Pink
    'accent': '#4ECDC4',     # Teal
    'gradient1': '#667EEA',  # Light purple
    'gradient2': '#764BA2'   # Dark purple
}
```

### Typography:
```python
font = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto'
```

### Layout:
- White background cards
- Rounded corners (15px)
- Subtle shadows
- Gradient header
- Responsive tabs

---

##  HOW TO MODIFY

### Add a new chart:
```python
# 1. Add to layout
dcc.Graph(
    figure=px.line(df, x='Date', y='Profit')
)
```

### Change colors:
```python
chart.update_layout(
    plot_bgcolor='#F5F7FA',  # Light gray
    paper_bgcolor='white'
)
```

### Add interactivity:
```python
from dash.dependencies import Input, Output

@app.callback(
    Output('my-graph', 'figure'),
    Input('my-dropdown', 'value')
)
def update_graph(selected_value):
    # Update chart based on dropdown
    return new_figure
```

---

##  KEY LIBRARIES

```python
dash==4.0.0              # Web framework
plotly==6.5.2            # Charts
pandas>=3.0.1            # Data manipulation
networkx==3.6.1          # Network graphs
gunicorn==21.2.0         # Production server
flask==3.0.0             # Web server (auto-included)
```

---

##  FEATURES ON YOUR DASHBOARD

1. **8 Interactive Tabs**
   - Overview statistics
   - MEV distribution
   - Top attackers
   - Contagion analysis
   - Validator behavior
   - Oracle analysis
   - ML models
   - Key findings

2. **Chart Types**
   - Bar charts (6)
   - Pie charts (1)
   - Heatmaps (1)
   - Scatter plots (2)
   - Network graphs (1)
   - Data tables (5)

3. **Interactivity**
   - Hover for details
   - Zoom/pan
   - Click to explore
   - Tab navigation

4. **Responsive Design**
   - Works on desktop
   - Works on mobile
   - Works on tablet

---

##  SUMMARY

**Your dashboard took:**
- 748 lines of Python
- 6 chart types
- 8 tabs of content
- Hours of MEV analysis

**And displays:**
- 112.9 SOL in MEV profits
- 1,617 attacks across 8 protocols
- 179 unique attackers
- Cross-pool contagion
- Validator behavior
- Oracle manipulation

**All accessible at:**
https://mev.aileena.xyz

---

##  QUICK TIPS

**To test locally:**
```bash
cd 12_live_dashboard
python3 mev_dashboard.py
# Visit http://localhost:8050
```

**To update live site:**
```bash
# Edit mev_dashboard.py
git add .
git commit -m "Update dashboard"
git push origin main
# Render auto-deploys in 2-3 min
```

**To add new data:**
```python
# Add to protocols_data dict
protocols_data['New Column'] = [1, 2, 3, ...]

# Use in chart
px.bar(df, x='Protocol', y='New Column')
```

---

 **Your dashboard is live and fully functional!**

Questions? Check [mev_dashboard.py](mev_dashboard.py) for the full source code.
