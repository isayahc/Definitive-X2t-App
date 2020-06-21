import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly
from app.Cloud import Cloud
import pandas as pd
from app.Frequency import IntraDay
from flask import Flask


external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
c = Cloud()
x = c.get_s3_keys()
server = app.server

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

index_page = html.Div([
    html.H1("Welcome to the Page"),
    html.H2('XayTech-Gold'),
    dcc.Link('Today data', href='/today'),
    html.Br(),
    dcc.Link('Go to Historial data', href='/historial'),
])

page_1_layout = html.Div([
    html.H1('Today'),
    html.Div(id='page-1-content'),
    html.Br(),
    dcc.Link('Go to Historical', href='/historial'),
    html.Br(),
    dcc.Link('Go back to home', href='/'),
    html.H4('Something'),
    html.Div(id='live-update-text'),
    dcc.Graph(
        id='live-update-graph'
        ),
    dcc.Interval(
        id='interval-component',
        interval= 60*1000, #in milliseconds
        n_intervals=0

    )
])

page_2_layout = html.Div([
    html.H1('Historical'),
    html.Div(id='page-2-content'),
    html.Br(),
    dcc.Link('Go to Today', href='/today'),
    html.Br(),
    dcc.Link('Go back to home', href='/'),
    html.Div(id='historical-page'),
    dcc.Dropdown(
        id='drop-down-data',
            options=[ {'label': i, 'value': i}  for i in x ],
            value= x[-1],

    ),
    dcc.Graph(id='static-graph'),

])

@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/today':
        return page_1_layout
    elif pathname == '/historial':
        return page_2_layout
    else:
        return index_page
    # You could also return a 404 "URL not found" page here

@app.callback(Output('live-update-graph','figure'),
[Input('interval-component', 'n_intervals')])
def update_graph_live(n):
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

@app.callback(dash.dependencies.Output('historical-page', 'children'),
              [dash.dependencies.Input('drop-down-data', 'value')])
def page_2_radios(value):
    return 'You have selected "{}"'.format(value)


@app.callback(dash.dependencies.Output('static-graph', 'figure'),
              [dash.dependencies.Input('drop-down-data', 'value')])
def page_2_radios(value):
    try:
        df =pd.read_csv(value, index_col='date')
    except FileNotFoundError:
        c = Cloud()
        c.downloadData(value,value)
        df = pd.read_csv(value, index_col='date')
        
    fig = plotly.tools.make_subplots(rows=2, cols=1, vertical_spacing=0.2)
    fig['layout']['margin'] = {
            'l': 30, 'r': 10, 'b': 30, 't': 10
    }

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

@app.callback(Output('live-update-text', 'children'),
[Input('interval-component', 'n_intervals')]
)
def update_metrics(n):
    
    i = IntraDay('spy',1)
    df = i.loadData()
    
    mean = df['1. open'].mean()
    low = df['1. open'].min()
    maxx = df['1. open'].max()
    volume_mean = df['5. volume'].mean()
    volume_low = df['5. volume'].min()
    volume_maxx = df['5. volume'].max()
    x = lambda x : f'{(x/1000):.2f}k'
    style = {'padding': '5px', 'fontSize': '16px'}
    return[
        html.Span(f'Mean: {mean}', style=style),
        html.Span(f'Low: {low}', style=style),
        html.Span(f'Max: {maxx}', style=style),
        html.Span(f'Volume Data: ', style=style),
        html.Span(f'Mean: {x(volume_mean)}', style=style),
        html.Span(f'Low: {volume_low}', style=style),
        html.Span(f'Max: {x(volume_maxx)}', style=style)
    ]


if __name__ == '__main__':
    app.run_server(debug=True)