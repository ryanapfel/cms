
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import plotly.graph_objects as go

import pandas as pd

def parseData(dataName, data):
    if dataName in data:
        df = pd.read_json(data[dataName])
    else:
        df = pd.DataFrame()
    return df

def getMediaItemId(data):
    df = parseData('title', data)
    if df.empty:
        return ''
    else:
        return df['media_item_id'].item()



def getMediaTitle(data):
    df = parseData('title', data)
    if df.empty:
        return ''
    else:
        return df['title'].item()

def alert(message, color='warning'):
    return dbc.Alert(message, color=color, is_open=True, duration=4000, fade=True)


def blankFig(message):
    fig = go.Figure().add_annotation(x=2, y=2,text=message,
                                        font=dict(family="sans serif",size=25,color="crimson"),showarrow=False,yshift=10)
    return fig


def card(**args):
    value = args['value']
    title = args['title']
    icon = 'fas fa-shield-alt fa-2x'
    
    cardBody = dbc.Card( dbc.CardBody( [
        dbc.Row([
        dbc.Col([
        html.P(
            title,
            className="card-text",
        ),
        html.H2(f'{round(value, 2)}', className="card-title"),

        ], md=9),

            dbc.Col([
        html.I(className=icon),

        ], md=3),
    ], align='center')]
    ))

    return cardBody
