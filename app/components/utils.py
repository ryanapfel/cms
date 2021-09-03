
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


def displayValue(**args):
    value = args['value']
    title = args['title']
    icon = 'fas fa-shield-alt fa-2x'
    
    component = html.Div([
            dbc.Row(html.P(title)),
            dbc.Row(html.H3(round(value, 2)))
        ], className='p-3')

    return component

def getTitleComps(data, componentId, mediaItems=[]):   
    df = parseData('client_titles', data)
    itemms = mediaItems if mediaItems else list(df['media_item_id'].unique())
    dff = df[df['media_item_id'].isin(itemms)][['title', 'media_item_id']]
    dff.rename(columns={'title':'label', 'media_item_id':'value'}, inplace=True)
    options = dff.to_dict(orient='records')

    component = dcc.Dropdown(
        id=componentId,
        options=options,
        value=[],
        multi=True
    )
    return component

# def getTitleComps(data, componentId, mediaItems=[]):
#     try:
#         df = parseData('client_titles', data)
#         itemms = mediaItems if mediaItems else df['media_item_id'].unique() 
#         dff = df[df['media_item_id'].isin(itemms)][['title', 'media_item_id']]
#         dff.rename(columns={'title':'label', 'media_item_id':'value'}, inplace=True)
#         options = dff.to_dict(orient='records')
            
#         component = dcc.Dropdown(
#             id=componentId,
#             options=titles,
#             value=[],
#             multi=True
#         )
#         return component
#     except Exception as e:
#         return html.P(str(e))
    

def getConfig():
    return {
			'displayModeBar':False,
			'queueLength':0
    }


def getGraph(id, figFunction):
    return dcc.Graph(id=id, config={'displayModeBar':False,'queueLength':0}, figure=figFunction)

def getGraphCard(graphId, graphFunction, title='', tooltip=''):
    comp = dbc.Card([dbc.CardBody([dbc.Row(dbc.Col(html.H6(title))),
                                    dbc.Row(dbc.Col(getGraph(id=graphId, figFunction=graphFunction)))
                                   ])
                    ])
                                    
    return comp



def dash_figure(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return blankFig(f'{func.__name__} : {e}')
            ## ADD LOGGER
    return wrapper 


def data_component(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return dcc.Div(hml.P(f'{e}'))
            ## ADD LOGGER
    return wrapper 


