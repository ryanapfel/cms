import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import plotly.express as px 
import pandas as pd
import dash_table
from  components.utils import *
from components.contained import CMSComponent




class OverivewStats(CMSComponent):
    def __init__(self, globalParams):
        super().__init__('overview-card', globalParams)
    
    def load(self, data):
        self.demand = pd.read_json(data['demand'])
        self.overall = pd.read_json(data['rating'])
    

    def transform(self):
        self.demand = self.demand[self.demand['media_item_id' ] == self.id]
        self.overall = self.overall[self.overall['media_item_id'] == self.id]

        data = {}
        data['overall'] = {'value': self.overall['mean'].item(),  'title': 'Average Overall Rating'}
        data['demand'] = {'value': self.demand['mean'].item(),  'title': 'Average Demand Rating'}
        data['count'] = {'value': self.overall['count'].item(),  'title': 'Number of Ratings'}


        self.data = data
    
    def displayValue(self, value, title):
        return html.Div([
                dbc.Row(html.P(title)),
                dbc.Row(html.H3(round(value, 2)))
            ], className='p-3')

    def display(self):
        components = [
            self.displayValue(value=self.data['overall']['value'], 
                         title=self.data['overall']['title']),
            self.displayValue(value=self.data['demand']['value'], 
                         title=self.data['demand']['title']),
            self.displayValue(value=self.data['count']['value'], 
                         title=self.data['count']['title']),
        ]
        kids = html.Div(id=self.componentId, children=components)

        return self.card(title='', children=kids)




class OverviewHistogram(CMSComponent):
    def __init__(self, dataName, globalParams):
        super().__init__(f'overview-histo-{dataName}', globalParams)
        self.dataName = dataName
    
    def transform(self):
        currentItem = self.df[self.df['media_item_id'] == self.id]
        self.itemMean = currentItem['mean'].item()
        self.df = self.df.loc[: , 'mean']
        self.allMean = self.df.mean()
    
    def display(self):
        fig = (px.histogram(self.df, x="mean")
            .update_layout(title_font_size=24)
            .add_vline(x=self.itemMean, line_width=4, annotation_text=f' {self.mediatitle} Rating',  annotation_textangle=-90)
            .add_vline(x=self.allMean, line_width=2, line_color="black", line_dash="dot", annotation_text='Average Rating', annotation_textangle=-90)
            .update_xaxes(title='Rating')
            .update_yaxes(title='Number of Titles'))
        
        graph = self.graph(id=self.componentId, figFunction=fig)
        return self.card(title=f'Distribution of {self.dataName.capitalize()}', children=graph)
    

class OverviewPrefs(CMSComponent):
    def __init__(self, nPrefs , globalParams):
        super().__init__('overview-prefrences', globalParams)
        self.dataName = 'prefrences'
        self.top = nPrefs
    
    def transform(self):
        self.df = self.df.iloc[:self.top].reset_index()
    
    def display(self):
        fig = (px.bar(self.df, y='platform', x='count', orientation='h')
        .update_layout(barmode='stack',  yaxis_categoryorder='total ascending'))
        fig.update_layout({'xaxis': {'title': 'Votes',
                        'visible': True,
                        'showticklabels': True},
                        'yaxis': {'title': '',
                                    'visible': True,
                                    'showticklabels': True}})
                                
        graph = self.graph(id=self.componentId, figFunction=fig)
        return self.card(title=f'Platform Prefrences', children=graph)



def Overview(data, params):
    stats = OverivewStats(params)
    demand = OverviewHistogram('demand', params)
    rating = OverviewHistogram('rating', params)
    prefs = OverviewPrefs(5, params)


    component = html.Div([    
        dbc.Row([
            dbc.Col(stats.show(data), md=2),
            dbc.Col(demand.show(data) ,md=5) ,           
            dbc.Col(rating.show(data) ,md=5) ,           
        ]),
        dbc.Row([
            dbc.Col(prefs.show(data), md=5)
        ])
    ], className='p-3')
 
    return component




