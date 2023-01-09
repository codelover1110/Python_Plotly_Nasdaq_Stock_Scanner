
from dash import Dash, dcc, html, Input, Output, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go

import pandas as pd
import numpy as np
import pandas_ta  as ta
import requests
from datetime import date

from decimal import Decimal
import math

from config import API_KEY, SYMBOLS

app = Dash(external_stylesheets=[dbc.themes.CYBORG])

def create_dropdown(option, id_value):

    return html.Div(
        [
            html.H5("SHARE PRICE",
            style={"padding": "0px 30px 0px 30px", "text-size": "15px", "margin": "0px"}),
            dcc.Dropdown(option, id=id_value, value=option[0], style={"width": "150px"}),
        ], style={"display": "flex", "margin": "auto", "align-items": "center"}
    )

app.layout = html.Div([

    html.Div([
        create_dropdown(SYMBOLS, "stock-select"),
    ], style={"display": "flex", "padding": "20px", "width": "800px", "justify-content": "space-around", "margin": "auto"}),

    html.Div(children=[
        html.Div([dcc.Graph(id="seconds_15")], style={"width": "75%"}),
        html.Div(children=[
            html.Div(children=[
                dash_table.DataTable(id="ask_table"),
            ], style={"width": "300px"}),
            html.Div(children=[
                dash_table.DataTable(id="bid_table"),
            ], style={"width": "300px"}),
            ], style= {"display":"flex", "align-items": "center", "background": "#111111"}
        ),
    ], style={"display": "flex", "margin": "auto"}),

    dcc.Graph(id="mins_15"),
    dcc.Graph(id="mins_15_vol"),
    html.Div([html.H5('Rolling Sharpe Ratio - 30 Seconds'),], style={"display": "flex", "justify-content":"center"}),
    dcc.Graph(id="rolling_share_30"),
    dcc.Interval(id="interval",  interval = 2000),

    ])


def table_styling(df, side):
    if side == "ask":
        font_color = "rgba(230, 31, 7)"
    if side == "bid":
        font_color = "rgba(13, 230, 49)"

    styles = []
    styles.append({
        "if": {"column_id":"Ask Price"},
        "color":font_color
    })
    styles.append({
        "if": {"column_id":"Bid Price"},
        "color":font_color
    })
    return styles


def aggregate_levels(levels_df, agg_level=Decimal('1'), side="bid"):

    if side == "bid":
        label_func = lambda x: x.left

    elif side == "ask":
        label_func = lambda x: x.right

    min_level = math.floor(Decimal(min(levels_df.price)) / agg_level - 1) * agg_level

    max_level = math.ceil(Decimal(max(levels_df.price)) / agg_level + 1) * agg_level

    level_bounds = [float(min_level + agg_level * x) for x in
                    range(int((max_level - min_level) / agg_level) + 1)
                    ]
    levels_df["bin"] = pd.cut(levels_df.price, bins=level_bounds, precision=10, right=True)

    levels_df = levels_df.groupby("bin").agg(
        quantity=("quantity", "sum")).reset_index()

    levels_df["price"] = levels_df.bin.apply(label_func)

    levels_df = levels_df[levels_df.quantity > 0]

    levels_df = levels_df[["price", "quantity"]]

    return levels_df


@app.callback(
    Output("bid_table", "data"),
    Output("bid_table", "style_data_conditional"),
    Output("ask_table", "data"),
    Output("ask_table", "style_data_conditional"),
    Input("interval","n_intervals"),
    Input("stock-select", "value"),
)
def update_orderbook(n_intervals, stock_pair):

    polygon_url = f"https://api.polygon.io/v3/quotes/{stock_pair}?apiKey={API_KEY}"
    data = requests.get(polygon_url).json()['results']
    data = pd.DataFrame(data)
    ask_df = pd.DataFrame().assign(price=data['ask_price'], quantity=data['ask_size'])
    bid_df = pd.DataFrame().assign(price=data['bid_price'], quantity=data['bid_size'])

    bid_df = bid_df[6:]
    ask_df = ask_df[6:]

    ask_df.columns = ['Ask Price', 'Ask Size']
    bid_df.columns = ['Bid Price', 'Bid Size']

    return (bid_df.to_dict("records"), table_styling(bid_df, "bid"), ask_df.to_dict("records"), table_styling(ask_df, "ask"))

@app.callback(
    Output("seconds_15","figure"),
    Output("mins_15","figure"),
    Output("mins_15_vol","figure"),
    Output("rolling_share_30","figure"),
    Input("interval","n_intervals"),
    Input("stock-select", "value"),
    )

def update_figure(n_intervals, stock_pair):

    today = date.today()
    symbol = stock_pair
    interval = 1
    interval_unit = 'minute'
    polygon_url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/{interval}/{interval_unit}/{today}/{today}?adjusted=true&sort=asc&limit=1000&apiKey={API_KEY}"
    data = requests.get(polygon_url).json()['results']
    data = pd.DataFrame(data)
    data["timestamp"] = pd.to_numeric(data.t) / 1000
    data.timestamp = pd.to_datetime(data.timestamp, unit = "s")
    data.c = pd.to_numeric(data.c)
    data.v = pd.to_numeric(data.v)
    rolling = (np.log(data['c']).diff(30).rolling(30))
    data[f"rolling_overlapping_sharpe_30S"] = (rolling.mean() / rolling.std())
    data['color'] = "red"
    data.loc[data['o'] - data['c']  >= 0, ['color']] = 'green'
    sec_15_d = data.iloc[500:]
    mins_15_d = data.iloc[14:]
    seconds_15 = px.line(x=sec_15_d.timestamp, y=sec_15_d.c, height = 300, template="plotly_dark")
    seconds_15.update_layout(xaxis_rangeslider_visible = False, height = 400, template="plotly_dark", yaxis_title = "Price (USD)",  xaxis_title = "")
    seconds_15.update_layout(transition_duration = 500)

    mins_15 = go.Figure(data = [go.Scatter(
                    x=mins_15_d.timestamp,
                    y=mins_15_d.c,
                    line = dict(color = 'red'),
                    name = "CLOSE")]
                    )
    mins_15.add_trace(
        go.Scatter(
            x=mins_15_d.timestamp,
            y=mins_15_d.vw,
            line = dict(color = 'green'),
            name = "VWAP"
        )
    )
    mins_15.update_layout(xaxis_rangeslider_visible = False, height = 400, template="plotly_dark", yaxis_title = "Price (USD)",  xaxis_title = "")
    mins_15.update_layout(transition_duration = 500)
    mins_15_vol = px.bar(x=mins_15_d.timestamp, y=mins_15_d.v, height = 1000, template="plotly_dark", color=mins_15_d['color'],)
    mins_15_vol.update_layout(xaxis_rangeslider_visible = False, height = 400, template="plotly_dark", yaxis_title = "Volume",  xaxis_title = "")
    mins_15_vol.update_layout(transition_duration = 500)
    rolling_share_30 = go.Figure(data=[go.Histogram(x=mins_15_d.rolling_overlapping_sharpe_30S, histnorm='probability')])
    rolling_share_30.update_layout(height = 400, template="plotly_dark", yaxis_title = "rolling_overlapping_sharpe_30S",  xaxis_title = "")
    rolling_share_30.update_layout(transition_duration = 500)

    return seconds_15, mins_15, mins_15_vol, rolling_share_30

if __name__ == '__main__':
    app.run_server()
