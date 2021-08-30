
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
                                        font=dict(size=10,color="red"),showarrow=False,yshift=10)
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

def getTitleComps(data, componentId):
    df = parseData('client_titles', data)
    titles = []
    if not df.empty:
        for idx, row in df.iterrows():
            tDict = {}
            t = row['title']
            i = row['media_item_id']
            tDict['label'] = f'{t} ({i})'
            tDict['value'] = i
            titles.append(tDict)
    
    component = dcc.Dropdown(
        id=componentId,
        options=titles,
        value=[],
        multi=True
    )
    return component
    

def getConfig():
    return {
			'displayModeBar':False,
			'queueLength':0
    }


def getGraph(id, figFunction):
    return dcc.Graph(id=id, config={'displayModeBar':False,'queueLength':0}, figure=figFunction)



def dash_figure(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return blankFig(f'{func.__name__} : {e}')
            ## ADD LOGGER
    return wrapper 

