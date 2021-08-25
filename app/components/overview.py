import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import plotly.express as px 
import pandas as pd
from  components.utils import *

def buildOverview(data):

    component = dbc.Row(dbc.Col(dbc.Card([
        dbc.CardHeader(html.H5("Overview")),
            dbc.CardBody([
                dbc.Row(
                    [
                    dbc.Col([dbc.Col(overviewCard(data, 'demand', 'demand','Demand Average'))], md=4), 
                    dbc.Col([dbc.Col(overviewCard(data, 'rating', 'rating','Overall Rating Average'))], md=4), 
                    dbc.Col([dbc.Col(overviewCard(data, 'rating', 'count','Count of Ratings'))], md=4), 
                    ], align='center'
                ),
                dbc.Row(
                    [
                    dbc.Col([dcc.Graph(id="demand", figure=ratingHistogram(data, 'demand', 'Distribution of Demand Ratings'))], md=6), 
                    dbc.Col([dcc.Graph(id="rating", figure=ratingHistogram(data, 'rating', 'Distribution of Overall Ratings'))], md=6), 
                    ], 
                    ),

                dbc.Row([
                    dbc.Col([dcc.Graph(id="platform-prefs", figure=graphPrefs(data, title='Platform Preferences (top 5)'))], md=12)
                ])
            ])
    ])))
    
    return component




def ratingHistogram(data, dataType, title):
    dataName = dataType
    df = parseData(dataName, data)

    try:
        mediaItem = getMediaItemId(data)
        itemTitle = getMediaTitle(data)
        currentItem = df[df.media_item_id == mediaItem]
        itemMean = currentItem['mean'].item()
        df = df.loc[: , 'mean']
        allMean = df.mean()
        
        fig = (px.histogram(df, x="mean", title=title)
        .update_layout(title_font_size=24)
        .add_vline(x=itemMean, line_width=4, line_color="red", annotation_text=f'{itemTitle} rating',  annotation_textangle=-90)
        .add_vline(x=allMean, line_width=2, line_color="black", line_dash="dot", annotation_text='Average Rating', annotation_textangle=-90)
        .update_xaxes(title='Rating')
        .update_yaxes(title='Number of Titles'))

        return fig
    except:
        return blankFig('No data for {dataType} figure')



def overviewCard(data, dataName, cardType ,title):
    df = parseData(dataName, data)    
    try:
        mediaItem = getMediaItemId(data)
        df = df[df.media_item_id == mediaItem]

        mean = df['mean'].item()
        std = df['std'].item()
        count = df['count'].item()

        if cardType == 'demand' or cardType == 'rating':
            value = mean
        elif cardType == 'count':
            value = count
        
        return card(value=value, title=title)
    
    except:
        print('Overview Card Exception')
        return card(value=0, title=title)



def graphPrefs(data, title):
    top = 5
    dataName = 'prefs'
    df = parseData(dataName, data)
    try:
        df = df.iloc[:top].reset_index()
        fig = (px.bar(df, y='platform', x='count', orientation='h')
        .update_layout(barmode='stack',  yaxis_categoryorder='total ascending',title=title))
        fig.update_layout({'xaxis': {'title': 'Votes',
                            'visible': True,
                            'showticklabels': True},
                            'yaxis': {'title': '',
                                        'visible': True,
                                        'showticklabels': True}})
    
                                
        return fig
    except:
        return blankFig('No data for this figure')



