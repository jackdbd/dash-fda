import requests
import pandas as pd
from flask import json


def get_results(url):
    response = requests.get(url)
    if response.ok:
        d = json.loads(response.text)
        results = d['results']
    else:
        results = []
    return results


def get_meta(url):
    response = requests.get(url)
    d = json.loads(response.text)
    return d['meta']


def create_intermediate_df(url):
    results = get_results(url)
    df = pd.DataFrame(results)
    # do not do anything more because datetime is not serializable
    return df


def unjsonify(jsonified_divs, id_div):
    jsonified_df = [d['props']['children'] for d in jsonified_divs
                    if d['props']['id'] == id_div][0]
    d = json.loads(jsonified_df)
    df = pd.DataFrame(d)
    return df
