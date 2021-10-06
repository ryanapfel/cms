import plotly.graph_objects as go
import plotly.io as pio


def template():
    pio.templates["bootstrap"] = go.layout.Template(
        {
            "layout": {
                "colorway": [
                    "#FF708B",  # primary
                    "#FFBA69",  # warning
                    "#4DFEE0",  # danger
                    "#8676FF",  # info
                    "#383874",  # secondary
                    "#00B929",  # success
                    "#F6F7FB",  # light
                    "#383874",  # dark
                ],
                "colorscale": {
                    "diverging": [
                        [0, "#8e0152"],
                        [0.1, "#c51b7d"],
                        [0.2, "#de77ae"],
                        [0.3, "#f1b6da"],
                        [0.4, "#fde0ef"],
                        [0.5, "#f7f7f7"],
                        [0.6, "#e6f5d0"],
                        [0.7, "#b8e186"],
                        [0.8, "#7fbc41"],
                        [0.9, "#4d9221"],
                        [1, "#276419"],
                    ],
                    "sequential": [
                        [0.0, "#FF2D2E"],
                        [0.5, "#FFBA69"],
                        [1.0, "#00B929"],
                    ],
                    "sequentialminus": [
                        [0.0, "#0d0887"],
                        [0.1111111111111111, "#46039f"],
                        [0.2222222222222222, "#7201a8"],
                        [0.3333333333333333, "#9c179e"],
                        [0.4444444444444444, "#bd3786"],
                        [0.5555555555555556, "#d8576b"],
                        [0.6666666666666666, "#ed7953"],
                        [0.7777777777777778, "#fb9f3a"],
                        [0.8888888888888888, "#fdca26"],
                        [1.0, "#f0f921"],
                    ],
                },
                "plot_bgcolor": "rgb(255, 255, 255)",
                "paper_bgcolor": "rgb(255, 255, 255)",
                "font": {"size": 12, "color": "#444", "family": "Poppins, sans-serif"},
                "margin": {"l": 0, "r": 0, "t": 0, "b": 0},
                "xaxis": {
                    "showgrid": False,
                    "showline": True,
                    "linecolor": "#383874",
                    "linewidth": 2,
                },
                "yaxis": {
                    "showgrid": True,
                    "showline": True,
                    "linecolor": "#383874",
                    "linewidth": 2,
                    "gridwidth": 2,
                    "gridcolor": "#F6F7FB",
                },
            }
        }
    )

    pio.templates.default = "ggplot2+bootstrap"
