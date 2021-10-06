import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import plotly.express as px
import pandas as pd
from components.utils import *
from components.contained import CMSComponent, TitleDropdowns
import traceback


def Rating(data, params):
    histo = AllRatingHistogram(globalParams=params)
    ratings = RatingPercentiles(globalParams=params)
    demo = DemoComparisons(globalParams=params)

    dropdown = TitleDropdowns("rating-update", params)

    component = html.Div(
        [
            dbc.Row(
                dbc.Col(
                    [
                        html.H2("Ratings"),
                        dbc.FormGroup(
                            [
                                dbc.Label(
                                    "Select Comparables", html_for="example-email"
                                ),
                                dropdown.show(data),
                                dbc.FormText(
                                    "Note: Only the most recent 100 titles for the selected client are included for comparisons.",
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
                    dbc.Col(histo.show(data), md=6),
                    dbc.Col(ratings.show(data), md=6),
                ]
            ),
            dbc.Row(demo.show(data)),
        ],
        className="p-3",
    )

    return component


class AllRatingHistogram(CMSComponent):
    def __init__(self, globalParams, other=[]):
        super().__init__("ratings-allhistogram", globalParams)
        self.other = other

    def load(self, data):
        self.titles = pd.read_json(data["client_titles"])
        self.df = pd.read_json(data["all_ratings"])

    def transform(self):
        self.toPlot = self.other + [self.id]

    def display(self, returnFig=False):
        fig = go.Figure()
        titles = []
        for item in self.toPlot:
            dff = self.df[self.df["media_item_id"] == item]
            title = self.titles[self.titles["media_item_id"] == item]["title"].item()
            titles.append(title)
            fig.add_trace(
                go.Histogram(
                    x=dff["overall-rating"], name=title, nbinsx=20, histnorm="percent"
                )
            )

        fig.update_layout(
            barmode="overlay",
            yaxis_title="Percent",
            xaxis=dict(tickmode="linear", tick0=0, dtick=1, title="Ratings"),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
            ),
            dragmode="select",
        )
        # Reduce opacity to see both histograms
        fig.update_traces(opacity=0.50)

        if returnFig:
            return fig

        graph = self.graph(id=self.componentId, figFunction=fig)
        joined_string = ",".join(titles)
        return self.card(
            title=f"Distrbution of Ratings for {joined_string}", children=graph
        )


class RatingPercentiles(CMSComponent):
    def __init__(self, globalParams, other=[]):
        super().__init__("ratings-percentile", globalParams)
        self.other = other

    def load(self, data):
        self.demand = pd.read_json(data["demand"])
        self.rating = pd.read_json(data["rating"])
        self.titles = pd.read_json(data["client_titles"])
        self.mediatitle = self.titles[self.titles["media_item_id"] == self.id][
            "title"
        ].item()

    def transform(self):
        toPlot = self.other + [self.id]
        rows = []
        for item in toPlot:
            title = self.titles[self.titles["media_item_id"] == item]["title"].item()
            percentile = self.rating[self.rating["media_item_id"] == item][
                "mean_percentile"
            ].item()
            size = self.rating[self.rating["media_item_id"] == item][
                "count_rank"
            ].item()
            # TODO:  size should be inverted -- smaller number is actually larger
            rows.append([title, "rating", percentile, size])

            percentile = self.demand[self.demand["media_item_id"] == item][
                "mean_percentile"
            ].item()
            size = self.demand[self.demand["media_item_id"] == item][
                "count_rank"
            ].item()
            rows.append([title, "demand", percentile, size])
        self.rows = rows

    def display(self, returnFig=False):
        graphDf = pd.DataFrame(
            self.rows, columns=["Title", "type", "Percentile", "size"]
        )
        fig = px.scatter(graphDf, y="type", x="Percentile", color="Title", size="size")

        fig.update_layout(
            yaxis_title="",
            xaxis=dict(
                tickmode="linear", tick0=0, dtick=0.1, title="Percentile", range=[0, 1]
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
            ),
        )

        if returnFig:
            return fig

        graph = self.graph(id=self.componentId, figFunction=fig)
        return self.card(
            title=f"Rating Percentile of {self.mediatitle}", children=graph
        )


class DemoComparisons(CMSComponent):
    def __init__(self, globalParams, other=[], ratingRange={"min": 0, "max": 10}):
        super().__init__("ratings-demo", globalParams)
        self.other = other
        self.min = ratingRange["min"]
        self.max = ratingRange["max"]

    def load(self, data):
        self.titles = pd.read_json(data["client_titles"])
        self.df = pd.read_json(data["all_ratings"])

    def transform(self):
        self.toPlot = self.other + [self.id]
        dff = self.df[
            (self.df["overall-rating"] > self.min)
            & (self.df["overall-rating"] < self.max)
        ]
        self.dff = dff[dff["media_item_id"].isin(self.toPlot)]

    def display(self, key, returnFig=False):

        fig = go.Figure()

        for item in self.toPlot:
            vals = self.dff[self.dff["media_item_id"] == item][key].value_counts(
                normalize=True
            )
            title = self.titles[self.titles["media_item_id"] == item]["title"].item()
            fig.add_trace(go.Bar(name=title, x=vals.index, y=vals.values))

        fig.update_layout(
            # xaxis_title="Percent ",
            yaxis_title="Percent",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
            ),
        )

        if returnFig:
            return fig

        graph = self.graph(id=f"{self.componentId}-{key}", figFunction=fig)
        return self.card(
            title=f"Distrbution of Ratings for {key.capitalize()}", children=graph
        )

    def show(self, data, keys=["ethnicity", "sex", "income"]):
        try:
            self.load(data)
            self.transform()
            cards = []
            for key in keys:
                cards.append(dbc.Col(self.display(key=key, returnFig=False), md=4))

            return cards

        except Exception:
            return self.errorComponent(traceback.format_exc(), data)
