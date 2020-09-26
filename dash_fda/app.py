import os
import dash
import dash_table
import dash_bootstrap_components as dbc
import chart_studio
import pandas as pd
import dash_core_components as dcc
import dash_fda.components as dfc
import dash_html_components as html
import plotly.graph_objs as go
from functools import partial
from flask import Flask
from flask_caching import Cache
from dash.dependencies import Input, Output, State
from dash_fda.constants import (
    APP_NAME,
    DEBUG,
    SECRET_KEY,
    URL_PREFIX,
)
from dash_fda.exceptions import ImproperlyConfigured
from dash_fda.utils import (
    create_intermediate_df,
    create_days,
    create_months,
    create_months_box,
    create_years,
    get_results,
    unjsonify,
)


# It would be cool to use Enum, but I don't think that's JSON-serializable.
INITIAL_STATE = {"dateOfEvent": "", "dateReceived": "", "yearBegin": "", "yearEnd": ""}


STORE_ID = f"{APP_NAME.replace(' ', '-')}_store"


server = Flask(APP_NAME)
server.secret_key = SECRET_KEY
app = dash.Dash(
    name=APP_NAME,
    server=server,
    external_stylesheets=[
        dbc.themes.SKETCHY,
        "https://fonts.googleapis.com/css2?family=Roboto&family=Lobster&family=Raleway&display=swap",
    ],
)

cache = Cache(
    app.server,
    config={
        "CACHE_TYPE": "filesystem",
        "CACHE_DIR": "cache",
        "CACHE_THRESHOLD": 10,
        "CACHE_DEFAULT_TIMEOUT": 30,
    },
)
# app.config.supress_callback_exceptions = True


def create_box(df, column):
    return go.Box(name=column, y=df[column].values, boxmean=True)


def content():
    return html.Div(
        children=[
            dfc.year_range(),
            dfc.table(),
            dfc.device_manufacturer_form(),
            dfc.box_plot(),
            dfc.line_charts(),
            dfc.pie_charts(),
        ],
    )


def serve_layout():
    return html.Div(
        children=[
            dcc.Store(
                id=STORE_ID,
                # storage_type="memory",
                # storage_type="local",
                storage_type="session",
                data=INITIAL_STATE,
            ),
            dfc.jumbotron,
            content(),
            dfc.footer(),
        ],
        className="container",
    )


app.layout = serve_layout


@app.callback(
    inputs=[Input("submit-button", "n_clicks")],
    output=Output("table-fda", "data"),
    state=[
        State("year-slider", "value"),
        State("manufacturer-dropdown", "value"),
        State("medical-device-input", "value"),
    ],
)
@cache.memoize(timeout=30)  # in seconds
def update_table(n_clicks, year_range, manufacturer, device):
    begin = "{}-01-01".format(year_range[0])
    end = "{}-12-31".format(year_range[1])
    limit = 100
    url = f"""
    {URL_PREFIX}&search=date_received:[{begin}+TO+{end}]+AND+device.manufacturer_d_name:{manufacturer}+AND+device.generic_name:{device}&limit={limit}&skip=0
    """
    results = get_results(url)
    # print("=== URL ===", url)
    # print("=== RESULTS[0] ===", results[0])

    # TODO: it seems that most of the info is in the mdr_text field (a list)
    data = list()
    for res in results:
        try:
            res["mdr_text"]
            yes_or_no = "Yes"
        except KeyError:
            yes_or_no = "No"

        d = {
            "Event type": res["event_type"],
            "Location": res["event_location"],
            "Reporter": res["reporter_occupation_code"],
            "Has MDR Text": yes_or_no,
        }
        data.append(d)
    return data


@app.callback(
    inputs=[Input("year-slider", "value")],
    output=Output(STORE_ID, "data"),
)
# @cache.memoize(timeout=30)  # in seconds
def set_data_in_store(year_range):
    """Update the app store when the slider changes."""
    begin = "{}-01-01".format(year_range[0])
    end = "{}-12-31".format(year_range[1])

    url_a = (
        "{url_prefix}&search=date_of_event:[{date_begin}+TO+{date_end}]"
        "&count=date_of_event".format(
            url_prefix=URL_PREFIX, date_begin=begin, date_end=end
        )
    )
    df_a = create_intermediate_df(url_a)

    url_b = (
        "{url_prefix}&search=date_received:[{date_begin}+TO+{date_end}]"
        "&count=date_received".format(
            url_prefix=URL_PREFIX, date_begin=begin, date_end=end
        )
    )
    df_b = create_intermediate_df(url_b)

    return {
        "dateOfEvent": df_a.to_json(),
        "dateReceived": df_b.to_json(),
        "yearBegin": f"{year_range[0]}",
        "yearEnd": f"{year_range[-1]}",
    }


@app.callback(
    inputs=[Input("year-slider", "value")],
    output=Output("pie-event", "figure"),
)
# @cache.memoize(timeout=30)  # in seconds (pickle.dump fails)
def update_pie_event(year_range):
    begin = "{}-01-01".format(year_range[0])
    end = "{}-12-31".format(year_range[1])
    url = f"""
    {URL_PREFIX}&search=date_received:[{begin}+TO+{end}]&count=event_type
    """
    results = get_results(url)
    labels = [r["term"] for r in results]
    values = [r["count"] for r in results]

    data = [
        go.Pie(
            name="Event Type",
            values=values,
            labels=labels,
            hoverinfo="label + percent + name",
            hole=0.45,
            # showlegend=False,
        )
    ]
    layout = go.Layout(
        autosize=True,
        hovermode="closest",
        title="Adverse Event Type",
        font=dict(
            # family="Courier New, monospace",
            family="Lobster",
            # family="Raleway",
            # family="Roboto",
            size=18,
            color="RebeccaPurple",
        ),
    )
    return go.Figure(data=data, layout=layout)


# @cache.memoize()  # if placed here, it seems to work
@app.callback(
    inputs=[Input("year-slider", "value")],
    output=Output("pie-device", "figure"),
)
# @cache.memoize()  # if placed here, pickle.dump fails
def update_pie_device(year_range):
    begin = "{}-01-01".format(year_range[0])
    end = "{}-12-31".format(year_range[1])
    url = f"""
    {URL_PREFIX}&search=date_received:[{begin}+TO+{end}]&count=device.openfda.device_class
    """
    results = get_results(url)
    labels = [r["term"] for r in results]
    values = [r["count"] for r in results]

    data = [
        go.Pie(
            name="Device Class",
            values=values,
            labels=labels,
            hoverinfo="label + percent + name",
            hole=0.45,
        )
    ]
    layout = go.Layout(
        autosize=True,
        hovermode="closest",
        title="Medical Device Class",
    )
    return go.Figure(data=data, layout=layout)


@app.callback(
    inputs=[Input(STORE_ID, "data")],
    output=Output("line-chart-year", "figure"),
)
def update_line_chart_by_year(state):
    df_a = unjsonify(state, "dateOfEvent")
    df_a.rename(columns={"count": "A"}, inplace=True)

    df_b = unjsonify(state, "dateReceived")
    df_b.rename(columns={"count": "B"}, inplace=True)

    df_merged = pd.merge(df_a, df_b, on="time")
    df = create_years(df_merged)

    data = [
        go.Scatter(
            x=df.index.values, y=df.A, mode="lines", name="Onset of the adverse event"
        ),
        go.Scatter(
            x=df.index.values,
            y=df["B"],
            mode="lines+markers",
            name="Report received by FDA",
        ),
    ]

    y0 = state["yearBegin"]
    y1 = state["yearEnd"]
    title = f"Adverse event reports by year [{y0} - {y1}]"
    layout = go.Layout(title=title)
    return go.Figure(data=data, layout=layout)


@app.callback(
    inputs=[Input(STORE_ID, "data")],
    output=Output("line-chart-month", "figure"),
)
def update_line_chart_by_month(state):
    df_a = unjsonify(state, "dateOfEvent")
    df_a.rename(columns={"count": "A"}, inplace=True)
    df_b = unjsonify(state, "dateReceived")
    df_b.rename(columns={"count": "B"}, inplace=True)

    df_merged = pd.merge(df_a, df_b, on="time")
    df = create_months(df_merged)

    data = [
        go.Scatter(
            x=df.index.values, y=df.A, mode="lines", name="Onset of the adverse event"
        ),
        go.Scatter(
            x=df.index.values,
            y=df["B"],
            mode="lines+markers",
            name="Report received by FDA",
        ),
    ]

    y0 = state["yearBegin"]
    y1 = state["yearEnd"]
    title = f"Adverse event reports by month [{y0} - {y1}]"
    layout = go.Layout(title=title)
    return go.Figure(data=data, layout=layout)


@app.callback(
    inputs=[Input(STORE_ID, "data")],
    output=Output("box-plot-month", "figure"),
)
def update_box_plot_by_month(state):
    df_b = unjsonify(state, "dateReceived")
    df = create_months_box(df_b)

    func = partial(create_box, df)
    boxes = list(map(func, df.columns))

    data = boxes
    layout = go.Layout(title="")
    return go.Figure(data=data, layout=layout)


@app.callback(
    inputs=[Input(STORE_ID, "data")],
    output=Output("line-chart-day", "figure"),
)
def update_line_chart_by_day(state):
    df_a = unjsonify(state, "dateOfEvent")
    df_a.rename(columns={"count": "A"}, inplace=True)
    df_b = unjsonify(state, "dateReceived")
    df_b.rename(columns={"count": "B"}, inplace=True)

    df_merged = pd.merge(df_a, df_b, on="time")
    df = create_days(df_merged)

    data = [
        go.Scatter(
            x=df.index.values, y=df.A, mode="lines", name="Onset of the adverse event"
        ),
        go.Scatter(
            x=df.index.values,
            y=df["B"],
            mode="lines+markers",
            name="Report received by FDA",
        ),
    ]

    y0 = state["yearBegin"]
    y1 = state["yearEnd"]
    title = f"Adverse event reports by day [{y0} - {y1}]"
    layout = go.Layout(title=title)
    return go.Figure(data=data, layout=layout)


if __name__ == "__main__":
    cache.clear()
    port = int(os.environ.get("PORT", 5000))
    app.run_server(debug=DEBUG, port=port, threaded=True)
