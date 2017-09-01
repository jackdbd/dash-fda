import os
import requests
import dash_core_components as dcc
import dash_html_components as html
from flask import Flask, json
from flask_caching import Cache
from dash import Dash
from dash.dependencies import Input, Output
from dotenv import load_dotenv


external_js = []

external_css = []


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
api_key = os.environ.get('API_KEY', 'default-api-key')

app_name = 'Dash FDA'
server = Flask(app_name)
server.secret_key = os.environ.get('SECRET_KEY', 'default-secret-key')
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

app.layout = html.Div(children=[
    html.H1(children=app_name),

    # html.Div([
    #     dcc.Markdown("""
    #         **Hover Data**
    #
    #         Mouse over values in the graph.
    #     """.replace('   ', '')),
    #     html.Pre(id='hover-data', style=styles['pre'])
    # ], style=styles['column']),

    dcc.Markdown("""
    #### Dash and Markdown

    Open FDA API endpoints
    
    - [Devices](https://open.fda.gov/device/)
    - [Drugs](https://open.fda.gov/drug/)
    - [Foods](https://open.fda.gov/food/)

    The API returns individual results as JSON by default. The JSON object has 
    two sections: `meta` and `results`.
    """.replace('   ', '')),

    html.Div([
        html.Label('Manufacturer', id='manufacturer-label'),
        dcc.Dropdown(
            options=[
                {'label': 'Covidien', 'value': 'COVIDIEN'},
                {'label': 'GE Healthcare', 'value': 'GE+Healthcare'},
                {'label': 'Medtronic', 'value': 'MEDTRONIC+MINIMED'},
                {'label': 'Zimmer', 'value': 'ZIMMER+INC.'},
                {'label': 'Baxter', 'value': 'BAXTER+HEALTHCARE+PTE.+LTD.'},
                {'label': 'Smiths Medical', 'value': 'SMITHS+MEDICAL+MD+INC.'},
            ],
            value='GE+Healthcare',
            id='manufacturer-dropdown'
        ),
        html.Div(
            [
                html.Label('From 2007 to 2017', id='time-range-label'),
                dcc.RangeSlider(
                    id='year_slider',
                    min=1991,
                    max=2017,
                    value=[2007, 2017]
                ),
            ],
            style={'margin-top': '20'}
        ),
    ]),

    html.Hr(),

    # create empty figure. It will be updated when _update_graph is triggered
    dcc.Graph(id='graph-fda')
])

# TODO: how to limit the number of API calls triggered by a slider?


@app.callback(
    output=Output('graph-fda', 'figure'),
    inputs=[
        Input('manufacturer-dropdown', 'value'),
        Input('year_slider', 'value')
    ])
@cache.memoize(timeout=30)  # in seconds
def _update_graph(manufacturer, year_range):
    date_start = '{}-01-01'.format(year_range[0])
    date_end = '{}-12-31'.format(year_range[1])
    url = '{openFDA}{api_endpoint}api_key={api_key}&search=date_received:[' \
          '{date_start}+TO+{date_end}]+AND+device.manufacturer_d_name:' \
          '{manufacturer}&count=device.generic_name.exact&limit={num}&skip=0'\
        .format(openFDA=openFDA, api_endpoint=api_endpoint, api_key=api_key,
                date_start=date_start, date_end=date_end,
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
    output=Output('time-range-label', 'children'),
    inputs=[Input('year_slider', 'value')])
def _update_time_range_label(year_range):
    return 'From {} to {}'.format(year_range[0], year_range[1])


if __name__ == '__main__':
    cache.clear()
    port = int(os.environ.get('PORT', 5000))
    app.run_server(debug=debug, port=port, threaded=True)
