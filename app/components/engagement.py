import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import plotly.express as px 
import pandas as pd
import dash_table
from  components.utils import *
import traceback
from components.contained import CMSComponent, TitleDropdowns

def Engagement(data, params):
    engagement = EngagementGraph(globalParams=params)
    vid = Video(globalParams=params)
    emotions =EmotionGraph(globalParams=params)
    component = html.Div([
        html.H1('Hello'),
        dbc.Row([
        dbc.Col(engagement.show(data), md=8),
        dbc.Col(vid.show(data), md=4),
        ]),
        dbc.Row(dbc.Col(engageDrop(), md=3)),
        dbc.Row(id='engagement-emotions-wrapper', children=emotions.show(data)),
        # dbc.Row(
        #     demo.show(data)
        # )
    ], className='p-3')
 
    return component


def engageDrop():
    options = [{'label':'Emotions', 'value':'EMOJI'}, {'label':'Hot or Not', 'value':'HOT_OR_NOT', }]
    return dcc.Dropdown(id='engagement-drop', options=options, value='EMOJI', multi=False)


class Video(CMSComponent):
    def __init__(self, globalParams, vidRange={'min':0, 'max':100}):
        super().__init__('engagement-vid', globalParams) 
        self.dataName = 'title'
        self.minPercent = vidRange['min']
        self.maxPercent  = vidRange['max']


    
    def load(self, data):
        self.mediatitle = pd.read_json(data['title'])['title'].item()
        self.df = pd.read_json(data[self.dataName])
        self.scenes = pd.read_json(data['scenes'])
    
    def transform(self):
        self.url = self.df[self.df['media_item_id'] == self.id]['url_1'].item()
        length = self.scenes[self.scenes['media_item_id'] == self.id]['end'].max()
        self.start = int(length * (self.minPercent / 100))
        self.end = int(length * (self.maxPercent / 100))

    def display(self):
        video = html.Video(src=f'{self.url}#t={self.start},{self.end}', controls = True, width='100%')
        title = f'{self.mediatitle} from {round(self.minPercent,0)}% to {round(self.maxPercent, 0)}%'
        return html.Div(id=self.componentId, 
                        children=self.card(title=title,children=video))



class EngagementGraph(CMSComponent):
    def __init__(self, globalParams, other=[]):
        super().__init__('engagement-percentile', globalParams)
        self.other = other
        self.dataName = 'client_engagment'
    
    def load(self, data):
        super().load(data)
        self.titles = pd.read_json(data['client_titles'])
    
    def transform(self):
        self.toPlot = self.other + [self.id]
    
    def display(self, returnFig=False):
        fig = go.Figure()
        for items in self.toPlot:
            dff = self.df[self.df['media_item_id'] == items]
            title = self.titles[self.titles['media_item_id'] == items]['title'].item()
            fig.add_trace(go.Scatter(x=dff['percentile'], 
                                 y=dff['normalized'].interpolate(), 
                                 name=f'{title}',
                                 mode='lines',
                                 line={'width':2, 'dash':'solid'}))


        fig.update_layout(legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1),
                          dragmode='select', 
                          selectdirection='h'
                          )

        
        if returnFig:
            return fig

        graph = self.graph(id=self.componentId, figFunction=fig)
        return self.card(title=f'Net Engagement', children=graph)
        


class EmotionGraph(CMSComponent):
    def __init__(self, globalParams, key='EMOJI', vidRange={'min':0, 'max':100}):
        super().__init__('engagement-emotions', globalParams)
        self.dataName = 'mediaRawEngagement'
        self.minPercent = vidRange['min']
        self.maxPercent  = vidRange['max']
        self.key = key

    def load(self, data):
        self.avgs = {"HOT_OR_NOT" : {"hot":13027392,
                "not": 1356411,
                },
                "EMOJI" : {"omg":3287942,
                "joy":3694890,
                "excited":4574767,
                "ouch":750170,
                "angry":626166,
                "sad":783843}}

        self.mediatitle = pd.read_json(data['title'])['title'].item()
        self.df = pd.read_json(data[self.dataName])
        self.scenes = pd.read_json(data['scenes'])
    
    def transform(self):
        length = self.scenes[self.scenes['media_item_id'] == self.id]['end'].max()
        self.start = int(length * (self.minPercent / 100))
        self.end = int(length * (self.maxPercent / 100))
        self.df = self.df[(self.df['timestamp'] >= self.start) &(self.df['timestamp'] <= self.end)]
        self.vals = self.df[self.df['meta_key'] == self.key]['meta_value'].value_counts(normalize=True)
        norms = pd.DataFrame(self.avgs[self.key], index=['count']).T
        norms['normalized'] = norms['count'] / norms['count'].sum()
        self.normvals = (norms['normalized'] - self.vals) * 100

    def display(self, graphType):
        idComp = f'self.componentId-{graphType}'
        if graphType == 'raw':
            fig = go.Figure(data=[go.Pie(labels=self.vals.index,
                             values=self.vals.values)])
            fig.update_traces(hoverinfo='label+percent', textinfo='label+percent', textfont_size=20,
                  marker=dict(line=dict(color='#000000', width=2)))
            graph = self.graph(id=idComp,
                                figFunction=fig)
            title = ''
        elif graphType == 'norms':
            fig = px.bar(x=self.normvals.index, y=self.normvals.values, color=self.normvals.values, color_continuous_scale='RdBu')
            graph = self.graph(id=idComp,
                               figFunction=fig)
            title=''
        elif graphType == 'table':
            df = pd.DataFrame(self.normvals, columns=['Marginal Difference']).reset_index().rename(columns={'index':'Value'})
            df['Marginal Difference'] = round(df['Marginal Difference'],2)
            graph = dbc.Table.from_dataframe(df)
            title = ''

        
        return self.card(title=title, children=graph)
    
    def show(self, data, keys=['raw','norms','table']):
        try:
            self.load(data)
            self.transform()
            cards = []
            for key in keys:
                cards.append(dbc.Col(self.display(graphType=key), md=4))
            
            return cards

        except Exception:
            return self.errorComponent(traceback.format_exc(), data)
    




    

    






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


