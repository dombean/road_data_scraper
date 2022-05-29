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

LOGGER = logging.getLogger(__name__)


def get(
    site_name: str,
    start_date: str,
    end_date: str,
    test_run: bool,
    full_csv_name: str,
    url: str,
    site_id: str,
    site_type: str,
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
        site_id (str): Unique ID of Road Traffic Sensor.
        site_type (str): Road Traffic Sensor Type: midas, tmu, tame.
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

    LOGGER.info(
        f"Request was completed in {response.elapsed.total_seconds()} seconds [{site_name}] [{response.url}]"
    )

    dataframe = pd.DataFrame.from_dict(response.json()["Rows"])
    dataframe.insert(0, "site_id", site_id)

    dataframe = dataframe.assign(
        longitude=longitude,
        latitude=latitude,
        status=status,
        type=site_type,
        direction=direction,
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
        "site_id",
        "site_name",
        "report_date",
        "time_period_end",
        "interval",
        "len_0_520_cm",
        "len_521_660_cm",
        "len_661_1160_cm",
        "len_1160_plus_cm",
        "speed_0_10_mph",
        "speed_11_15_mph",
        "speed_16_20_mph",
        "speed_21_25_mph",
        "speed_26_30_mph",
        "speed_31_35_mph",
        "speed_36_40_mph",
        "speed_41_45_mph",
        "speed_46_50_mph",
        "speed_51_55_mph",
        "speed_56_60_mph",
        "speed_61_70_mph",
        "speed_71_80_mph",
        "speed_80_plus_mph",
        "speed_avg_mph",
        "total_vol",
        "longitude",
        "latitude",
        "status",
        "type",
        "direction",
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

    (
        url,
        site_id,
        site_type,
        direction,
        longitude,
        latitude,
        status,
        easting,
        northing,
    ) = zip(*metadata)

    with ThreadPoolExecutor(max_workers=THREAD_POOL) as executor:
        executor.map(
            get,
            repeat(site_name),
            repeat(start_date),
            repeat(end_date),
            repeat(test_run),
            repeat(full_csv_name),
            url,
            site_id,
            site_type,
            direction,
            longitude,
            latitude,
            status,
            easting,
            northing,
        )
