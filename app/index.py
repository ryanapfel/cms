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
from components.navbar import buildNavbar, staticNavbar, clientDropdown, updateClientOptions
from components.overview import *
from components.demographic import buildDemographic, demoBar
from components.engagement import buildEngagement, addTitleToEngage
from dash.exceptions import PreventUpdate
import plotly.io as pio
import dash_table
import json


pio.templates.default = "ggplot2"

USER = ML_DB_USER
PASS = ML_DB_PASSWORD
PRODUCTION = False
DEBUG = not PRODUCTION 

server = flask.Flask(__name__) # define flask app.server

external_stylesheets = [{
    'href': 'https://use.fontawesome.com/releases/v5.8.1/css/all.css',
    'rel': 'stylesheet',
    'integrity': 'sha384-50oBUHEmvpQ+1lW4y57PTFmhCaXp0ML5d60M1M7uH2+nqUivzIebhndOJK28anvf',
    'crossorigin': 'anonymous'
}]

meta_tags = {
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


SPINNER = dbc.Row(
        dbc.Col(
            dbc.Spinner(spinner_style={'color':'primary', "width": "3rem", "height": "3rem"})
            ,width={"size": 6, "offset": 6},
        ))



DEFAULT_LAYOUT = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='store'),
    dcc.Store(id='loadStore'),
    dcc.Store(id='loadingState'),
    html.Div(id='content', children=[
        staticNavbar('Volkno' ),
        html.Div(id='loading', style={'display':'block'}, children=SPINNER),
        html.Div(id='page-layout')
    ])
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





@app.callback(Output('loadStore', 'data'),
              Input('url', 'href'),
              Input('client-dropdown','value'))
def getLoadData(url, dropvalue):
    state = parse_state(url)
    state['dropdown'] = dropvalue
    state['loading'] = True
    return state

@app.callback(Output('store', 'data'),
              Output('client-dropdown', 'options'),
              Input('loadStore', 'data'))
def getData(loadingState):
    try:

        
        mId = int(loadingState['mediaId'])
        dropdown = int(loadingState['dropdown'])
        initialClient = int(loadingState['clientId'])
        options = updateClientOptions(initialClient)
        return retrieve(mId, dropdown, USER, PASS), options
    except:
    # return empty data store if mediaId is not in URL
        return {}, []




@app.callback(Output('page-layout', 'children'),
              Output('loading', 'style'),
              Input('store','data'))
def getLayout(data):
    debug = DEBUG
    loading = {'display':'none'}
    try:
        layout = [
                buildOverview(data),
                # buildEngagement(data),
                # buildDemographic(data)
            ]

        return layout, loading
    except Exception as e:
        layout = [
            staticNavbar('Volkno'),
            dbc.Alert(f"{e}", color="danger", is_open=True, duration=5000, fade=True),
        ]
        return layout, loading


    
@app.callback(Output('engagement-graph', 'figure'),
              Input('store','data'),
              Input('engagement-dropdown','value'),
              prevent_initial_call=True)
def engagementCallback(data, value):
    return addTitleToEngage(data, value)

@app.callback(Output('rating-histogram', 'figure'),
              Input('store','data'),
              Input('overview-update','value'))
def engagementCallback(data, value):
    return graphOverviewHisto(data, value)


@app.callback(Output('rating-comparisons', 'figure'),
              Input('store','data'),
              Input('overview-update','value'),
              prevent_initial_call=True)
def engagementCallback(data, value):
    return graphComparison(data, value)



@app.callback(Output('data-table','children'),
              Output('ethnicity-comparable-rating', 'figure'),
              Input('store','data'),
              Input('rating-histogram','selectedData'))
            #   Input('overview-update','value'))
def returnDataTOtable(data, select):
    try:
        minR = select['range']['x'][0]
        maxR = select['range']['x'][1] 
        return json.dumps([select['range']]),  demoFiltrtedComps(data, minR, maxR)
    except Exception as e:
        return {}, demoFiltrtedComps(data, 0, 10)






@app.callback(Output('demo-eth-bar', 'figure'),
              Input('store','data'),
              Input('demographic-dropdown','value'),
              prevent_initial_call=True)
def engagementCallback(data, value):
    return demoBar(data, value, 'ethnicity')

    



if __name__ == "__main__":
    if PRODUCTION:
        app.run_server(debug=False)
    else:
        app.run_server(debug=True, host='0.0.0.0', port=8050)
