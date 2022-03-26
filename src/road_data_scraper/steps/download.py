import csv
import logging
import multiprocessing
import time
from concurrent.futures import ThreadPoolExecutor
from itertools import repeat
from pathlib import Path

import pandas as pd
import requests

THREAD_POOL = multiprocessing.cpu_count()

session = requests.Session()
session.mount(
    "https://",
    requests.adapters.HTTPAdapter(
        pool_maxsize=THREAD_POOL, max_retries=3, pool_block=True
    ),
)


def get(
    site_name: str,
    start_date: str,
    end_date: str,
    test_run: bool,
    full_csv_name: str,
    url: str,
    direction: str,
    longitude: str,
    latitude: str,
    status: str,
    easting: str,
    northing: str,
):
    """
    Downloads a URL from WebTRIS Highways /reports/daily/ endpoint.

    Args:
        site_name (str): Road Traffic Sensor Name.
        start_date (str): Start Date; format: %Y-%m-%d.
        end_date (str): End Date; format: %Y-%m-%d.
        test_run (bool): If True, will only download a small subset data from WebTRIS Highways England API.
        full_csv_name (str): Output CSV File Path.
        url (str): URL of Road Traffic Sensor for a given Site ID.
        direction (str): Direction of Road Traffic Sensor for a given Site ID.
        longitude (str): Longitude of Road Traffic Sensor for a given Site ID.
        latitude (str): Latitude of Road Traffic Sensor for a given Site ID.
        status (str): Status of Road Traffic Sensor for a given Site ID.
        easting (str): Easting of Road Traffic Sensor for a given Site ID.
        northing (str): Northing of Road Traffic Sensor for a given Site ID.

    Returns:
        _type_: _description_
    """

    message = "Parallel request of data for use in ONS. Emerging Platforms Team. @GitHub: dombean/road_data_scraper"
    headers = {"Message": f"{message}"}

    response = session.get(url, headers=headers)

    logging.info(
        f"Request was completed in {response.elapsed.total_seconds()} seconds [{site_name}] [{response.url}]"
    )

    dataframe = pd.DataFrame.from_dict(response.json()["Rows"])

    dataframe = dataframe.assign(
        direction=direction,
        longitude=longitude,
        latitude=latitude,
        status=status,
        easting=easting,
        northing=northing,
    )

    dataframe.to_csv(f"{full_csv_name}", mode="a", header=False, index=False)

    if response.status_code != 200:
        logging.error(
            "request failed, error code %s [%s]", response.status_code, response.url
        )

    if 500 <= response.status_code < 600:
        # server is overloaded? give it a break
        time.sleep(5)

    return response


def download(
    site_name: str,
    start_date: str,
    end_date: str,
    metadata: pd.DataFrame,
    test_run: bool,
    run_id_path: Path,
):
    """
    Scrapes data from Highways England WebTRIS API
    in Parallel.

    Args:
        site_name (str): Name of Road Traffic Sensor.
        start_date (str): Start Date; format: %Y-%m-%d.
        end_date (str): End Date; format: %Y-%m-%d.
        metadata (pd.DataFrame): Pandas DataFrame containing Metadata regarding a Road
        Traiff Sensor.
        test_run (bool): If True, will only download a small subset data from WebTRIS Highways England API.
        run_id_path (Path): Path object to run_id directory.
    """

    if site_name not in ("midas", "tame", "tmu"):
        raise ValueError("Available sites are: midas, tame, tmu.")

    headers = [
        "site_name",
        "report_date",
        "time_period_ending",
        "time_interval",
        "0_520_cm",
        "521_660_cm",
        "661_1160_cm",
        "1160+_cm",
        "0_10_mph",
        "11_15_mph",
        "16_20_mph",
        "21_25_mph",
        "26_30_mph",
        "31_35_mph",
        "36_40_mph",
        "41_45_mph",
        "46_50_mph",
        "51_55_mph",
        "56_60_mph",
        "61_70_mph",
        "71_80_mph",
        "80_plus_mph",
        "avg_mph",
        "total_volume",
        "direction",
        "longitude",
        "latitude",
        "status",
        "easting",
        "northing",
    ]

    if test_run:
        full_csv_name = (
            f"{str(run_id_path)}/{site_name}_{start_date}-{end_date}_TEST_RUN.csv"
        )
    else:
        full_csv_name = f"{str(run_id_path)}/{site_name}_{start_date}-{end_date}.csv"

    with open(full_csv_name, "w") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()

    url, direction, longitude, latitude, status, easting, northing = zip(*metadata)

    with ThreadPoolExecutor(max_workers=THREAD_POOL) as executor:
        executor.map(
            get,
            repeat(site_name),
            repeat(start_date),
            repeat(end_date),
            repeat(test_run),
            repeat(full_csv_name),
            url,
            direction,
            longitude,
            latitude,
            status,
            easting,
            northing,
        )
