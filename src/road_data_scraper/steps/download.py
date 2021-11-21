import csv
import logging
import multiprocessing
import time
from concurrent.futures import ThreadPoolExecutor
from itertools import repeat

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
    site_name,
    start_date,
    end_date,
    test_run,
    full_csv_name,
    url,
    direction,
    longitude,
    latitude,
    status,
    easting,
    northing,
):

    message = "Parallel request of data for use in ONS. Emerging Platforms Team. @GitHub: dombean/road_data_scraper"

    headers = {"Message": f"{message}"}

    response = session.get(url, headers=headers)

    logging.info(
        f"request was completed in {response.elapsed.total_seconds()} seconds [{site_name}] [{response.url}]"
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


def download(site_name, start_date, end_date, metadata, test_run, run_id_path):

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
