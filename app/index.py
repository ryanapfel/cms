import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import plotly.express as px
import dash_html_components as html
import flask
import os
import pickle
import pandas as pd
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import numpy as np
from urllib.parse import urlparse, parse_qsl, urlencode
from data import retrieve
from secretVars import *
from components.navbar import buildNavbar, staticNavbar
from components.overview import buildOverview, graphOverviewHisto, graphComparison
from components.demographic import buildDemographic, demoBar
from components.engagement import buildEngagement, addTitleToEngage
from dash.exceptions import PreventUpdate
import plotly.io as pio
import json


pio.templates.default = "ggplot2"

USER = ML_DB_USER
PASS = ML_DB_PASSWORD
PRODUCTION = False
DEBUG = not PRODUCTION 

server = flask.Flask(__name__) # define flask app.server

external_stylesheets = [dbc.themes.BOOTSTRAP, {
    'href': 'https://use.fontawesome.com/releases/v5.8.1/css/all.css',
    'rel': 'stylesheet',
    'integrity': 'sha384-50oBUHEmvpQ+1lW4y57PTFmhCaXp0ML5d60M1M7uH2+nqUivzIebhndOJK28anvf',
    'crossorigin': 'anonymous'
}]

meta_tags = {
            "name": "viewport",
            "content": "width=device-width, initial-scale=1.0"
            }

app = dash.Dash(
    __name__,
    meta_tags=[meta_tags],
    server=server,
    # Include custom stylesheets here
    external_stylesheets=external_stylesheets,
    # Include custom js here
    suppress_callback_exceptions=True
)

DEFAULT_LAYOUT = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='store'),
    html.Div(id='page-layout', children=[
        dbc.Row(
        dbc.Col(
            dbc.Spinner(spinner_style={'color':'primary', "width": "3rem", "height": "3rem"})
            ,width={"size": 6, "offset": 6},
            ))])
])


app.layout = DEFAULT_LAYOUT



def apply_default_value(params):
    def wrapper(func):
        def apply_value(*args, **kwargs):
            if 'id' in kwargs and kwargs['id'] in params:
                kwargs['value'] = params[kwargs['id']]
            return func(*args, **kwargs)
        return apply_value
    return wrapper




def parse_state(url):
    parse_result = urlparse(url)
    params = parse_qsl(parse_result.query)
    state = dict(params)
    return state



@app.callback(Output('store', 'data'),
              Input('url', 'href'))
def getData(href):
    state = parse_state(href)

    # only run expensive data retrieve if the correct url format is passed
    if 'mediaId' in state:
        data = retrieve(state, USER, PASS)
        return data
    
    # return empty data store if mediaId is not in URL
    return {}

@app.callback(Output('page-layout', 'children'),
              Input('store','data'))
def getLayout(data):
    debug = DEBUG
    try:
        layout = [
                buildNavbar(data),
                buildOverview(data),
                buildEngagement(data),
                # buildDemographic(data)
            ]

        return layout
    except Exception as e:
        layout = [
            staticNavbar('Volkno'),
            dbc.Alert(f"{e}", color="danger", is_open=True, duration=5000, fade=True),
        ]
        return layout


    
@app.callback(Output('engagement-graph', 'figure'),
              Input('store','data'),
              Input('engagement-dropdown','value'),
              prevent_initial_call=True)
def engagementCallback(data, value):
    return addTitleToEngage(data, value)

@app.callback(Output('rating-histogram', 'figure'),
              Input('store','data'),
              Input('overview-update','value'),
              prevent_initial_call=True)
def engagementCallback(data, value):
    return graphOverviewHisto(data, value)


@app.callback(Output('rating-comparisons', 'figure'),
              Input('store','data'),
              Input('overview-update','value'),
              prevent_initial_call=True)
def engagementCallback(data, value):
    return graphComparison(data, value)






@app.callback(Output('demo-eth-bar', 'figure'),
              Input('store','data'),
              Input('demographic-dropdown','value'),
              prevent_initial_call=True)
def engagementCallback(data, value):
    return demoBar(data, value, 'ethnicity')

    



if __name__ == "__main__":
    if PRODUCTION:
        app.run_server(debug=True)
    else:
        app.run_server(debug=True, host='0.0.0.0', port=8050)
