import datetime
import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table
from dash_fda.constants import INITIAL_URL, MANUFACTURERS
from dash_fda.utils import get_meta, get_results


jumbotron = dbc.Jumbotron(
    children=[
        html.H1("Dash FDA", className="display-3"),
        html.P(
            "A Plotly Dash application to interact with the API endpoints of openFDA.",
            className="lead",
        ),
    ],
    className="bg-info text-white",
)


def box_plot():
    return dbc.Card(
        [
            dbc.CardBody(
                [
                    html.H3(
                        "Adverse event reports received each month",
                        className="card-title",
                    ),
                    dcc.Graph(
                        id="box-plot-month",
                        config={"editable": False},
                        figure={"layout": {"title": {"text": ""}}},
                    ),
                ]
            ),
        ]
    )


def device_manufacturer_form():
    """medical device label+input and manufacturer label+dropdown"""
    return dbc.Card(
        dbc.Form(
            [
                dbc.FormGroup(
                    [
                        dbc.Label("Device", html_for="medical-device-input"),
                        dbc.Input(
                            id="medical-device-input",
                            placeholder="E.g. x-ray",
                            type="text",
                        ),
                    ]
                ),
                dbc.FormGroup(
                    [
                        dbc.Label("Manufacturer", html_for="manufacturer-dropdown"),
                        dcc.Dropdown(
                            id="manufacturer-dropdown",
                            options=MANUFACTURERS,
                            value=MANUFACTURERS[3]["value"],
                        ),
                    ]
                ),
                html.Div(
                    [
                        dbc.Button("Submit", color="primary", id="submit-button"),
                    ],
                    className="text-right",
                ),
            ]
        )
    )


def pie_charts():
    return html.Div(
        [
            dbc.Card(
                [
                    dbc.CardBody(
                        [
                            # html.H3("Adverse Event Type", className="card-title"),
                            dcc.Graph(id="pie-event"),
                            html.P(
                                "Some quick example text to build on the card title and "
                                "make up the bulk of the card's content.",
                                className="card-text",
                            ),
                        ]
                    ),
                ],
            ),
            dbc.Card(
                [
                    dbc.CardBody(
                        [
                            # html.H3("Medical Device Class", className="card-title"),
                            dcc.Graph(id="pie-device"),
                        ]
                    ),
                ]
            ),
        ]
    )


def footer():
    meta = get_meta(INITIAL_URL)
    disclaimer = meta["disclaimer"]
    return dbc.Card(
        dbc.CardBody(
            [
                html.Span("Built with "),
                dbc.CardLink(
                    "Plotly Dash",
                    href="https://github.com/plotly/dash",
                    target="_blank",
                ),
                html.Span(" — "),
                html.Span("Data from the "),
                dbc.CardLink(
                    "openFDA API", href="https://open.fda.gov/apis/", target="_blank"
                ),
                html.Hr(className="my-2"),
                html.H4("Disclaimer"),
                html.P(disclaimer, className="card-text"),
                html.Span("Terms: "),
                dbc.CardLink(meta["terms"], href=meta["terms"], target="_blank"),
                html.Span(" — "),
                html.Span("License: "),
                dbc.CardLink(meta["license"], href=meta["license"], target="_blank"),
                html.Span(" — "),
                html.Span(f"Last updated: {meta['last_updated']}"),
            ]
        )
    )


def line_charts():
    return html.Div(
        [
            dbc.Card(
                [
                    dbc.CardBody(
                        [
                            html.H3(
                                "Adverse event reports by year",
                                className="card-title",
                            ),
                            dcc.Graph(id="line-chart-year"),
                        ]
                    ),
                ]
            ),
            dbc.Card(
                [
                    dbc.CardBody(
                        [
                            html.H3(
                                "Adverse event reports by month",
                                className="card-title",
                            ),
                            dcc.Graph(id="line-chart-month"),
                        ]
                    ),
                ]
            ),
            dbc.Card(
                [
                    dbc.CardBody(
                        [
                            html.H3(
                                "Adverse event reports by day",
                                className="card-title",
                            ),
                            dcc.Graph(id="line-chart-day"),
                        ]
                    ),
                ]
            ),
        ]
    )


def year_range():
    """Range slider with start year and end year."""
    now = datetime.datetime.now()
    year_min = now.year - 10
    return dcc.RangeSlider(
        id="year-slider",
        min=year_min,
        max=now.year,
        value=[now.year - 5, now.year],
        marks={(i): f"{i}" for i in range(year_min, now.year + 1, 1)},
    )


def table():
    columns = [
        {"name": x, "id": x}
        for x in ["Event type", "Location", "Reporter", "Has MDR Text"]
    ]
    return dash_table.DataTable(
        id="table-fda",
        columns=columns,
        data=[],
        fixed_rows={"headers": True},
        # page_size=20,
        # sort_action="native"
        # style_table={"height": "300px", "overflowY": "auto"},
    )
