import requests
import pandas as pd
from flask import json


def get_results(url):
    response = requests.get(url)
    if response.ok:
        d = json.loads(response.text)
        results = d["results"]
    else:
        results = []
    return results


def get_meta(url):
    response = requests.get(url)
    d = json.loads(response.text)
    return d["meta"]


def create_intermediate_df(url):
    results = get_results(url)
    df = pd.DataFrame(results)
    # do not do anything more because datetime is not serializable
    return df


def unjsonify(state, field):
    """Deserialize a JSON-formatted value, identified by its field in state."""
    return pd.DataFrame(json.loads(state[field]))


def create_years(df):
    """Convert a DataFrame in a grouped DataFrame, by year.

    In order to group by week, year, etc later on, we need to create a datetime
    variable now and set it as an index (because DataFrame.resample needs a
    DatetimeIndex).
    """
    df["date"] = pd.to_datetime(df["time"])
    df.set_index(df["date"], inplace=True)
    # we don't need the original 'time' column any longer, so we can drop it.
    df.drop(["time"], axis=1, inplace=True)

    dfr = df.resample("Y").sum()
    dfr["year"] = dfr.index.strftime("%Y")
    grouped = dfr.groupby("year")
    dframe = grouped.sum()
    return dframe


def create_months(df):
    """Convert a DataFrame in a grouped DataFrame, by month.

    In order to group by week, year, etc later on, we need to create a datetime
    variable now and set it as an index (because DataFrame.resample needs a
    DatetimeIndex).
    """
    df["date"] = pd.to_datetime(df["time"])
    df.set_index(df["date"], inplace=True)
    # we don't need the original 'time' column any longer, so we can drop it.
    df.drop(["time"], axis=1, inplace=True)

    dfr = df.resample("M").sum()
    dfr["month"] = dfr.index.strftime("%B")
    # don't sort alphabetically
    grouped = dfr.groupby("month", sort=False)
    dframe = grouped.sum()

    # We now have a DataFrame grouped by month of the year, but not necessarily
    # sorted as we would like to have it: [January, February, ..., December].
    # We can fix this in 4 steps:
    # 1) reset index (in place): 'month' becomes a new column in the DataFrame
    dframe.reset_index(inplace=True)
    # 2) create new column to sort (in place) the records in the DataFrame
    custom_dict = {
        "January": 0,
        "February": 1,
        "March": 2,
        "April": 3,
        "May": 4,
        "June": 5,
        "July": 6,
        "August": 7,
        "September": 8,
        "October": 9,
        "November": 10,
        "December": 11,
    }
    dframe["rank"] = dframe["month"].map(custom_dict)
    dframe.sort_values(by="rank", inplace=True)
    # 3) drop (in place) the column that we have just used for sorting
    dframe.drop(["rank"], axis=1, inplace=True)
    # 4) restore the original index (in place)
    dframe.set_index("month", inplace=True)
    return dframe


def create_days(df):
    # In order to group by week, year, etc later on, we need to create a
    # datetime variable now and set it as an index (because DataFrame.resample
    # needs a DatetimeIndex)
    df["date"] = pd.to_datetime(df["time"])
    df.set_index(df["date"], inplace=True)
    # we don't need the original 'time' column any longer, so we can drop it.
    df.drop(["time"], axis=1, inplace=True)

    dfr = df.resample("D").sum()
    dfr["day"] = dfr.index.strftime("%A")
    # don't sort alphabetically
    grouped = dfr.groupby("day", sort=False)
    dframe = grouped.sum()

    # We now have a DataFrame grouped by weekday, but not necessarily sorted as
    # we would like to have it: [Monday, Tuesday, ..., Sunday].
    # We can fix this in 4 steps:
    # 1) reset index (in place): 'day' becomes a new column in the DataFrame
    dframe.reset_index(inplace=True)
    # 2) create new column to sort (in place) the records in the DataFrame
    custom_dict = {
        "Monday": 0,
        "Tuesday": 1,
        "Wednesday": 2,
        "Thursday": 3,
        "Friday": 4,
        "Saturday": 5,
        "Sunday": 6,
    }
    dframe["rank"] = dframe["day"].map(custom_dict)
    dframe.sort_values(by="rank", inplace=True)
    # 3) drop (in place) the column that we have just used for sorting
    dframe.drop(["rank"], axis=1, inplace=True)
    # 4) restore the original index (in place)
    dframe.set_index("day", inplace=True)
    return dframe


def create_months_box(df):
    # In order to group by week, year, etc later on, we need to create a
    # datetime variable now and set it as an index (because DataFrame.resample
    # needs a DatetimeIndex)
    df["date"] = pd.to_datetime(df["time"])
    df.set_index(df["date"], inplace=True)
    # we don't need the original 'time' column any longer, so we can drop it.
    df.drop(["time"], axis=1, inplace=True)

    dfr = df.resample("M").sum()
    dfr["month"] = dfr.index.strftime("%B")

    months = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]
    dataframes = list()
    for m in months:
        arr = dfr[dfr.month == m]["count"].values
        dff = pd.DataFrame({m: arr})
        dataframes.append(dff)

    dframe = pd.concat(dataframes, axis=1)
    return dframe
