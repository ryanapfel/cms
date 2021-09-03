import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import plotly.express as px 
import pandas as pd
import dash_table
from  components.utils import *


@data_component
def header(title):
    comp = dbc.Row(dbc.Col(html.H4(f'{title} Overview')))
    return comp


@data_component
def secondHeader(data, title):
    mediaIds = list(parseData('allRatings', data)['media_item_id'].unique())
    
    comp = dbc.Row([
        dbc.Col(html.H4(f'{title} Rating Comparables')),
        dbc.Col(getTitleComps(data, 'overview-update', mediaItems=mediaIds), md=3)
        ], className='p-4')
    return comp
    
def overview(data):
    card = dbc.Card([
                    dbc.CardBody([
                    dbc.Row(dbc.Col(overviewCard(data, 'demand', 'demand','Demand Average'))),
                    dbc.Row(dbc.Col(overviewCard(data, 'rating', 'rating','Overall Rating Average'))),
                    dbc.Row(dbc.Col(overviewCard(data, 'rating', 'count','Count of Ratings'))) 
                    ], className='p-3'),
                    
                    ])
    return card






def buildOverview(data):
    title = getMediaTitle(data)

    component = html.Div([
        header(title),
    
        dbc.Row([
            dbc.Col(overview(data), md=2),
            dbc.Col(getGraphCard(graphId='demand', 
                                graphFunction= ratingHistogram(data, 'demand', ''), 
                                title='Distribution of Demand'
                                ) ,md=5) ,           
            dbc.Col(getGraphCard(graphId='rating', 
                                graphFunction= ratingHistogram(data, 'rating', ''), 
                                title='Distribution of Ratings'
                                ) ,md=5)
        ]),
        secondHeader(data, title),
        dbc.Row([
                dbc.Col(getGraphCard(graphId='rating-histogram', 
                                    graphFunction=graphOverviewHisto(data, []),
                                    title=f'Distribution Of {title} Ratings'), md=6),
                dbc.Col(getGraphCard(graphId='rating-comparisons', 
                                    graphFunction=graphComparison(data, []),
                                    title='Rating Percentile'), md=6)
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                html.H5('Demographic Breakdonwn'),
                html.Pre(id='data-table', children=[]),
                dcc.Graph(id='ethnicity-comparable-rating')
                ])
            ])
        ])


        
                                
             
        
                #     dbc.Col([getGraph(id='rating', figFunction=ratingHistogram(data, 'rating', 'Distribution of Overall Ratings'))], md=6), 
                    

                # # dbc.Row([
                # #     dbc.Col([dcc.Graph(id="platform-prefs", figure=graphPrefs(data, title='Platform Preferences (top 5)'))], md=12)
                # # ]),
                #     dbc.Row([
                # ]),
                #     
        ], className='p-3')
 
    return component


@dash_figure
def demoFiltrtedComps(data, minRating, maxRating):
    dataName = 'allRatings'
    titlesDf = parseData('client_titles', data)
    df = parseData(dataName, data)
    mediaItem = getMediaItemId(data)
    itemTitle = getMediaTitle(data)

    dff = df[(df['overall-rating'] > minRating) & (df['overall-rating'] < maxRating)]

    fig = go.Figure()

    key='ethnicity'

    vals = dff[dff['media_item_id'] == mediaItem][key].value_counts()
    fig.add_trace(go.Bar(name=itemTitle, x=vals.index, y=vals.values))

    # for item in titles:
    #     vals = dff[dff['media_item_id'] == item][key].value_counts(normalize=True)
    #     title = titlesDf[titlesDf['media_item_id'] == item]['title'].item()
    #     fig.add_trace(go.Bar(name=title, x=vals.index, y=vals.values))
    
    return fig 

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

        return displayValue(value=value, title=title)
    
    except:
        return displayValue(value=0, title=title)


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
    fig.add_trace(go.Histogram(x=dff['overall-rating'],customdata=dff['user_id'],  name=itemTitle, nbinsx=40))

    for item in comparisonId:
        dff = df[df['media_item_id'] == item]
        title = titlesDf[titlesDf['media_item_id'] == item]['title'].item()
        fig.add_trace(go.Histogram(x=dff['overall-rating'],customdata=dff['user_id'],  name=title, nbinsx=40))

    # Overlay both histograms
    fig.update_layout(barmode='overlay', legend=dict(
                                            orientation="h",
                                            yanchor="bottom",
                                            y=1.02,
                                            xanchor="right",
                                            x=1
                                        ), dragmode='select')
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



    