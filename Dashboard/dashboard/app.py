import dash
from dash import dcc, html, dash_table, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# =========================================================
# LOAD DATA
# =========================================================

df = pd.read_csv(
    'outputs/pricing_recommendations_v3.csv'
)

# Clean data
df = df.dropna(subset=['Final_Recommendation'])

df = df[
    df['Final_Recommendation']
    != 'Insufficient Data'
]

# Safe numeric conversions
for col in ['Avg_Price', 'Elasticity', 'Revenue_Uplift']:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

# Fill missing values
df['Elasticity'] = df['Elasticity'].fillna(0)
df['Revenue_Uplift'] = df['Revenue_Uplift'].fillna(0)

# =========================================================
# GROUP each recommendation into a broad ACTION bucket
# Used for scatter shape/colour logic
# =========================================================

def action_bucket(rec):
    r = str(rec).upper()
    if 'RAISE' in r or 'TEST' in r:
        return 'RAISE / TEST'
    if 'REDUCE' in r:
        return 'REDUCE'
    if 'HOLD' in r:
        return 'HOLD'
    return 'MONITOR'

df['Action_Bucket'] = df['Final_Recommendation'].apply(action_bucket)

# =========================================================
# DASH APP
# =========================================================

app = dash.Dash(__name__)
app.title = "Dynamic Pricing Intelligence Dashboard"

# =========================================================
# COLORS
# =========================================================

BG   = "#0f172a"
CARD = "#1e293b"
TEXT = "#e2e8f0"
SUBTEXT = "#94a3b8"

COLOR_MAP = {
    'RAISE PRICE +10% to +15%'    : '#16a34a',
    'RAISE PRICE +5% to +8%'      : '#22c55e',
    'TEST +3% Increase'            : '#84cc16',
    'HOLD — Inelastic Demand Protects': '#3b82f6',
    'HOLD — Elastic, Raising Will Hurt': '#60a5fa',
    'REDUCE -5%'                   : '#f97316',
    'REDUCE PRICE -8% to -12%'    : '#dc2626',
    'MONITOR — No Clear Signal'    : '#94a3b8'
}

# Bucket-level colours used for the scatter highlight logic
BUCKET_COLOR = {
    'RAISE / TEST' : '#22c55e',
    'HOLD'         : '#60a5fa',
    'REDUCE'       : '#ef4444',
    'MONITOR'      : '#94a3b8'
}

# =========================================================
# KPI VALUES
# =========================================================

total_uplift   = df['Revenue_Uplift'].sum()
positive_skus  = len(df[df['Revenue_Uplift'] > 0])
avg_elasticity = round(df['Elasticity'].mean(), 2)
overpriced     = len(df[df['Pricing_Flag'].astype(str).str.contains("Overpriced", na=False)])

# =========================================================
# CARD STYLE HELPER
# =========================================================

def card(extra=None):
    base = {
        'background'  : CARD,
        'borderRadius': '16px',
        'boxShadow'   : '0 4px 20px rgba(0,0,0,0.3)',
        'padding'     : '25px',
    }
    if extra:
        base.update(extra)
    return base

# =========================================================
# LAYOUT
# =========================================================

app.layout = html.Div([

    # --------------------------------------------------
    # HEADER
    # --------------------------------------------------
    html.Div([
        html.H1(
            "Dynamic Pricing Intelligence System",
            style={'color': 'white', 'fontSize': '42px',
                   'fontWeight': 'bold', 'marginBottom': '10px'}
        ),
        html.P(
            "Powered Pricing Optimization • Elasticity Modeling • Revenue Intelligence",
            style={'color': SUBTEXT, 'fontSize': '18px'}
        )
    ], style={
        'padding': '35px',
        'background': 'linear-gradient(90deg, #0f172a, #111827)',
        'borderBottom': '1px solid #334155'
    }),

    # --------------------------------------------------
    # KPI CARDS
    # --------------------------------------------------
    html.Div([

        html.Div([
            html.H3(f"£{total_uplift:,.0f}",
                    style={'color': '#4ade80', 'fontSize': '34px', 'marginBottom': '5px'}),
            html.P("Projected Revenue Uplift", style={'color': SUBTEXT})
        ], style={**card(), 'flex': '1', 'margin': '10px'}),

        html.Div([
            html.H3(f"{positive_skus}",
                    style={'color': '#60a5fa', 'fontSize': '34px', 'marginBottom': '5px'}),
            html.P("Positive Revenue Opportunity SKUs", style={'color': SUBTEXT})
        ], style={**card(), 'flex': '1', 'margin': '10px'}),

        html.Div([
            html.H3(f"{avg_elasticity}",
                    style={'color': '#facc15', 'fontSize': '34px', 'marginBottom': '5px'}),
            html.P("Average Elasticity", style={'color': SUBTEXT})
        ], style={**card(), 'flex': '1', 'margin': '10px'}),

        html.Div([
            html.H3(f"{overpriced}",
                    style={'color': '#f87171', 'fontSize': '34px', 'marginBottom': '5px'}),
            html.P("Overpriced SKUs", style={'color': SUBTEXT})
        ], style={**card(), 'flex': '1', 'margin': '10px'}),

    ], style={'display': 'flex', 'padding': '20px'}),

    # --------------------------------------------------
    # PRICING SIMULATOR
    # --------------------------------------------------
    html.Div([
        html.H2("Pricing Simulator", style={'color': 'white', 'marginBottom': '16px'}),

        dcc.Dropdown(
            id='recommendation-dropdown',
            options=[{'label': i, 'value': i}
                     for i in sorted(df['Final_Recommendation'].unique())],
            value='MONITOR — No Clear Signal',
            style={'width': '480px', 'color': 'black'}
        ),

        html.Br(),

        html.Div(id='simulator-output',
                 style={'fontSize': '20px', 'color': '#4ade80', 'fontWeight': 'bold'})

    ], style={**card(), 'margin': '20px'}),

    # --------------------------------------------------
    # SCATTER  +  PIE
    # --------------------------------------------------
    html.Div([

        html.Div([
            dcc.Graph(id='elasticity-scatter', config={'displayModeBar': True})
        ], style={**card({'padding': '10px'}), 'flex': '2', 'margin': '10px'}),

        html.Div([
            dcc.Graph(id='recommendation-pie', config={'displayModeBar': False})
        ], style={**card({'padding': '10px'}), 'flex': '1', 'margin': '10px'}),

    ], style={'display': 'flex', 'padding': '10px'}),

    # --------------------------------------------------
    # BAR CHART
    # --------------------------------------------------
    html.Div([
        dcc.Graph(id='uplift-bar-chart')
    ], style={**card(), 'margin': '20px', 'padding': '15px'}),

    # --------------------------------------------------
    # DATA TABLE
    # --------------------------------------------------
    html.Div([
        html.H2("SKU Pricing Recommendations", style={'color': 'white'}),
        dash_table.DataTable(
            data=df.head(200).round(2).to_dict('records'),
            columns=[{'name': c, 'id': c} for c in [
                'StockCode', 'Description', 'Avg_Price',
                'Recommended_Price', 'Elasticity',
                'Pricing_Flag', 'Final_Recommendation', 'Revenue_Uplift'
            ]],
            style_header={
                'backgroundColor': '#111827', 'color': 'white',
                'fontWeight': 'bold', 'fontSize': '14px'
            },
            style_cell={
                'backgroundColor': CARD, 'color': TEXT,
                'padding': '10px', 'fontSize': '12px',
                'border': '1px solid #334155', 'textAlign': 'left'
            },
            style_data_conditional=[
                {'if': {'filter_query': '{Revenue_Uplift} > 0'},
                 'backgroundColor': '#052e16', 'color': '#4ade80'},
                {'if': {'filter_query': '{Revenue_Uplift} < 0'},
                 'backgroundColor': '#450a0a', 'color': '#f87171'}
            ],
            page_size=15, sort_action='native', filter_action='native'
        )
    ], style={**card(), 'margin': '20px'}),

    # --------------------------------------------------
    # FOOTER
    # --------------------------------------------------
    html.Div([

        html.Div(style={
            'height': '2px',
            'background': 'linear-gradient(90deg, transparent, #4ade80, #60a5fa, #a78bfa, transparent)'
        }),

        html.Div([

            html.Div("SM", style={
                'width': '56px', 'height': '56px',
                'borderRadius': '50%',
                'background': 'linear-gradient(135deg, #4ade80, #60a5fa)',
                'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center',
                'fontSize': '20px', 'fontWeight': '800', 'color': '#0f172a',
                'marginBottom': '14px', 'boxShadow': '0 0 20px rgba(74,222,128,0.4)'
            }),

            html.P("Made by - Soumyadeep Mukherjee", style={
                'color': '#f1f5f9', 'fontSize': '22px', 'fontWeight': '700',
                'letterSpacing': '0.5px', 'marginBottom': '12px'
            }),

            html.Div([
                html.Span(tech, style={
                    'background': 'rgba(255,255,255,0.07)',
                    'border': '1px solid rgba(255,255,255,0.14)',
                    'borderRadius': '999px', 'padding': '5px 16px',
                    'fontSize': '13px', 'color': color,
                    'fontWeight': '600', 'margin': '4px'
                })
                for tech, color in [
                    ('🐍 Python', '#4ade80'), ('⚡ Dash', '#60a5fa'),
                    ('📊 Plotly', '#a78bfa'), ('🐼 Pandas', '#fb923c'),
                    ('🔢 NumPy', '#f472b6'), ('🤖 ML Concepts', '#facc15'),
                ]
            ], style={'display': 'flex', 'flexWrap': 'wrap',
                      'justifyContent': 'center', 'marginBottom': '18px'}),

            html.P("Dynamic Pricing Intelligence", style={
                'color': '#64748b', 'fontSize': '14px', 'letterSpacing': '1px'
            })

        ], style={
            'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center',
            'padding': '36px 45px 30px 45px',
            'background': 'linear-gradient(180deg, rgba(15,23,42,0) 0%, rgba(15,23,42,0.95) 100%)'
        })
    ])

], style={
    'background': 'linear-gradient(135deg, #0f172a, #111827)',
    'minHeight': '100vh',
    'fontFamily': 'Arial'
})


# =========================================================
# CALLBACK: SIMULATOR
# =========================================================

@app.callback(
    Output('simulator-output', 'children'),
    Input('recommendation-dropdown', 'value')
)
def update_simulator(selected):

    filtered = df[df['Final_Recommendation'] == selected]
    uplift   = filtered['Revenue_Uplift'].sum()
    count    = len(filtered)

    if 'Price_Change_Factor' in df.columns:
        avg_change = (filtered['Price_Change_Factor'].mean() - 1) * 100
        change_str = f" | Avg Price Change: {avg_change:+.1f}%"
    else:
        change_str = ""

    return (
        f"{count} SKUs{change_str} | "
        f"Projected Revenue Impact: £{uplift:,.0f}"
    )


# =========================================================
# CALLBACK: SCATTER — fully reactive to simulator dropdown
# =========================================================

@app.callback(
    Output('elasticity-scatter', 'figure'),
    Input('recommendation-dropdown', 'value')
)
def update_scatter(selected):

    # ----------------------------------------------------------
    # 1. Work on a clean copy; remove extreme outliers only
    # ----------------------------------------------------------
    plot_df = df.copy()
    plot_df = plot_df.dropna(subset=['Elasticity', 'Avg_Price'])
    plot_df = plot_df[
        (plot_df['Elasticity'] > -6) &
        (plot_df['Elasticity'] < 3)  &
        (plot_df['Avg_Price']  < 100)
    ]

    # ----------------------------------------------------------
    # 2. Split into SELECTED vs BACKGROUND
    # ----------------------------------------------------------
    sel_mask = plot_df['Final_Recommendation'] == selected
    bg_df    = plot_df[~sel_mask].copy()
    hi_df    = plot_df[ sel_mask].copy()

    # Bucket colour for the selected group
    sel_bucket = hi_df['Action_Bucket'].iloc[0] if len(hi_df) else 'MONITOR'
    sel_color  = BUCKET_COLOR.get(sel_bucket, '#94a3b8')

    fig = go.Figure()

    # ----------------------------------------------------------
    # 3. BACKGROUND traces — all non-selected points, dimmed
    #    Draw one trace per unique recommendation so we keep
    #    proper colour coding even in the dim layer
    # ----------------------------------------------------------
    for rec, grp in bg_df.groupby('Final_Recommendation'):
        fig.add_trace(go.Scatter(
            x=grp['Avg_Price'],
            y=grp['Elasticity'],
            mode='markers',
            name=rec,
            marker=dict(
                color=COLOR_MAP.get(rec, '#94a3b8'),
                size=7,
                opacity=0.18,       # very dim — still visible
                line=dict(width=0)
            ),
            hoverinfo='skip',       # no tooltip on background
            showlegend=False
        ))

    # ----------------------------------------------------------
    # 4. HIGHLIGHTED trace — selected recommendation
    #    Larger, vivid, with full hover
    # ----------------------------------------------------------
    if len(hi_df):
        # Scale marker size by |Revenue_Uplift| — bigger = more money
        raw_uplift = hi_df['Revenue_Uplift'].abs()
        max_up = raw_uplift.max() if raw_uplift.max() > 0 else 1
        sizes  = 10 + (raw_uplift / max_up) * 18   # range 10–28 px

        hover_text = (
            "<b>%{customdata[0]}</b><br>"
            "Price: £%{x:.2f}<br>"
            "Elasticity: %{y:.3f}<br>"
            "Revenue Uplift: £%{customdata[1]:,.0f}<br>"
            "<i>%{customdata[2]}</i>"
            "<extra></extra>"
        )

        fig.add_trace(go.Scatter(
            x=hi_df['Avg_Price'],
            y=hi_df['Elasticity'],
            mode='markers',
            name=selected,
            marker=dict(
                color=sel_color,
                size=sizes,
                opacity=0.95,
                line=dict(width=1.5, color='rgba(255,255,255,0.7)')
            ),
            customdata=np.column_stack([
                hi_df['Description'].fillna('—'),
                hi_df['Revenue_Uplift'],
                hi_df['Final_Recommendation']
            ]),
            hovertemplate=hover_text,
            showlegend=True
        ))

    # ----------------------------------------------------------
    # 5. REFERENCE LINES
    # ----------------------------------------------------------
    ref_lines = [
        (-0.5, '#4ade80', 'dot',  1.5, 'top left',    'Inelastic (−0.5)'),
        (-1.0, '#ef4444', 'dash', 2.0, 'top left',    'Unit Elastic (−1)'),
        (-2.0, '#fb923c', 'dot',  1.5, 'bottom left', 'Highly Elastic (−2)'),
    ]
    for y_val, color, dash, width, pos, label in ref_lines:
        fig.add_hline(
            y=y_val,
            line_dash=dash,
            line_color=color,
            line_width=width,
            annotation_text=f"  {label}",
            annotation_font=dict(size=12, color=color),
            annotation_position=pos
        )

    # Subtle zone shading
    fig.add_hrect(y0=-0.5, y1=0,   fillcolor='rgba(74,222,128,0.05)', line_width=0)
    fig.add_hrect(y0=-6,   y1=-2,  fillcolor='rgba(249,115,22,0.04)', line_width=0)

    # ----------------------------------------------------------
    # 6. COUNT ANNOTATION — how many points highlighted
    # ----------------------------------------------------------
    fig.add_annotation(
        text=f"<b>{len(hi_df)}</b> SKUs selected",
        xref='paper', yref='paper',
        x=0.99, y=0.99,
        xanchor='right', yanchor='top',
        showarrow=False,
        bgcolor='rgba(15,23,42,0.8)',
        bordercolor=sel_color,
        borderwidth=1,
        borderpad=6,
        font=dict(size=13, color=sel_color)
    )

    # ----------------------------------------------------------
    # 7. LAYOUT
    # ----------------------------------------------------------
    fig.update_layout(

        title=dict(
            text='Price Elasticity vs Current Product Price',
            x=0.5, xanchor='center',
            font=dict(size=21, color='white')
        ),

        paper_bgcolor=CARD,
        plot_bgcolor='rgba(15,23,42,0.6)',

        font=dict(color=TEXT, size=13),

        # Vertical legend on right — no title overlap
        legend=dict(
            title=dict(text='Selected Group', font=dict(size=12, color=SUBTEXT)),
            orientation='v',
            yanchor='middle', y=0.5,
            xanchor='left',   x=1.02,
            bgcolor='rgba(15,23,42,0.8)',
            bordercolor='rgba(255,255,255,0.1)',
            borderwidth=1,
            font=dict(size=12)
        ),

        margin=dict(l=80, r=220, t=65, b=80),
        height=620,

        xaxis=dict(
            title=dict(text='Current Product Price (£)',
                       font=dict(size=14, color=SUBTEXT)),
            tickfont=dict(size=12),
            gridcolor='rgba(255,255,255,0.05)',
            zeroline=True,
            zerolinecolor='rgba(255,255,255,0.12)',
            zerolinewidth=1
        ),

        yaxis=dict(
            title=dict(text='Price Elasticity of Demand',
                       font=dict(size=14, color=SUBTEXT)),
            tickfont=dict(size=12),
            gridcolor='rgba(255,255,255,0.05)',
            zeroline=True,
            zerolinecolor='rgba(255,255,255,0.12)',
            zerolinewidth=1
        ),

        hoverlabel=dict(
            bgcolor='#1e293b',
            bordercolor='rgba(255,255,255,0.2)',
            font=dict(size=13, color='white')
        ),

        hovermode='closest'
    )

    return fig


# =========================================================
# CALLBACK: PIE CHART
# =========================================================

@app.callback(
    Output('recommendation-pie', 'figure'),
    Input('recommendation-dropdown', 'value')
)
def update_pie(selected):

    counts = (
        df['Final_Recommendation']
        .value_counts()
        .reset_index()
    )
    counts.columns = ['Recommendation', 'Count']

    fig = px.pie(
        counts,
        names='Recommendation',
        values='Count',
        color='Recommendation',
        color_discrete_map=COLOR_MAP,
        hole=0.82,
        template='plotly_dark',
    )

    fig.update_traces(
        textposition='inside',
        textinfo='percent',
        textfont=dict(size=13, color='white'),
        insidetextorientation='horizontal',
        pull=[0.06 if r == selected else 0.01 for r in counts['Recommendation']],
        marker=dict(line=dict(color='rgba(15,23,42,0.9)', width=2)),
        hovertemplate='<b>%{label}</b><br>Count: %{value:,}<br>Share: %{percent}<extra></extra>'
    )

    total = counts['Count'].sum()
    fig.add_annotation(
        text=f"<b>{total:,}</b>", x=0.5, y=0.56,
        font=dict(size=26, color='white', family='Arial Black'),
        showarrow=False, align='center'
    )
    fig.add_annotation(
        text="Total SKUs", x=0.5, y=0.44,
        font=dict(size=12, color=SUBTEXT),
        showarrow=False, align='center'
    )

    fig.update_layout(
        title=dict(
            text='Recommendation Distribution',
            x=0.5, xanchor='center', y=0.97, yanchor='top',
            font=dict(size=19, color='white')
        ),
        paper_bgcolor=CARD,
        font=dict(color=TEXT, size=13),
        legend=dict(
            orientation='v',
            yanchor='middle', y=0.5,
            xanchor='left',   x=1.02,
            bgcolor='rgba(15,23,42,0.8)',
            bordercolor='rgba(255,255,255,0.1)',
            borderwidth=1,
            font=dict(size=11)
        ),
        margin=dict(t=60, b=30, l=10, r=180),
        height=700
    )

    return fig


# =========================================================
# CALLBACK: BAR CHART
# =========================================================

@app.callback(
    Output('uplift-bar-chart', 'figure'),
    Input('recommendation-dropdown', 'value')
)
def update_bar(selected):

    top = (
        df.sort_values('Revenue_Uplift', ascending=False)
        .head(15)
    )

    fig = px.bar(
        top,
        x='StockCode',
        y='Revenue_Uplift',
        color='Final_Recommendation',
        hover_data=['Description'],
        color_discrete_map=COLOR_MAP,
        template='plotly_dark',
        title='Top 15 Revenue Uplift Opportunities'
    )

    fig.update_layout(
        paper_bgcolor=CARD,
        plot_bgcolor='rgba(15,23,42,0.6)',
        font_color=TEXT,
        title=dict(x=0.5, xanchor='center', font=dict(size=19, color='white')),
        legend=dict(
            orientation='v',
            yanchor='middle', y=0.5,
            xanchor='left',   x=1.02,
            bgcolor='rgba(15,23,42,0.8)',
            bordercolor='rgba(255,255,255,0.1)',
            borderwidth=1,
            font=dict(size=11)
        ),
        margin=dict(l=70, r=200, t=60, b=70)
    )

    return fig


# =========================================================
# RUN APP
# =========================================================

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)