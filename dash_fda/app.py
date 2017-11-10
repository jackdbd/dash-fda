import os
import requests
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
from flask import Flask, json
from flask_caching import Cache
from dash import Dash
from dash.dependencies import Input, Output, State, Event
from dotenv import load_dotenv
from datetime import datetime
from dash_fda.exceptions.exceptions import ImproperlyConfigured


external_js = []

external_css = [
    # dash stylesheet
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    'https://fonts.googleapis.com/css?family=Lobster|Raleway',
]


try:
    # the app is on Heroku
    os.environ['DYNO']
    debug = False
    # google analytics with the tracking ID for this app
    external_js.append('https://codepen.io/jackdbd/pen/NgmpzR.js')
except KeyError:
    debug = True
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(dotenv_path)

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

# Number of device adverse events since 1991
# url1 = '{openFDA}{api_endpoint}count=date_received'\
#     .format(openFDA=openFDA, api_endpoint=api_endpoint)
#
# # Reported device's generic name includes x-ray
# device_name = 'x-ray'
# url2 = '{}{}search=device.generic_name:{}&count=date_received'\
#     .format(openFDA, api_endpoint, device_name)

styles = {
    'column': {
        'display': 'inline-block',
        'width': '33%',
        'padding': 10,
        'boxSizing': 'border-box',
        'minHeight': '200px'
    },
    'pre': {'border': 'thin lightgrey solid'}
}

initial_url = '{openFDA}{api_endpoint}api_key={api_key}' \
              '&search=date_received:[1991-01-01+TO+2017-11-10]' \
              'AND+device.manufacturer_d_name:Covidien' \
              '&count=device.generic_name.exact&limit=10'\
    .format(openFDA=openFDA, api_endpoint=api_endpoint, api_key=api_key)
initial_req = requests.get(initial_url)
initial_d = json.loads(initial_req.text)

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
            # button. It's the only Input in this app (i.e. the only component
            # that triggers the callback )
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
                rows=initial_d['results'],
                filterable=True,
                sortable=True,
                # selected_row_indices=[],
            ),
            dcc.Graph(id='graph-fda')
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
    url = '{openFDA}{api_endpoint}api_key={api_key}&search=date_received:[' \
          '{date_start}+TO+{date_end}]+AND+device.manufacturer_d_name:' \
          '{manufacturer}&count=device.generic_name.exact&limit={num}&skip=0' \
        .format(openFDA=openFDA, api_endpoint=api_endpoint, api_key=api_key,
                date_start=start, date_end=end, manufacturer=manufacturer, num=10)
    req = requests.get(url)
    d = json.loads(req.text)
    rows = d['results']
    return rows


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
    url = '{openFDA}{api_endpoint}api_key={api_key}&search=date_received:[' \
          '{date_start}+TO+{date_end}]+AND+device.manufacturer_d_name:' \
          '{manufacturer}&count=device.generic_name.exact&limit={num}&skip=0'\
        .format(openFDA=openFDA, api_endpoint=api_endpoint, api_key=api_key,
                date_start=start, date_end=end, manufacturer=manufacturer, num=10)
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


if __name__ == '__main__':
    cache.clear()
    port = int(os.environ.get('PORT', 5000))
    app.run_server(debug=debug, port=port, threaded=True)
