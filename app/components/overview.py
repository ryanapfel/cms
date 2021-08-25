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
                    dbc.Col([dbc.Col(demandCard(data))], md=4), 
                    dbc.Col([dbc.Col(ratingCard(data))], md=4), 
                    dbc.Col([dbc.Col(countCard(data))], md=4), 
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

    if df.empty:
        return blankFig('No data for this figure')

    mediaItem = getMediaItemId(data)
    itemTitle = getMediaTitle(data)
    currentItem = df[df.media_item_id == mediaItem]
    itemMean = currentItem['mean'].item()
    df = df.loc[: , 'mean']
    allMean = df.mean()
    
    fig = (px.histogram(df, x="mean", nbins=30, title=title)
    .update_layout(title_font_size=24)
    .add_vline(x=itemMean, line_width=4, line_color="red", annotation_text=f'{itemTitle} rating',  annotation_textangle=-90)
    .add_vline(x=allMean, line_width=2, line_color="black", line_dash="dot", annotation_text='Average Rating', annotation_textangle=-90)
    .update_xaxes(title='Rating')
    .update_yaxes(title='Number of Titles'))

    return fig




# def buildRating(data):

def demandCard(data):
    dataName = 'demand'
    df = parseData(dataName, data)
    if df.empty:
        return card(value=0, title='Average Demand')

    mediaItem = getMediaItemId(data)

    df = df[df.media_item_id == mediaItem]

    mean = df['mean'].item()
    std = df['std'].item()
    count = df['count'].item()

    return card(value=mean, title='Average Demand')

def card(**args):
    value = args['value']
    title = args['title']
    
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
        html.I(className="fas fa-shield-alt fa-2x"),

        ], md=3),
    ], align='center')]
    ))

    return cardBody


def ratingCard(data):
    dataName = 'rating'
    df = parseData(dataName, data)
    if df.empty:
        return card(value=0, title='Average Rating')
    
    mediaItem = getMediaItemId(data)
    
    df = df[df.media_item_id == mediaItem]
    mean = df['mean'].item()
    std = df['std'].item()
    count = df['count'].item()

    return card(value=mean, title='Average Rating')

def countCard(data):
    dataName = 'rating'
    df = parseData(dataName, data)
    if df.empty:
        return card(value=0, title='Total  Ratings')

    mediaItem = getMediaItemId(data)
    
    df = df[df.media_item_id == mediaItem]
    mean = df['mean'].item()
    std = df['std'].item()
    count = df['count'].item()

    return card(value=count, title='Total Ratings')


def graphPrefs(data, title):
    top = 5
    dataName = 'prefs'
    df = parseData(dataName, data)

    if df.empty:
        return blankFig('No data for this figure')

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



