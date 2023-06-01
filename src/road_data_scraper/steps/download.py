"""
Download Module
---------------
This module is designed for scraping data from the WebTRIS Highways England API. It includes functionalities for data downloading in parallel,
handling HTTP responses, converting the JSON response to a Pandas DataFrame, and appending the data to a CSV file.

The module employs several concurrent programming concepts like threading, multiprocessing, and concurrent futures. The main function `download` uses ThreadPoolExecutor
for parallel requests to increase the efficiency of the scraping process.

List of classes, dataclasses, and functions:
---------------------------------------------

1. DataClass: UrlMetadata:
    Represents the metadata of a URL that includes details like site_id, site_type, geographical coordinates, etc.

2. Function: _get_headers():
    Returns the list of headers used for creating the CSV file.

3. Function: _response_to_df(response, metadata: UrlMetadata):
    Converts the response JSON object into a pandas DataFrame and adds additional metadata/columns to it.

4. Function: get_url(site_name: str, start_date: str, end_date: str, test_run: bool, full_csv_name: str, metadata: UrlMetadata, total_urls: int):
    Responsible for scraping a URL from the WebTRIS Highways endpoint and logging the progress. It also handles request failures and server overloads.

5. Function: download(site_name: str, start_date: str, end_date: str, metadata: list[tuple], test_run: bool, run_id_path: Path):
    Main function responsible for initiating the scraping process. It takes in details about the site name, date range, metadata, etc., and executes the process in parallel.

Imported Libraries:
-------------------
- csv: For handling CSV file operations.
- logging: For logging details about the progress and errors.
- multiprocessing: For getting the number of CPUs on the current machine.
- threading: For handling locks and concurrent programming.
- time: For introducing sleep time.
- concurrent.futures: For ThreadPoolExecutor for parallel processing.
- dataclasses: For creating a data class that holds metadata about the URL.
- itertools: For repeating certain variables the same number of times as there are URLs.
- pathlib: For handling the file path.
- pandas as pd: For creating dataframes and handling data.
- requests: For sending HTTP requests.

Global Variables:
-----------------
- THREAD_POOL: Number of threads for ThreadPoolExecutor, equals the number of CPUs on the current machine.
- session: A session of HTTP requests.
- LOGGER: Logging object for logging progress and errors.
- COUNTER_LOCK: A lock to handle the COUNTER variable in concurrent programming.
- COUNTER: A counter to keep track of processed URLs.
"""

import csv
import logging
import multiprocessing
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
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

COUNTER_LOCK = threading.Lock()
COUNTER = 0


@dataclass(frozen=True)
class UrlMetadata:
    url: str
    site_id: str
    site_type: str
    direction: str
    longitude: str
    latitude: str
    status: str
    easting: str
    northing: str
    """
    A class used to represent the metadata of a URL.

    Attributes
    ----------
    url : str
        The URL to be scraped.
    site_id : str
        The unique ID of the road traffic sensor.
    site_type : str
        The type of the road traffic sensor, e.g., 'midas', 'tmu', 'tame'.
    direction : str
        The direction of the road traffic sensor.
    longitude : str
        The longitude of the road traffic sensor.
    latitude : str
        The latitude of the road traffic sensor.
    status : str
        The status of the road traffic sensor.
    easting : str
        The easting of the road traffic sensor.
    northing : str
        The northing of the road traffic sensor.
    """


def _get_headers() -> list[str]:
    """
    Returns a list of headers that are used to create a CSV file of data
    downloaded from the Highways England WebTRIS API. These headers correspond
    to the columns of the CSV file.

    The headers include information like the unique site ID, site name,
    report date, time period, speed intervals, vehicle length intervals,
    average speed, total volume, geographical information and status of
    the Road Traffic Sensor.

    Returns:
        list[str]: A list of strings, where each string is a header name.
    """
    return [
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
        "sites_status",
        "type",
        "direction",
        "easting",
        "northing",
    ]


def _response_to_df(response, metadata: UrlMetadata):
    """
    Converts JSON stored `requests` response object to a Pandas DataFrame.
    Then adds additional metadata/columns to the DataFrame using an instance of UrlMetadata.

    Args:
        response (requests.Response): `requests` response object.
        metadata (UrlMetadata): An instance of UrlMetadata containing the metadata for a URL.

    Returns:
        df (pd.DataFrame): Pandas DataFrame.
    """

    df = pd.DataFrame.from_dict(response.json()["Rows"])

    df.insert(0, "site_id", metadata.site_id)

    df = df.assign(
        longitude=metadata.longitude,
        latitude=metadata.latitude,
        sites_status=metadata.status,
        type=metadata.site_type,
        direction=metadata.direction,
        easting=metadata.easting,
        northing=metadata.northing,
    )

    return df


def get_url(
    site_name: str,
    start_date: str,
    end_date: str,
    test_run: bool,
    full_csv_name: str,
    metadata: UrlMetadata,
    total_urls: int,
):
    """
    Scrapes a URL from WebTRIS Highways /reports/daily/ endpoint as a Pandas DataFrame,
    appends the DataFrame to a CSV, and logs progress.

    Args:
        site_name (str): The name of the road traffic sensor.
        start_date (str): The start date in the format %Y-%m-%d.
        end_date (str): The end date in the format %Y-%m-%d.
        test_run (bool): If True, will only download a small subset data from WebTRIS Highways England API.
        full_csv_name (str): The output CSV file path.
        metadata (UrlMetadata): An instance of UrlMetadata containing the metadata for a URL.
        total_urls (int): The total number of URLs to be processed.

    Returns:
        response: The HTTP response received when accessing the URL.
    """
    global COUNTER

    message = "Parallel request of data for use in ONS. Emerging Platforms Team. @GitHub: dombean/road_data_scraper"
    headers = {"Message": f"{message}"}

    response = session.get(metadata.url, headers=headers)

    with COUNTER_LOCK:
        COUNTER += 1
        remaining = total_urls - COUNTER
        log_interval = max(
            1, total_urls // 10
        )  # log after processing about 10% of the URLs, but at least once

        if COUNTER % log_interval == 0 or COUNTER == total_urls:
            LOGGER.info(
                f"Processed {COUNTER} URLs. Remaining: {remaining}. Last request was completed in {response.elapsed.total_seconds()} seconds. [{response.url}]"
            )

    df = _response_to_df(response=response, metadata=metadata)

    df.to_csv(f"{full_csv_name}", mode="a", header=False, index=False)

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
    metadata: list[tuple],
    test_run: bool,
    run_id_path: Path,
):
    """
    Scrapes data from Highways England WebTRIS API in parallel.

    Args:
        site_name (str): The name of the road traffic sensor.
        start_date (str): The start date in the format %Y-%m-%d.
        end_date (str): The end date in the format %Y-%m-%d.
        metadata (list[tuple]): A list of tuples. Each tuple contains a URL and associated metadata
                                for a road traffic sensor.
        test_run (bool): If True, will only download a small subset data from WebTRIS Highways England API.
        run_id_path (Path): A Path object to the run_id directory.
    """

    LOGGER.info(f"Downloading {site_name} URLs.")

    if site_name not in ("midas", "tame", "tmu"):
        raise ValueError("Available sites are: midas, tame, tmu.")

    if test_run:
        full_csv_name = (
            f"{str(run_id_path)}/{site_name}_{start_date}-{end_date}_TEST_RUN.csv"
        )
    else:
        full_csv_name = f"{str(run_id_path)}/{site_name}_{start_date}-{end_date}.csv"

    with open(full_csv_name, "w") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=_get_headers())
        writer.writeheader()

    total_urls = len(metadata)
    url_metadata_list = [UrlMetadata(*item) for item in metadata]

    with ThreadPoolExecutor(max_workers=THREAD_POOL) as executor:
        executor.map(
            get_url,
            repeat(site_name),
            repeat(start_date),
            repeat(end_date),
            repeat(test_run),
            repeat(full_csv_name),
            url_metadata_list,
            repeat(total_urls),
        )

    LOGGER.info(f"Finish Downloading {site_name} URLs.")
