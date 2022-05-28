import datetime
from functools import partial

import pandas as pd
import requests

BASE_URL = "https://webtris.highwaysengland.co.uk/api/v1/"


def create_sensor_metadata_tuples(
    sensor_tables: dict, start_date: str, end_date: str, sensor_name: str = None
):
    """
    Helper Function that returns a list of tuples containing metadata
    regarding a particular Road Traffic Sensor URL/Site ID.

    Args:
        sensor_tables (Dict[pd.DataFrame]): Keyed by the name of the Road Traffic Sensor,
        values are Pandas DataFrames containing Metadata regarding each Traffic Sensor.
        start_date (str): Start Date; format: %Y-%m-%d.
        end_date (str): End Date; format: %Y-%m-%d.

    Returns:
        sensor_metadata List(tuple): A list containing tuples which holds metadata
        regarding each Road Traffic Sensor URL/Site ID.
    """

    if sensor_name not in ("midas", "tame", "tmu"):
        raise ValueError("Available Sensors are: midas, tame, tmu.")

    sensor_ids = list(sensor_tables[sensor_name]["id"])
    sensor_urls = [
        f"{BASE_URL}reports/{start_date}/to/{end_date}/daily?sites={site}&page=1&page_size=40000"
        for site in sensor_ids
    ]

    sensor_metadata = list(
        zip(
            sensor_urls,
            sensor_tables[sensor_name]["id"],
            sensor_tables[sensor_name]["name"],
            sensor_tables[sensor_name]["direction"],
            sensor_tables[sensor_name]["longitude"],
            sensor_tables[sensor_name]["latitude"],
            sensor_tables[sensor_name]["status"],
            sensor_tables[sensor_name]["easting"],
            sensor_tables[sensor_name]["northing"],
        )
    )
    return sensor_metadata


def get_sensor_urls(sensor_tables: dict, start_date: str, end_date: str):
    """
    Generates URLs for each Road Sensor: MIDAS, TAME, TMU.

    Stores each URL in a tuple alongside the sensor's direction, longitude, latitude,
    status, easting, and northing.

    Args:
        sensor_tables (Dict[pd.DataFrame]): Keyed by the name of the Road Traffic Sensor,
        values are Pandas DataFrames containing Metadata regarding each Traffic Sensor.
        start_date (str): Start Date; format: %Y-%m-%d.
        end_date (str): End Date; format: %Y-%m-%d.

    Returns:
        midas_metadata List(tuple): A list containing tuples which holds metadata for each MIDAS sensor URL.
        tmu_metadata List(tuple): A list containing tuples which holds metadata for each TMU sensor URL.
        tame_metadata List(tuple): A list containing tuples which holds metadata for each TAME sensor URL.
    """

    create_sensor_metadata_tuples_partial = partial(
        create_sensor_metadata_tuples,
        sensor_tables=sensor_tables,
        start_date=datetime.datetime.strptime(start_date, "%Y-%m-%d").strftime(
            "%d%m%Y"
        ),
        end_date=datetime.datetime.strptime(end_date, "%Y-%m-%d").strftime("%d%m%Y"),
    )

    midas_metadata = create_sensor_metadata_tuples_partial(sensor_name="midas")
    tmu_metadata = create_sensor_metadata_tuples_partial(sensor_name="tmu")
    tame_metadata = create_sensor_metadata_tuples_partial(sensor_name="tame")

    return midas_metadata, tmu_metadata, tame_metadata


def direction_string_cleaner(record):
    """
    Pandas Helper Function to clean a record in the "direction" column.

    Args:
        record (str): Strings in "direction" column.

    Returns:
        str: Cleaned string.
    """
    if "eastbound" in str(record):
        return "eastbound"
    elif "northbound" in str(record):
        return "northbound"
    elif "southbound" in str(record):
        return "southbound"
    elif "westbound" in str(record):
        return "westbound"
    elif "clockwise" in str(record):
        return "clockwise"
    elif "anti-clockwise" in str(record):
        return "clockwise"
    elif "legacy site" in str(record):
        return "legacy site"
    elif "on connector" in str(record):
        return "carriageway connector"
    else:
        return record


def name_string_cleaner(record):
    """
    Pandas Helper function to clean "name" column.

    Args:
        record (str): Strings in "name" column.

    Returns:
        str: Cleaned string.
    """
    if "MIDAS" in str(record):
        return "midas"
    elif "TMU" in str(record):
        return "tmu"
    elif "TAME" in str(record):
        return "tame"
    elif "Legacy Site" in str(record):
        return "Legacy Site"
    else:
        return record


def get_sites_by_sensor():
    """
    Queries WebTRIS Highways England /sites/ endpoint.

    Returns:
        sensor_tables (Dict[pd.DataFrame]): Keyed by the name of the Road Traffic Sensor,
        values are Pandas DataFrames containing Metadata regarding each Traffic Sensor.
        lookup_df (pd.DataFrame): Pandas DataFrame containing all Road Traffic Sensors.

    """

    response = requests.get(f"{BASE_URL}sites")

    lookup_df = pd.DataFrame.from_dict(response.json()["sites"])
    lookup_df.columns = [col.lower() for col in lookup_df.columns]
    lookup_df["id"] = lookup_df["id"].astype(int)

    lookup_df["direction"] = lookup_df["name"].str.split("; ").str[-1]
    lookup_df[["easting", "northing"]] = (
        lookup_df["name"].str.extract(r"(\d+;\d+)")[0].str.split(";", expand=True)
    )

    lookup_df["direction"] = lookup_df["direction"].str.lower()
    lookup_df["direction"] = lookup_df["direction"].apply(direction_string_cleaner)

    lookup_df["name"] = lookup_df["name"].apply(name_string_cleaner)

    midas_df = lookup_df.query("name.str.contains('midas', case = True)")
    tmu_df = lookup_df.query("name.str.contains('tmu', case = True)")
    tame_df = lookup_df.query("name.str.contains('tame', case = True)")
    other_df = lookup_df.query(
        "name.str.contains('midas|tmu|tame', case = True)==False"
    )

    sensor_tables = {
        "midas": midas_df,
        "tmu": tmu_df,
        "tame": tame_df,
        "other": other_df,
    }
    return sensor_tables, lookup_df
