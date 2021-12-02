import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import plotly.express as px
import pandas as pd
from components.utils import *
import traceback
from components.contained import CMSComponent, TitleDropdowns
import numpy as np


def Engagement(data, params):
    engagement = EngagementGraph(globalParams=params)
    vid = Video(globalParams=params)
    emotions = EmotionGraph(globalParams=params)
    compDrop = TitleDropdowns("engage-update", globalParams=params)

    component = html.Div(
        [
            dbc.Row(
                dbc.Col(
                    [
                        html.H2("Engagement"),
                        dbc.FormGroup(
                            [
                                dbc.Label("Select Comparables", html_for=""),
                                compDrop.show(data),
                                dbc.FormText(
                                    "Note: Only the most recent 250 titles for the selected client are included for comparisons.",
                                    color="grey",
                                ),
                            ]
                        ),
                    ],
                    md=4,
                )
            ),
            dbc.Row(
                [
                    dbc.Col(engagement.show(data), md=8),
                    dbc.Col(vid.show(data), md=4),
                ]
            ),
            dbc.Row(
                dbc.Col(
                    dbc.FormGroup(
                        [
                            dbc.Label("Select Data Type", html_for=""),
                            engageDrop(),
                        ]
                    ),
                    md=3,
                )
            ),
            dbc.Row(id="engagement-emotions-wrapper", children=emotions.show(data)),
            # dbc.Row(
            #     demo.show(data)
            # )
        ],
        className="p-3",
    )

    return component


def engageDrop():
    options = [
        {"label": "Emotions", "value": "EMOJI"},
        {
            "label": "Hot or Not",
            "value": "HOT_OR_NOT",
        },
    ]
    return dcc.Dropdown(
        id="engagement-drop", options=options, value="EMOJI", multi=False
    )


class Video(CMSComponent):
    def __init__(self, globalParams, vidRange={"min": 0, "max": 100}):
        super().__init__("engagement-vid", globalParams)
        self.dataName = "title"
        self.minPercent = vidRange["min"]
        self.maxPercent = vidRange["max"]

    def load(self, data):
        self.mediatitle = pd.read_json(data["title"])["title"].item()
        self.df = pd.read_json(data[self.dataName])
        self.video = pd.read_json(data["video_info"])

    def transform(self):
        self.url = self.df[self.df["media_item_id"] == self.id]["url_1"].item()
        try:
            length = self.video[self.video["media_item_id"] == self.id][
                "duration"
            ].item()
            self.start = int(length * (self.minPercent / 100))
            self.end = int(length * (self.maxPercent / 100))
        except:
            self.start = 0
            self.end = 5000

    def display(self):
        video = html.Video(
            src=f"{self.url}#t={self.start},{self.end}", controls=True, width="100%"
        )
        title = f"{self.mediatitle} from {round(self.minPercent,0)}% to {round(self.maxPercent, 0)}%"
        return html.Div(
            id=self.componentId, children=self.card(title=title, children=video)
        )


class EngagementGraph(CMSComponent):
    def __init__(self, globalParams, other=[]):
        super().__init__("engagement-percentile", globalParams)
        self.other = other
        self.dataName = "client_engagment"

    def load(self, data):
        super().load(data)
        self.titles = pd.read_json(data["client_titles"])

    def transform(self):
        self.toPlot = self.other + [self.id]

    def display(self, returnFig=False):
        fig = go.Figure()
        for items in self.toPlot:
            dff = self.df[self.df["media_item_id"] == items]
            title = self.titles[self.titles["media_item_id"] == items]["title"].item()
            fig.add_trace(
                go.Scatter(
                    x=dff["percentile"],
                    y=dff["count"].interpolate(),
                    name=f"{title}",
                    mode="lines",
                    line={"width": 2, "dash": "solid"},
                )
            )

        fig.update_layout(
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
            ),
            dragmode="select",
            yaxis_title="Total Engagement",
            xaxis=dict(title="Percent of Trailer"),
            selectdirection="h",
        )

        if returnFig:
            return fig

        graph = self.graph(id=self.componentId, figFunction=fig)
        return self.card(title=f"Net Engagement", children=graph)


class EmotionGraph(CMSComponent):
    def __init__(self, globalParams, key="EMOJI", vidRange={"min": 0, "max": 100}):
        super().__init__("engagement-emotions", globalParams)
        self.dataName = "mediaRawEngagement"
        self.minPercent = vidRange["min"]
        self.maxPercent = vidRange["max"]
        self.key = key

    def load(self, data):
        # NOTE Emoji scared and suprsied might need to be changed back to ouch and omg

        self.avgs = {
            "HOT_OR_NOT": {
                "hot": 13027392,
                "not": 1356411,
            },
            "EMOJI": {
                "suprised": 3287942,
                "joy": 3694890,
                "excited": 4574767,
                "scared": 750170,
                "angry": 626166,
                "sad": 783843,
            },
        }

        self.mediatitle = pd.read_json(data["title"])["title"].item()
        self.df = pd.read_json(data[self.dataName])
        self.video = pd.read_json(data["video_info"])

    def transform(self):
        # NOTE Emoji scared and suprsied might need to be changed back to ouch and omg

        self.df.replace(
            to_replace=["ouch", "omg"], value=["scared", "suprised"], inplace=True
        )

        try:
            length = self.video[self.video["media_item_id"] == self.id][
                "duration"
            ].item()
            self.start = int(length * (self.minPercent / 100))
            self.end = int(length * (self.maxPercent / 100))
        except:
            self.start = 0
            self.end = 5000

        self.df = self.df[
            (self.df["timestamp"] >= self.start) & (self.df["timestamp"] <= self.end)
        ]
        self.vals = self.df[self.df["meta_key"] == self.key]["meta_value"].value_counts(
            normalize=True
        )
        norms = pd.DataFrame(self.avgs[self.key], index=["count"]).T
        norms["normalized"] = norms["count"] / norms["count"].sum()
        self.normvals = (norms["normalized"] - self.vals) * 100

    def display(self, graphType):
        idComp = f"self.componentId-{graphType}"
        if graphType == "raw":
            fig = go.Figure(
                data=[go.Pie(labels=self.vals.index, values=self.vals.values)]
            )

            fig.update_traces(
                hoverinfo="label+percent",
                textinfo="label+percent",
                textfont_size=20,
                marker=dict(line=dict(color="#fff", width=4)),
            )
            graph = self.graph(id=idComp, figFunction=fig)
            title = ""
            return self.card(title=title, children=graph)
        elif graphType == "norms":
            fig = px.bar(
                x=self.normvals.index,
                y=self.normvals.values,
                color=self.normvals.values,
            )
            fig.update_layout(
                yaxis_title="Difference From Expectation",
                xaxis_title="",
                xaxis={"categoryorder": "total descending"},
                showlegend=False,
                coloraxis_showscale=False,
            )

            graph = self.graph(id=idComp, figFunction=fig)
            title = ""
            return self.card(title=title, children=graph)
        elif graphType == "table":
            tables = []
            for index, value in self.normvals.items():
                tables.append(getInsightCard(index, value))
            return html.Div(children=tables)

    def show(self, data, keys=["raw", "norms", "table"]):
        try:
            self.load(data)
            self.transform()
            cards = []
            for key in keys:
                cards.append(dbc.Col(self.display(graphType=key), md=4))

            return cards

        except Exception:
            return self.errorComponent(traceback.format_exc(), data)


def getInsightCard(index, value):
    valueClean = round(value, 2)

    if valueClean > 0:
        sValue = f"  {np.abs(valueClean)}%"
        badge = html.H5(
            [
                dbc.Badge(
                    html.I(className="fa fa-arrow-up green-font"),
                    color="#a4e5b2",
                    className="mr-1",
                ),
                sValue,
            ]
        )
        text = html.P(
            f"{index.capitalize()} is {sValue} higher than expected for the selected time."
        )
    else:
        sValue = f"  {np.abs(valueClean)}%"
        badge = html.H5(
            [
                dbc.Badge(
                    html.I(className="fa fa-arrow-down red-font"),
                    color="#ffbecb",
                    className="mr-1",
                ),
                sValue,
            ]
        )

        text = html.P(
            f"{index.capitalize()} is {sValue} lower than expected for the selected time."
        )

    comp = dbc.Card(dbc.CardBody([badge, text]), style={"margin-bottom": "10px"})

    return comp
