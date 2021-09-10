
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import plotly.express as px 
import pandas as pd
import traceback



class CMSComponent:
    def __init__(self, componentId,  globalParams):
        self.params = globalParams
        self.componentId = componentId
        self.id = int(globalParams['mediaId'])
        self.clientId = int(globalParams['clientId'])

        self.dataName = '' # needs to be set

    def load(self, data):
        self.mediatitle = pd.read_json(data['title'])['title'].item()
        self.df = pd.read_json(data[self.dataName])
    
    def card(self, title, children):
        comp = dbc.Card([dbc.CardBody([dbc.Row(dbc.Col(html.H6(title))),
                                    dbc.Row(dbc.Col(children))
                                   ])
                    ])              
        return comp

    def graph(self, id, figFunction):
        return dcc.Graph(id=id, config={'displayModeBar':False,'queueLength':0}, figure=figFunction)

    
    
    def show(self, data):
        try:
            self.load(data)
            self.transform()
            return self.display()

        except Exception:
            return self.errorComponent(traceback.format_exc(), data)
    
    def errorComponent(self, e, data):
        return dbc.Alert(e, color="danger", is_open=True)
    


class TitleDropdowns(CMSComponent):
    def __init__(self, compId, globalParams, limit=[]):
        super().__init__(compId, globalParams)
        self.dataName = 'client_titles'
    
    def transform(self):
        items = list(self.df['media_item_id'].unique())
        
        dff = self.df[self.df['media_item_id'].isin(items)][['title', 'media_item_id']]
        dff.rename(columns={'title':'label', 'media_item_id':'value'}, inplace=True)
        self.df = dff.to_dict(orient='records')

    def display(self):
        return dcc.Dropdown(
        id=self.componentId,
        options=self.df,
        value=[],
        multi=True
        )


        



