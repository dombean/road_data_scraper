import datetime

import pandas as pd
import requests


def get_site_urls(sensor_tables, start_date, end_date):

    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").strftime("%d%m%Y")
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").strftime("%d%m%Y")

    midas_id = list(sensor_tables["midas"]["id"])
    midas_urls = [
        f"https://webtris.highwaysengland.co.uk/api/v1/reports/{start_date}/to/{end_date}/daily?sites={site}&page=1&page_size=40000"
        for site in midas_id
    ]

    midas_direction = sensor_tables["midas"]["direction"]
    midas_longitude = sensor_tables["midas"]["longitude"]
    midas_latitude = sensor_tables["midas"]["latitude"]
    midas_status = sensor_tables["midas"]["status"]
    midas_easting = sensor_tables["midas"]["easting"]
    midas_northing = sensor_tables["midas"]["northing"]

    midas_metadata = list(
        zip(
            midas_urls,
            midas_direction,
            midas_longitude,
            midas_latitude,
            midas_status,
            midas_easting,
            midas_northing,
        )
    )

    tmu_id = list(sensor_tables["tmu"]["id"])
    tmu_urls = [
        f"https://webtris.highwaysengland.co.uk/api/v1/reports/{start_date}/to/{end_date}/daily?sites={site}&page=1&page_size=40000"
        for site in tmu_id
    ]

    tmu_direction = sensor_tables["tmu"]["direction"]
    tmu_longitude = sensor_tables["tmu"]["longitude"]
    tmu_latitude = sensor_tables["tmu"]["latitude"]
    tmu_status = sensor_tables["tmu"]["status"]
    tmu_easting = sensor_tables["tmu"]["easting"]
    tmu_northing = sensor_tables["tmu"]["northing"]

    tmu_metadata = list(
        zip(
            tmu_urls,
            tmu_direction,
            tmu_longitude,
            tmu_latitude,
            tmu_status,
            tmu_easting,
            tmu_northing,
        )
    )

    tame_id = list(sensor_tables["tame"]["id"])
    tame_urls = [
        f"https://webtris.highwaysengland.co.uk/api/v1/reports/{start_date}/to/{end_date}/daily?sites={site}&page=1&page_size=40000"
        for site in tame_id
    ]

    tame_direction = sensor_tables["tame"]["direction"]
    tame_longitude = sensor_tables["tame"]["longitude"]
    tame_latitude = sensor_tables["tame"]["latitude"]
    tame_status = sensor_tables["tame"]["status"]
    tame_easting = sensor_tables["tame"]["easting"]
    tame_northing = sensor_tables["tame"]["northing"]

    tame_metadata = list(
        zip(
            tame_urls,
            tame_direction,
            tame_longitude,
            tame_latitude,
            tame_status,
            tame_easting,
            tame_northing,
        )
    )

    return midas_metadata, tmu_metadata, tame_metadata


def status_string_cleaner(x):
    if "eastbound" in str(x):
        return "eastbound"
    elif "northbound" in str(x):
        return "northbound"
    elif "southbound" in str(x):
        return "southbound"
    elif "westbound" in str(x):
        return "westbound"
    elif "clockwise" in str(x):
        return "clockwise"
    elif "anti-clockwise" in str(x):
        return "clockwise"
    elif "legacy site" in str(x):
        return "legacy site"
    elif "on connector" in str(x):
        return "carriageway connector"
    else:
        return x


def name_string_cleaner(x):
    if "MIDAS" in str(x):
        return "MIDAS"
    elif "TMU" in str(x):
        return "TMU"
    elif "TAME" in str(x):
        return "TAME"
    elif "Legacy Site" in str(x):
        return "Legacy Site"
    else:
        return x


def get_sites_by_sensor():

    url = "https://webtris.highwaysengland.co.uk/api/v1/sites"
    response = requests.get(url)

    lookup_df = pd.DataFrame.from_dict(response.json()["sites"])
    lookup_df.columns = [col.lower() for col in lookup_df.columns]
    lookup_df["id"] = lookup_df["id"].astype(int)

    lookup_df["direction"] = lookup_df["name"].str.split("; ").str[-1]
    lookup_df[["easting", "northing"]] = (
        lookup_df["name"].str.extract(r"(\d+;\d+)")[0].str.split(";", expand=True)
    )

    lookup_df["direction"] = lookup_df["direction"].str.lower()
    lookup_df["direction"] = lookup_df["direction"].apply(status_string_cleaner)

    lookup_df["name"] = lookup_df["name"].apply(name_string_cleaner)

    midas_df = lookup_df.query("name.str.contains('MIDAS', case = True)")
    tmu_df = lookup_df.query("name.str.contains('TMU', case = True)")
    tame_df = lookup_df.query("name.str.contains('TAME', case = True)")
    other_df = lookup_df.query(
        "name.str.contains('MIDAS|TAME|TMU', case = True)==False"
    )

    sensor_tables = {
        "midas": midas_df,
        "tmu": tmu_df,
        "tame": tame_df,
        "other": other_df,
    }

    return sensor_tables, lookup_df
