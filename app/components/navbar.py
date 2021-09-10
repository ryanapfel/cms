import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import pandas as pd
from  components.utils import parseData, getMediaTitle



def updateClientOptions(client):
    return [{'label': 'Volkno Titles', 'value': 1}, {'label': 'Client Titles', 'value':client}]



def clientDropdown( client):
    try:
        options = [{'label': 'Volkno Titles', 'value': 1} ,
                  {'label': 'Client Titles', 'value': client}]
        
        drop = dcc.Dropdown( 
                    id='client-dropdown',
                    options=options,
                    value=1,
                    clearable=False
                    )
        return drop
    except:
        return dcc.Dropdown(id='client-dropdown', 
                options = [{'label': 'Volkno Titles', 'value': 1}],
                value= 1, 
                clearable=False
                )

def initialDrop():
    options = [{'label': 'Volkno Titles', 'value': 1}]
    return dcc.Dropdown( 
                    id='client-dropdown',
                    options=options,
                    value=1,
                    clearable=False
                    )


def staticNavbar(title):

    component = html.Div([
        dbc.Row([
            dbc.Col(html.Div(initialDrop(), style={'width':'200px'})),
        ])
    ], className='p-3')

    return component

def dynamic(title, client):

    component = dbc.Navbar(
        children=[
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    dbc.Col(dbc.NavbarBrand(f"{title} Dashboard", className="ml-2"), width=3),
                    align="center",
                    no_gutters=True,
                ),
                href="https://cms2.volkno.com",
            ),
            dbc.Row(
            [
                dbc.Col(html.Div(clientDropdown(client), style={'width':'200px'})),

            ],
        no_gutters=True,
        className="ml-auto flex-nowrap mt-3 mt-md-0",
        align="center",
    )
           
        ],
        color="dark",
        dark=True,
        sticky="top",
    )
    return component

def buildNavbar(data, debug=False):
    try:
        title = getMediaTitle(data)
        client = data['client']
        return dynamic(title, int(client))
    except Exception as e:
        return staticNavbar(f'{e}', -1)