import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import plotly.express as px 
import pandas as pd
from  components.utils import *

def buildEngagement(data):
    component = dbc.Row(dbc.Col(dbc.Card([
        dbc.CardHeader(html.H5("Engagement")),
            dbc.CardBody([
                dbc.Row([dbc.Col([
                    html.P('Select Titles to Compare'),
                    getTitleComps(data, 'engagement-dropdown')
                    ], align='end', width='3')]),
                dbc.Row([
                    dbc.Col([dcc.Graph(id="engagement-graph", figure=plotEngagement(data))], md=12)
                ])
            ])
    ])))
    
    return component

    
def plotEngagement(data, returnDf = False):
    dataName = 'client_engagment'
    df = parseData(dataName, data)
    mediaItem = getMediaItemId(data)
    itemTitle = getMediaTitle(data)
    if df.empty or mediaItem == '' or itemTitle == '':
        if returnDf:
            return pd.DataFrame(), blankFig('No Engagement Data')
        else:
            return blankFig('No Engagement Data')

    fig = go.Figure()
    
    # dff = df.groupby('percentile').mean().reset_index()[['percentile', 'count','normalized']]
    # fig.add_trace(go.Scatter(x=dff['percentile'],
    #                          y=dff['normalized'], 
    #                          name='Average', 
    #                          mode='lines', line={'dash': 'dash', 'color':'black'}))
    
    dff = df[df['media_item_id'] == mediaItem]
    fig.add_trace(go.Scatter(x=dff['percentile'], 
                             y=dff['normalized'].interpolate(), 
                             name=f'{itemTitle}', 
                             mode='lines',
                             line={'width':3}))

    if returnDf:
        return df, fig

    return fig

def addTitleToEngage(data, mediaIdToAdd):
    df, fig = plotEngagement(data, returnDf=True)
    titlesDf = parseData('client_titles', data)
    if df.empty or titlesDf.empty:
        return fig
    
    for items in mediaIdToAdd:
        dff = df[df['media_item_id'] == items]
        title = titlesDf[titlesDf['media_item_id'] == items]['title'].item()
        fig.add_trace(go.Scatter(x=dff['percentile'], 
                                 y=dff['normalized'].interpolate(), 
                                 name=f'{title}',
                                 mode='lines',
                                 line={'width':2, 'dash':'solid'}))

    return fig


