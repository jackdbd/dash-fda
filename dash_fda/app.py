import os
import requests
import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import plotly.plotly as py
import plotly.graph_objs as go
from flask import Flask, json
from flask_caching import Cache
from dash import Dash
from dash.dependencies import Input, Output, State, Event
from dotenv import load_dotenv
from datetime import datetime
from dash_fda.exceptions.exceptions import ImproperlyConfigured


def get_results(url):
    req = requests.get(url)
    d = json.loads(req.text)
    return d['results']


external_js = []

external_css = [
    # dash stylesheet
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    'https://fonts.googleapis.com/css?family=Lobster|Raleway',
]

if 'DYNO' in os.environ:
    # the app is on Heroku
    debug = False
    # google analytics with the tracking ID for this app
    external_js.append('https://codepen.io/jackdbd/pen/NgmpzR.js')
else:
    debug = True
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(dotenv_path)

py.sign_in(os.environ['PLOTLY_USERNAME'], os.environ['PLOTLY_API_KEY'])
openFDA = 'https://api.fda.gov/'
api_endpoint = 'device/event.json?'
api_key = os.environ.get('OPEN_FDA_API_KEY')
if api_key is None:
    raise ImproperlyConfigured('openFDA API KEY not set in .env')

app_name = 'Dash FDA'
server = Flask(app_name)
server.secret_key = os.environ.get('SECRET_KEY')
if server.secret_key is None:
    raise ImproperlyConfigured('Flask SECRET KEY not set in .env')
app = Dash(name=app_name, server=server, csrf_protect=False)

cache = Cache(app.server, config={
    'CACHE_TYPE': 'filesystem', 'CACHE_DIR': 'cache',
    'CACHE_THRESHOLD': 10, 'CACHE_DEFAULT_TIMEOUT': 30})
# app.config.supress_callback_exceptions = True

# # Reported device's generic name includes x-ray
# device_name = 'x-ray'
# url2 = '{}{}search=device.generic_name:{}&count=date_received'\
#     .format(openFDA, api_endpoint, device_name)

url_prefix = '{openFDA}{api_endpoint}api_key={api_key}'\
    .format(openFDA=openFDA, api_endpoint=api_endpoint, api_key=api_key)

initial_url = '{}&count=date_of_event'.format(url_prefix)
initial_results = get_results(initial_url)

theme = {
    'font-family': 'Lobster',
    'background-color': '#787878',
}


def create_header():
    header_style = {
        'background-color': theme['background-color'],
        'padding': '1.5rem',
    }
    header = html.Header(html.H1(children=app_name, style=header_style))
    return header


def create_content():
    content = html.Div(
        children=[

            # range slider with start date and end date
            html.Div(
                children=[
                    dcc.RangeSlider(
                        id='year-slider',
                        min=1991,
                        max=2017,
                        value=[2010, 2015],
                        marks={(i): '{}'.format(i) for i in range(1991, 2017, 5)},
                    ),
                ],
                style={'margin-bottom': 20, 'background-color': '#ff0000'},
            ),

            # pie charts
            html.Div(
                children=[
                    html.Div(
                        dcc.Graph(id='pie-event'),
                        className='six columns',
                    ),
                    html.Div(
                        dcc.Graph(id='pie-device'),
                        className='six columns',
                    ),
                ],
                className='row',
                style={'margin-bottom': 20, 'background-color': '#789789'},
            ),

            html.Hr(),

            # line chart
            html.Div(
                children=[
                    dcc.Graph(id='line-chart'),
                ],
                className='row',
                style={'margin-bottom': 30, 'background-color': '#ff0000'},
            ),

            # date picker with start date and end date
            html.Div(
                children=[
                    dcc.DatePickerRange(
                        id='date-picker-range',
                        calendar_orientation='horizontal',
                        clearable=True,
                        display_format='DD/MM/YYYY',
                        start_date=datetime(1991, 1, 2),
                        # start_date_placeholder_text='Select a date!',
                        end_date=datetime.now(),
                        # end_date_placeholder_text='Select a date!',
                        min_date_allowed='1991-01-01',
                    ),
                ],
                className='five columns',
                # style={'background-color': '#00f'}
            ),
            # manufacturer label+dropdown
            html.Div(
                children=[
                    # html.Label('Manufacturer', id='manufacturer-label'),
                    dcc.Dropdown(
                        id='manufacturer-dropdown',
                        options=[
                            {'label': 'Covidien', 'value': 'COVIDIEN'},
                            {'label': 'GE Healthcare', 'value': 'GE+Healthcare'},
                            {'label': 'Medtronic', 'value': 'MEDTRONIC+MINIMED'},
                            {'label': 'Zimmer', 'value': 'ZIMMER+INC.'},
                            {'label': 'Baxter', 'value': 'BAXTER+HEALTHCARE+PTE.+LTD.'},
                            {'label': 'Smiths Medical', 'value': 'SMITHS+MEDICAL+MD+INC.'},
                        ],
                        # multi=True,
                        value='GE+Healthcare',
                    ),
                ],
                className='four columns offset-by-one',
                # style={'background-color': '#0f0'},
            ),
            # button
            html.Div(
                children=[
                    html.Button('Submit', id='button'),
                ],
                className='two columns',
                # style={'background-color': '#f00'},
            ),
            # table with dash_table_experiments
            dt.DataTable(
                id='table-fda',
                rows=initial_results,
                filterable=True,
                sortable=True,
                # selected_row_indices=[],
            ),
            dcc.Graph(id='graph-fda'),
            html.Hr(),
        ],
        id='content',
        style={'width': '100%', 'height': '100%'},
    )
    return content


def create_footer():
    footer_style = {
        'background-color': theme['background-color'],
        'padding': '0.5rem',
    }
    footer = html.Footer(children=['disclaimer here...'], style=footer_style)
    return footer


def serve_layout():
    layout = html.Div(
        children=[
            create_header(),
            create_content(),
            create_footer(),
        ],
        className='container',
        style={'font-family': theme['font-family']},
    )
    return layout


app.layout = serve_layout
for js in external_js:
    app.scripts.append_script({'external_url': js})
for css in external_css:
    app.css.append_css({'external_url': css})


@app.callback(
    output=Output('table-fda', 'rows'),
    inputs=[Input('button', 'n_clicks')],
    state=[
        State('manufacturer-dropdown', 'value'),
        State('date-picker-range', 'start_date'),
        State('date-picker-range', 'end_date'),
    ]
)
@cache.memoize(timeout=30)  # in seconds
def _update_table(n_clicks, manufacturer, start_date, end_date):
    start = start_date.split(' ')[0]
    end = end_date.split(' ')[0]
    url = '{url_prefix}&search=date_received:[{date_start}+TO+{date_end}]+' \
          'AND+device.manufacturer_d_name:{manufacturer}' \
          '&count=device.generic_name.exact&limit={num}&skip=0'\
        .format(url_prefix=url_prefix, date_start=start, date_end=end,
                manufacturer=manufacturer, num=10)
    req = requests.get(url)
    d = json.loads(req.text)
    rows = d['results']
    return rows


# TIME SERIES: https://api.fda.gov/device/event.json?count=date_received
# https://api.fda.gov/device/event.json?count=date_report_to_fda

# https://api.fda.gov/device/event.json?api_key=API-KEY-HERE&search=date_received:[2016-01-01+TO+2016-01-03]+AND+event_type:Injury&limit=3

@app.callback(
    output=Output('graph-fda', 'figure'),
    inputs=[Input('button', 'n_clicks')],
    state=[
        State('manufacturer-dropdown', 'value'),
        State('date-picker-range', 'start_date'),
        State('date-picker-range', 'end_date'),
    ],
)
@cache.memoize(timeout=30)  # in seconds
def _update_graph(n_clicks, manufacturer, start_date, end_date):
    start = start_date.split(' ')[0]
    end = end_date.split(' ')[0]
    url = '{url_prefix}&search=date_received:[{date_start}+TO+{date_end}]+' \
          'AND+device.manufacturer_d_name:{manufacturer}' \
          '&count=device.generic_name.exact&limit={num}&skip=0'\
        .format(url_prefix=url_prefix, date_start=start, date_end=end,
                manufacturer=manufacturer, num=10)
    req = requests.get(url)
    d = json.loads(req.text)
    x = [r['term'] for r in d['results']]
    y = [r['count'] for r in d['results']]

    figure = {
        'data': [
            {'x': x, 'y': y, 'type': 'bar', 'name': manufacturer},
        ],
        'layout': {
            'title': 'Adverse events with devices by {}'.format(manufacturer)
        }
    }
    return figure


@app.callback(
    output=Output('pie-event', 'figure'),
    inputs=[
        Input('year-slider', 'value'),
    ],
)
# @cache.memoize(timeout=30)  # in seconds
def _update_pie_event(year_range):
    date_start = '{}-01-01'.format(year_range[0])
    date_end = '{}-12-31'.format(year_range[1])
    url = '{url_prefix}&search=date_received:[{date_start}+TO+{date_end}]' \
          '&count=event_type'\
        .format(url_prefix=url_prefix, date_start=date_start, date_end=date_end)
    results = get_results(url)
    labels = [r['term'] for r in results]
    values = [r['count'] for r in results]

    data = go.Data([
        go.Pie(
            name='Event Type',
            values=values,
            labels=labels,
            hoverinfo='label + percent + name',
            hole=0.45,
        ),
    ])
    layout = go.Layout(
        title='Adverse Event Type',
        autosize=True,
        hovermode='closest',
        font=dict(family=theme['font-family'], color='#777777', size='24'),
        # margin=go.Margin(l=0, r=0, t=45, b=10),
    )
    figure = go.Figure(data=data, layout=layout)
    return figure


@app.callback(
    output=Output('pie-device', 'figure'),
    inputs=[
        Input('year-slider', 'value'),
    ],
)
# @cache.memoize(timeout=30)  # in seconds
def _update_pie_device(year_range):
    date_start = '{}-01-01'.format(year_range[0])
    date_end = '{}-12-31'.format(year_range[1])
    url = '{url_prefix}&search=date_received:[{date_start}+TO+{date_end}]' \
          '&count=device.openfda.device_class'\
        .format(url_prefix=url_prefix, date_start=date_start, date_end=date_end)
    results = get_results(url)
    labels = [r['term'] for r in results]
    values = [r['count'] for r in results]

    data = go.Data([
        go.Pie(
            name='Device Class',
            values=values,
            labels=labels,
            hoverinfo='label + percent + name',
            hole=0.45,
        ),
    ])
    layout = go.Layout(
        title='Medical Device Class',
        autosize=True,
        hovermode='closest',
        font=dict(family=theme['font-family'], color='#777777', size='24'),
    )
    figure = go.Figure(data=data, layout=layout)
    return figure


@app.callback(
    output=Output('line-chart', 'figure'),
    inputs=[
        Input('year-slider', 'value'),
    ],
)
def _update_line_chart(year_range):
    date_start = '{}-01-01'.format(year_range[0])
    date_end = '{}-12-31'.format(year_range[1])
    url = '{url_prefix}&search=date_of_event:[{date_start}+TO+{date_end}]' \
          '&count=date_of_event' \
        .format(url_prefix=url_prefix, date_start=date_start, date_end=date_end)

    # url = '{url_prefix}&search=date_received:[{date_start}+TO+{date_end}]' \
    #       '&count=date_received' \
    #     .format(url_prefix=url_prefix, date_start=date_start,
    #             date_end=date_end)
    results = get_results(url)
    df = pd.DataFrame(results)

    # in order to group by week, year, etc we need a datetime variable and set
    # it as an index
    df['date'] = pd.to_datetime(df['time'])
    df.set_index(df['date'], inplace=True)
    # we don't need the original time column any longer
    df.drop(['time'], axis=1, inplace=True)

    dff = df.resample('Y').sum()
    # dff.resample('M').mean()
    # dff.resample('D', how='sum')
    dff.rename(columns={'count': 'aggregated_count'}, inplace=True)
    dff['year'] = dff.index.strftime('%Y')

    dates = dff['year']
    counts = dff['aggregated_count']

    data = go.Data([
        go.Scatter(
            x=dates,
            y=counts,
            mode='lines',
            name='lines',
        ),
        go.Scatter(
            x=dates,
            y=counts,
            mode='lines+markers',
            name='lines and markers',
        )
    ])
    layout = go.Layout(
        title='From {} to {}'.format(dates[0], dates[-1]),
        yaxis={'title': 'Reports received by FDA'},
    )
    figure = go.Figure(data=data, layout=layout)
    return figure


if __name__ == '__main__':
    cache.clear()
    port = int(os.environ.get('PORT', 5000))
    app.run_server(debug=debug, port=port, threaded=True)
