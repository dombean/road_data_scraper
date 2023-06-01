"""
Metadata Module
---------------
This module is primarily used to generate metadata for the road traffic sensor data scraping pipeline. It interacts
with the Highways England WebTRIS API to fetch sensor data and create relevant metadata including sensor URLs.

The module provides several functions:

    - create_sensor_metadata_tuples: Creates tuples of sensor metadata including sensor URL and other sensor details.
    - get_sensor_urls: Generates URLs for the road sensors (MIDAS, TAME, TMU) and packs each URL with other sensor
        metadata into a tuple.
    - direction_string_cleaner: Cleans the direction data string.
    - name_string_cleaner: Cleans the sensor name string.
    - get_sites_by_sensor: Fetches and processes sensor data from the API to generate metadata.

Constants:
----------
    BASE_URL (str): Base URL for the Highways England WebTRIS API.
"""
import datetime
from functools import partial

import pandas as pd
import requests

BASE_URL = "https://webtris.highwaysengland.co.uk/api/v1/"


def create_sensor_metadata_tuples(
    sensor_tables: dict[str, pd.DataFrame],
    start_date: str,
    end_date: str,
    sensor_name: str = None,
) -> list[tuple[str, int, str, str, float, float, str, float, float]]:
    """
    Generates metadata tuples for specific road traffic sensor based on the given sensor name.

    This function constructs the URL for accessing the sensor data and combines it with various
    sensor metadata to form a tuple. The list of these tuples for all sensors of the specified
    type is then returned.

    Args:
        sensor_tables (dict): A dictionary mapping sensor names (midas, tame, tmu) to their corresponding
            metadata stored in pandas DataFrame.
        start_date (str): Start date in the format 'YYYY-MM-DD'.
        end_date (str): End date in the format 'YYYY-MM-DD'.
        sensor_name (str, optional): The name of the sensor for which metadata tuples are to be created.
            Should be one of 'midas', 'tame', or 'tmu'. Defaults to None.

    Raises:
        ValueError: If sensor_name is not 'midas', 'tame' or 'tmu'.

    Returns:
        sensor_metadata (list[tuple]): List of tuples, each containing metadata of a sensor.
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


def get_sensor_urls(
    sensor_tables: dict[str, pd.DataFrame], start_date: str, end_date: str
) -> tuple[
    list[tuple[str, int, str, str, float, float, str, float, float]],
    list[tuple[str, int, str, str, float, float, str, float, float]],
    list[tuple[str, int, str, str, float, float, str, float, float]],
]:
    """
    Generates URLs and associated metadata for all road sensors: MIDAS, TAME, TMU.

    This function uses the create_sensor_metadata_tuples function to create metadata tuples
    for all types of sensors.

    Args:
        sensor_tables (dict): A dictionary mapping sensor names (midas, tame, tmu) to their corresponding
            metadata stored in pandas DataFrame.
        start_date (str): Start date in the format 'YYYY-MM-DD'.
        end_date (str): End date in the format 'YYYY-MM-DD'.

    Returns:
        tuple[list]: Three lists containing metadata tuples for MIDAS, TMU, and TAME sensors respectively.
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


def direction_string_cleaner(record: str) -> str:
    """
    Cleans a string in the "direction" column of the sensor metadata.

    Based on some predetermined rules, the function assigns a cleaned version of the direction string.

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


def name_string_cleaner(record: str) -> str:
    """
    Cleans a string in the "name" column of the sensor metadata.

    The function checks if certain substrings are in the original string and replaces the original
    string with a cleaned version based on that.

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


def get_sites_by_sensor() -> tuple[dict[str, pd.DataFrame], pd.DataFrame]:
    """
    Retrieves site metadata from the Highways England WebTRIS API.

    This function sends a GET request to the API and processes the response into a Pandas DataFrame.
    The function also performs data cleaning operations on the "name" and "direction" columns.

    Returns:
        sensor_tables (dict[pd.DataFrame]): A dictionary mapping sensor names to their respective metadata DataFrames.
        lookup_df (pd.DataFrame): A DataFrame containing metadata for all road traffic sensors.
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
