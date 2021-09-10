import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import plotly.express as px 
import pandas as pd
import dash_table
from  components.utils import *
from components.contained import CMSComponent, TitleDropdowns

def Rating(data, params):
    # stats = OverivewStats(params)
    # demand = OverviewHistogram('demand', params)
    # rating = OverviewHistogram('rating', params)
    # prefs = OverviewPrefs(5, params)
    histo = AllRatingHistogram(globalParams=params)
    ratings = RatingPercentiles(globalParams=params)
    demo = EthnicityComparisons(globalParams=params)

    dropdown = TitleDropdowns('rating-update', params)

    component = html.Div([
        dbc.Row(dbc.Col(dropdown.show(data))),
        dbc.Row([
            dbc.Col(histo.show(data), md=6),
            dbc.Col(ratings.show(data), md=6),           
        ]),
        dbc.Row(
            demo.show(data)
        )
    ], className='p-3')
 
    return component



class AllRatingHistogram(CMSComponent):
    def __init__(self, globalParams, other=[]):
        super().__init__('ratings-allhistogram', globalParams)
        self.other = other

    
    def load(self, data):
        self.titles = pd.read_json(data['client_titles'])
        self.df = pd.read_json(data['all_ratings'])
    
    def transform(self):
        self.toPlot = self.other + [self.id]

    def display(self, returnFig=False):
        fig = go.Figure()
        titles = []
        for item in self.toPlot:
            dff = self.df[self.df['media_item_id'] == item]
            title = self.titles[self.titles['media_item_id'] == item]['title'].item()
            titles.append(title)
            fig.add_trace(go.Histogram(x=dff['overall-rating'], name=title, nbinsx=40, histnorm='percent'))

        fig.update_layout(barmode='overlay', legend=dict(
                                            orientation="h",
                                            yanchor="bottom",
                                            y=1.02,
                                            xanchor="right",
                                            x=1
                                        ), dragmode='select')
    # Reduce opacity to see both histograms
        fig.update_traces(opacity=0.50)

        if returnFig:
            return fig

        graph = self.graph(id=self.componentId, figFunction=fig)
        joined_string = ",".join(titles)
        return self.card(title=f'Distrbution of Ratings for {joined_string}', children=graph)
            

class RatingPercentiles(CMSComponent):
    def __init__(self, globalParams, other=[]):
        super().__init__('ratings-percentile', globalParams)
        self.other = other
    
    
    def load(self, data):
        self.demand = pd.read_json(data['demand']) 
        self.rating = pd.read_json(data['rating']) 
        self.titles = pd.read_json(data['client_titles'])
        self.mediatitle = self.titles[self.titles['media_item_id'] == self.id]['title'].item()
        
    def transform(self):
        toPlot = self.other + [self.id]
        rows = []
        for item in toPlot:
            title = self.titles[self.titles['media_item_id'] == item]['title'].item()
            percentile = self.rating[self.rating['media_item_id'] == item ]['mean_percentile'].item()
            size = self.rating[self.rating['media_item_id'] == item ]['count_rank'].item()
            # TODO:  size should be inverted -- smaller number is actually larger
            rows.append([title, 'rating', percentile , size])
            
            percentile = self.demand[self.demand['media_item_id'] == item ]['mean_percentile'].item()
            size = self.demand[self.demand['media_item_id'] == item ]['count_rank'].item()
            rows.append([title,'demand', percentile , size])
        self.rows = rows

    def display(self, returnFig=False):
        graphDf = pd.DataFrame(self.rows, columns=['Title','type','Percentile','size'])
        fig = px.scatter(graphDf, y='type', x='Percentile', color='Title', size='size')

        if returnFig:
            return fig

        graph = self.graph(id=self.componentId, figFunction=fig)
        return self.card(title=f'Rating Percentile of {self.mediatitle}', children=graph)
        

class EthnicityComparisons(CMSComponent):
    def __init__(self, globalParams, other=[], ratingRange={'min':0, 'max':10}):
        super().__init__('ratings-demo', globalParams)
        self.other = other
        self.min = ratingRange['min']
        self.max = ratingRange['max']

    
    def load(self, data):
        self.titles = pd.read_json(data['client_titles'])
        self.df = pd.read_json(data['all_ratings'])
    
    def transform(self):
        self.toPlot = self.other + [self.id]
        dff = self.df[(self.df['overall-rating'] > self.min) & (self.df['overall-rating'] < self.max)]
        self.dff = dff[dff['media_item_id'].isin(self.toPlot)]

    def display(self, key,  returnFig=False):

        fig = go.Figure()

        for item in self.toPlot:
            vals = self.dff[self.dff['media_item_id'] == item][key].value_counts(normalize=True)
            title = self.titles[self.titles['media_item_id'] == item]['title'].item()
            fig.add_trace(go.Bar(name=title, x=vals.index, y=vals.values))
        
        if returnFig:
            return fig

        graph = self.graph(id=f'{self.componentId}-{key}', figFunction=fig)
        return self.card(title=f'Distrbution of Ratings for {key.capitalize()}', children=graph)

    def show(self, data, keys=['ethnicity','sex','income']):
        try:
            self.load(data)
            self.transform()
            cards = []
            for key in keys:
                cards.append(dbc.Col(self.display(key=key, returnFig=False), md=4))
            
            return cards

        except Exception:
            return self.errorComponent(traceback.format_exc(), data)
    

    

    