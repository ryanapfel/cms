import dash
import dash_html_components as html
import flask
import os
import pickle
import pandas as pd
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import numpy as np
from urllib.parse import urlparse, parse_qsl, urlencode, quote_plus
from data import retrieve, Engine
from secretVars import ML_DB_USER, ML_DB_PASSWORD, ML_DB_HOST, ML_DB_DB
from components.navbar import (
    buildNavbar,
    staticNavbar,
    clientDropdown,
    updateClientOptions,
)
from components.overview import *
from components.engagement import *
from components.contained import TitleDropdowns
from components.ratings import *
from components.utils import getDummy
from dash.exceptions import PreventUpdate
from components.template import template


template()


PRODUCTION = False
DEBUG = not PRODUCTION

COMPONENT = "engagement"

server = flask.Flask(__name__)  # define flask app.server

external_stylesheets = [
    {
        "href": "https://use.fontawesome.com/releases/v5.8.1/css/all.css",
        "rel": "stylesheet",
        "integrity": "sha384-50oBUHEmvpQ+1lW4y57PTFmhCaXp0ML5d60M1M7uH2+nqUivzIebhndOJK28anvf",
        "crossorigin": "anonymous",
    }
]

meta_tags = {}

app = dash.Dash(
    __name__,
    meta_tags=[meta_tags],
    server=server,
    # Include custom stylesheets here
    external_stylesheets=external_stylesheets,
    # Include custom js here
    suppress_callback_exceptions=True,
)


SPINNER = dbc.Row(
    dbc.Col(
        dbc.Spinner(
            spinner_style={"color": "primary", "width": "3rem", "height": "3rem"}
        ),
        width={"size": 6, "offset": 6},
    )
)


DEFAULT_LAYOUT = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        dcc.Store(id="store"),
        dcc.Store(id="loadStore"),
        dcc.Store(id="loadingState"),
        html.Div(
            id="content",
            children=[
                html.Div(id="loading", style={"display": "block"}, children=SPINNER),
                html.Div(id="page-layout"),
            ],
        ),
    ]
)


app.layout = DEFAULT_LAYOUT


def apply_default_value(params):
    def wrapper(func):
        def apply_value(*args, **kwargs):
            if "id" in kwargs and kwargs["id"] in params:
                kwargs["value"] = params[kwargs["id"]]
            return func(*args, **kwargs)

        return apply_value

    return wrapper


def parse_state(url):
    parse_result = urlparse(url)
    params = parse_qsl(parse_result.query)
    state = dict(params)
    return state


@app.callback(Output("loadStore", "data"), Input("url", "href"))
def getLoadData(url):
    state = parse_state(url)
    if "view" not in state:
        state["view"] = "other"

    return state


@app.callback(
    Output("store", "data"),
    Input("loadStore", "data"),
)
def getData(loadingState):
    mediaId = int(loadingState["mediaId"])
    client = int(loadingState["clientId"])
    view = loadingState["view"]
    returnDict = {}

    password = quote_plus(ML_DB_PASSWORD)
    queryString = f"mysql+pymysql://{ML_DB_USER}:{password}@{ML_DB_HOST}/{ML_DB_DB}"

    engine = Engine(mediaId, client, queryString)
    # get title
    returnDict["mediaId"] = mediaId
    returnDict["client"] = client
    returnDict["title"] = engine.getTitle()

    if view == "overview":
        returnDict["rating"] = engine.getRating()
        returnDict["demand"] = engine.getDemand()
        returnDict["prefrences"] = engine.getPreferences()

    if view == "rating":
        returnDict["all_ratings"] = engine.getAllRatings()
        returnDict["client_titles"] = engine.getClientComps(100)
        returnDict["rating"] = engine.getRating()
        returnDict["demand"] = engine.getDemand()

    if view == "engagement":
        returnDict["client_engagment"] = engine.getEngagement()
        returnDict["client_titles"] = engine.getClientComps(250)
        # returnDict["scenes"] = engine.getScenes()
        returnDict["video_info"] = engine.getVideoInfo()
        returnDict["mediaRawEngagement"] = engine.getRawEngagement()

    # returnDict['exists'] = engine.mediaItemExists()

    # returnDict['client_titles'] = engine.getClientComps()
    # returnDict['client_engagment'] = engine.getEngagement()
    # returnDict['demographics'] = engine.getDemographics()

    return returnDict


@app.callback(
    Output("page-layout", "children"),
    Output("loading", "style"),
    Input("store", "data"),
    Input("loadStore", "data"),
)
def getLayout(data, params):
    debug = DEBUG
    loading = {"display": "none"}
    view = params["view"]

    if view == "overview":
        layout = [Overview(data, params)]

    elif view == "rating":
        layout = [Rating(data, params)]

    elif view == "engagement":
        layout = [Engagement(data, params)]
    elif view == "test":
        layout = [getDummy()]
    else:
        layout = [html.H1("Nothing to See")]

    return layout, loading


@app.callback(
    Output("engagement-graph", "figure"),
    Input("store", "data"),
    Input("engagement-dropdown", "value"),
    prevent_initial_call=True,
)
def engagementCallback(data, value):
    return addTitleToEngage(data, value)


@app.callback(
    Output("ratings-allhistogram", "figure"),
    Input("store", "data"),
    Input("rating-update", "value"),
    Input("loadStore", "data"),
)
def engagementCallback(data, others, params):
    histo = AllRatingHistogram(globalParams=params, other=others)
    histo.load(data)
    histo.transform()
    return histo.display(returnFig=True)


@app.callback(
    Output("engagement-percentile", "figure"),
    Input("engage-update", "value"),
    Input("loadStore", "data"),
    Input("store", "data"),
)
def eggGraph(others, params, data):
    g = EngagementGraph(globalParams=params, other=others)
    g.load(data)
    g.transform()
    return g.display(returnFig=True)


@app.callback(
    Output("ratings-percentile", "figure"),
    Input("store", "data"),
    Input("rating-update", "value"),
    Input("loadStore", "data"),
)
def engagementCallback(data, others, params):
    histo = RatingPercentiles(globalParams=params, other=others)
    histo.load(data)
    histo.transform()
    return histo.display(returnFig=True)


@app.callback(
    Output("ratings-demo-ethnicity", "figure"),
    Output("ratings-demo-sex", "figure"),
    Output("ratings-demo-income", "figure"),
    Input("store", "data"),
    Input("ratings-allhistogram", "selectedData"),
    Input("rating-update", "value"),
    Input("loadStore", "data"),
    prevent_initial_call=True,
)
def returnDataTOtable(data, select, other, params):
    rRange = {}
    if select is not None and "range" in select:
        rRange["min"] = select["range"]["x"][0]
        rRange["max"] = select["range"]["x"][1]
    else:
        rRange["min"] = 0
        rRange["max"] = 10
    demo = DemoComparisons(globalParams=params, other=other, ratingRange=rRange)
    demo.load(data)
    demo.transform()
    eth = demo.display(key="ethnicity", returnFig=True)
    sex = demo.display(key="sex", returnFig=True)
    income = demo.display(key="income", returnFig=True)
    return eth, sex, income


@app.callback(
    Output("engagement-vid", "children"),
    Input("store", "data"),
    Input("engagement-percentile", "selectedData"),
    Input("loadStore", "data"),
    prevent_initial_call=True,
)
def videoUpdate(data, select, params):
    rRange = {}
    if select is not None and "range" in select:
        rRange["min"] = select["range"]["x"][0]
        rRange["max"] = select["range"]["x"][1]
    else:
        rRange["min"] = 0
        rRange["max"] = 100

    vid = Video(globalParams=params, vidRange=rRange)
    return vid.show(data)


@app.callback(
    Output("engagement-emotions-wrapper", "children"),
    Input("store", "data"),
    Input("engagement-percentile", "selectedData"),
    Input("loadStore", "data"),
    Input("engagement-drop", "value"),
    prevent_initial_call=True,
)
def videoUpdate(data, select, params, key):
    rRange = {}
    if select is not None and "range" in select:
        rRange["min"] = select["range"]["x"][0]
        rRange["max"] = select["range"]["x"][1]
    else:
        rRange["min"] = 0
        rRange["max"] = 100

    graph = EmotionGraph(globalParams=params, key=key, vidRange=rRange)
    return graph.show(data)


@app.callback(
    Output("demo-eth-bar", "figure"),
    Input("store", "data"),
    Input("demographic-dropdown", "value"),
    prevent_initial_call=True,
)
def engagementCallback(data, value):
    return demoBar(data, value, "ethnicity")


if __name__ == "__main__":
    if PRODUCTION:
        app.run_server(debug=False)
    else:
        app.run_server(debug=True, host="0.0.0.0", port=8050)
