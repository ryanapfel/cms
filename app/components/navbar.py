import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import pandas as pd
from  components.utils import parseData, getMediaTitle

def staticNavbar(title):

    component = dbc.Navbar(
        children=[
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(
                            dbc.NavbarBrand(f"{title} Dashboard", className="ml-2")
                        ),
                    ],
                    align="center",
                    no_gutters=True,
                ),
                href="https://cms2.volkno.com",
            )
        ],
        color="dark",
        dark=True,
        sticky="top",
    )
    return component

def buildNavbar(data, debug=False):
    title = getMediaTitle(data)
    try:
        return staticNavbar(title)
    except Exception as e:
        comp = staticNavbar('Volkno Dashboard')
        return comp
        