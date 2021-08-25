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
from components.overview import buildOverview
from components.engagement import buildEngagement, addTitleToEngage
import json

USER = ML_DB_USER
PASS = ML_DB_PASSWORD
DEBUG = True

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
    if not href:
        return {}
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
    if 'exists' in data and data['exists']:
        layout = [
            buildNavbar(data),
            buildOverview(data),
            buildEngagement(data)
        ]
    elif 'exists' in data and not data['exists']:
        layout = [
            staticNavbar('Volkno'),
            dbc.Alert("Media Item doesn't exists in our records", color="warning", is_open=True, duration=4000, fade=True),
        ]
    else:
        layout = [
            staticNavbar('Volkno'),
            dbc.Alert("URL format is invalid", color="danger", is_open=True, duration=3000, fade=True),
        ]
    if debug:
        layout.append(html.Pre(json.dumps(data, indent=4)))
    return layout

    
@app.callback(Output('engagement-graph', 'figure'),
              Input('store','data'),
              Input('engagement-dropdown','value'),
              prevent_initial_call=True)
def engagementCallback(data, value):
    return addTitleToEngage(data, value)


if __name__ == "__main__":
    app.run_server(debug=True, host='0.0.0.0', port=8050)




            # apply_default_value(params)(dcc.Dropdown)(
        #     id='dropdown',
        #     options=[{'label': i, 'value': i} for i in ['LA', 'NYC', 'MTL']],
        #     value='LA'
        # ),
        # apply_default_value(params)(dcc.Input)(
        #     id='input',
        #     placeholder='Enter a value...',
        #     value=''
        # ),