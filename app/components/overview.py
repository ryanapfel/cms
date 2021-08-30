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
                    dbc.Col([getGraph(id='demand', figFunction=ratingHistogram(data, 'demand', 'Distribution of Overall Ratings'))], md=6), 
                    dbc.Col([getGraph(id='rating', figFunction=ratingHistogram(data, 'rating', 'Distribution of Overall Ratings'))], md=6), 
                    ]),
                    

                # dbc.Row([
                #     dbc.Col([dcc.Graph(id="platform-prefs", figure=graphPrefs(data, title='Platform Preferences (top 5)'))], md=12)
                # ]),
                #     dbc.Row([
                #     dbc.Col([getTitleComps(data, 'overview-update')], md=12)
                # ]),
                #     dbc.Row([
                #     dbc.Col([dcc.Graph(id='rating-histogram', figure=graphOverviewHisto(data))], md=6),
                #     dbc.Col([getGraph(id='rating-comparisons', figFunction=graphComparison(data, []))], md=6), 
                # ])
                
                        
            ])
    ])))
    
    return component



@dash_figure
def ratingHistogram(data, dataType, title):
    dataName = dataType
    df = parseData(dataName, data)
    mediaItem = getMediaItemId(data)
    itemTitle = getMediaTitle(data)
    currentItem = df[df.media_item_id == mediaItem]
    itemMean = currentItem['mean'].item()
    df = df.loc[: , 'mean']
    allMean = df.mean()
    
    fig = (px.histogram(df, x="mean", title=title)
    .update_layout(title_font_size=24)
    .add_vline(x=itemMean, line_width=4, annotation_text=f'{itemTitle} rating',  annotation_textangle=-90)
    .add_vline(x=allMean, line_width=2, line_color="black", line_dash="dot", annotation_text='Average Rating', annotation_textangle=-90)
    .update_xaxes(title='Rating')
    .update_yaxes(title='Number of Titles'))

    return fig




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
        return card(value=0, title=title)


@dash_figure
def graphPrefs(data, title):
    top = 5
    dataName = 'prefs'
    df = parseData(dataName, data)
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



# there will be a bug for now where its possible the possible options wont line up 
@dash_figure
def graphOverviewHisto(data, comparisonId=[]):
    dataName = 'allRatings'
    titlesDf = parseData('client_titles', data)
    df = parseData(dataName, data)
    mediaItem = getMediaItemId(data)
    itemTitle = getMediaTitle(data)
    

    fig = go.Figure()
    dff = df[df['media_item_id'] == mediaItem] 
    fig.add_trace(go.Histogram(x=dff['overall-rating'], name=itemTitle))

    for item in comparisonId:
        dff = df[df['media_item_id'] == item]
        title = titlesDf[titlesDf['media_item_id'] == item]['title'].item()
        fig.add_trace(go.Histogram(x=dff['overall-rating'],  name=title))

    # Overlay both histograms
    fig.update_layout(barmode='overlay')
    # Reduce opacity to see both histograms
    fig.update_traces(opacity=0.50)

    return fig


@dash_figure
def graphComparison(data, items=[]):

    titlesDf = parseData('client_titles', data)
    rating = parseData('rating', data)
    demand = parseData('demand', data)
    mediaItem = getMediaItemId(data)
    itemTitle = getMediaTitle(data)
    items.append(mediaItem) 
    
    rows = []
    for item in items:
        title = titlesDf[titlesDf['media_item_id'] == item]['title'].item()
        percentile = rating[rating['media_item_id'] == item ]['mean_percentile'].item()
        size = rating[rating['media_item_id'] == item ]['count_rank'].item()
        # TODO:  size should be inverted -- smaller number is actually larger
        rows.append([title, 'rating', percentile , size])
        
        percentile = demand[demand['media_item_id'] == item ]['mean_percentile'].item()
        size = demand[demand['media_item_id'] == item ]['count_rank'].item()
        rows.append([title,'demand', percentile , size])

        
        

    graphDf = pd.DataFrame(rows, columns=['Title','type','Percentile','size'])
    fig = px.scatter(graphDf, y='type', x='Percentile', color='Title', size='size')
    return fig