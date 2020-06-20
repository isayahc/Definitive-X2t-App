import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly
from app.Cloud import Cloud
import pandas as pd
from app.Frequency import IntraDay
import main
from flask import Flask


external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
c = Cloud()
x = c.get_s3_keys() + [IntraDay('spy',1).FileFormat()]

app.layout = html.Div(children=[
    html.Div(id='page-content'),
    html.H1(children='XAYTECH! XAYTECH! XAYTECH! XAYTECH!'),

    html.Div(children="files to choose from"),

    dcc.Dropdown(
        id='drop-down-data',
            options=[ {'label': i, 'value': i}  for i in x ],
            value= x[-1],

    ),
    dcc.Graph(id='live-update-graph'),

    html.Div(children='''
    Dash: A web application framework for Python.
    '''),

    dcc.Interval(
        id='interval-components',
        interval= 60*1000,
        n_intervals=0
    )
])

@app.callback(Output('live-update-graph','figure'),
[Input('interval-components', 'n_intervals')])
def update_graph_live(n):
    # c.downloadData('SPY_1min_2020-06-03.csv','SPY_1min_2020-06-03.csv')
    i = IntraDay('spy',1)
    i.collectData()
    df = i.loadData()

    fig = plotly.tools.make_subplots(rows=2, cols=1, vertical_spacing=0.2)
    fig['layout']['margin'] = {
        'l': 30, 'r': 10, 'b': 30, 't': 10
    }
    #fig['layout']['legend'] = {'x': 0, 'y': 1, 'xanchor': 'left'}

    fig.append_trace({
        'x': df.index,
        'y': df['1. open'],
        'name': 'Price action'
    }, 1, 1)
    fig.append_trace({
        'x': df.index,
        'y': df['5. volume'],
        'name': 'volume',
        'type': 'bar'
    }, 2, 1)
    return fig




app.run_server(debug=True, port=8055)