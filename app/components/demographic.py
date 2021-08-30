import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import plotly.express as px 
import pandas as pd
from  components.utils import *

demoCodes = {"ethnicity": {"L":"Hispanic", "B":"Black","W":"White","A":"Asian","O":"Other", "N":"Native American"} }

def buildDemographic(data):
    component = dbc.Row(dbc.Col(dbc.Card([
        dbc.CardHeader(html.H5("Demographics")),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.H4('Ethnicity'),
                        html.P('Select titles to compare'),
                        getTitleComps(data, "demographic-dropdown")
                    ], width='3')
                ]),
                dbc.Row([dbc.Col([
                    dcc.Graph(id="demo-eth-pie", figure=demoPie(data, 'ethnicity'))
                    ], align='start', width='3'),
                dbc.Col([
                    dcc.Graph(id="demo-eth-bar", figure=demoBar(data, [] ,'ethnicity'))
                    ], width='9')
                ]),                   
            ])
    ])))
    
    return component





def convertDemoCodes(convertList, demoKey, refrence):
    try:
        newList = []
        subdict = refrence[demoKey]
        for code in convertList:
            if code in subdict:
                newList.append(subdict[code])
            else:
                newList.append(code)
        return newList
    except OSError as err:
        return convertList
    

def blankPie():
    return go.Figure(go.Pie(labels=['N/A'], values=[1], textinfo='label', textposition='inside'), layout={'showlegend':False})

def demoPie(data, key, **args):
    dataName = 'demographics'
    df = parseData(dataName, data)
    mediaItem = getMediaItemId(data)
    try:
        dff = df[(df['media_item_id'] == mediaItem) & (df['demographic_key'] == key)]
        
        labels = convertDemoCodes(dff['demographic_value'].to_list(), key, demoCodes)
        values = dff['count'].to_list()
        
        common_props = dict(labels=labels, values=values)
        
        trace1 = go.Pie(
        **common_props,
        textinfo='percent',
        textposition='outside')

        trace2 = go.Pie(
        **common_props,
        textinfo='label',
        textposition='inside')
        return go.Figure(data=[trace1, trace2], layout={'showlegend':False})
    except:
        return blankPie()

def demoBar(data, otherMediaItems, key, **args):
    dataName = 'demographics'
    df = parseData(dataName, data)
    mediaItem = getMediaItemId(data)
    itemTitle = getMediaTitle(data)
    titlesDf = parseData('client_titles', data)
    try:
        dff = df[(df['media_item_id'] == mediaItem) & (df['demographic_key'] == key)]
        values = dff['mean'].to_list()
        labels = convertDemoCodes(dff['demographic_value'].to_list(), key, demoCodes)
        std = dff['std'].to_list()
        figdata=[go.Bar(name=itemTitle, x=labels, y=values, error_y=dict(type='data', array=std) )]
        
        for idx, items in enumerate(otherMediaItems):
            dff = df[(df['media_item_id'] == items) & (df['demographic_key'] == key)]
            values = dff['mean'].to_list()
            std = dff['std'].to_list()
            title = titlesDf[titlesDf['media_item_id'] == items]['title'].item()
            figdata.append(go.Bar(name=f'{title}', x=labels, y=values, error_y=dict(type='data', array=std) ))
            
        
        fig = go.Figure(data=figdata)
        fig.update_layout(barmode='group', 
                        title=f'Rating by {key.capitalize()}', 
                        yaxis_title="Rating",
                        xaxis_title=f"{key.capitalize()}",
                        **args)
        return fig

    except Exception as e:
        return blankFig(f'{e}')

