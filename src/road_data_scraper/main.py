"""
Main Module
-----------
This module contains the main driver function for the road traffic data scraping pipeline. 

It interfaces with the necessary sub-modules and coordinates the pipeline's stages.
"""
import ast
import calendar
import configparser
import logging
import shutil
import time
from datetime import datetime
from functools import partial
from pathlib import Path

from dateutil.relativedelta import relativedelta

from road_data_scraper import TMP_LOG_PATH
from road_data_scraper.report.report import run_reports
from road_data_scraper.steps.download import THREAD_POOL, download
from road_data_scraper.steps.file_handler import (
    dump_config,
    file_handler,
    gcp_upload_from_directory,
)
from road_data_scraper.steps.metadata import get_sensor_urls, get_sites_by_sensor

LOGGER = logging.getLogger(__name__)


def run(config: dict, api_run: bool) -> None:
    """
    Orchestrates the execution of a web scraping pipeline that extracts Road Traffic Sensor Data
    from the Highways England WebTRIS API. It handles various stages including configuration setup,
    data fetching, report generation, and optional actions such as data upload to a Google Cloud
    Platform bucket and directory removal.

    Args:
        config (dict): Configuration file containing various settings for the pipeline run.
            Contains settings such as start and end dates, the number of threads to use,
            test run flag, report generation flag, and details for Google Cloud Storage, etc.

        api_run (bool): Flag indicating whether the pipeline is being run through the FastAPI
            framework. Affects how certain configuration settings are processed.

    The function also interacts with several other functions to accomplish its task:
        1. It uses the `file_handler` function to create necessary directories.
        2. It uses `get_sites_by_sensor` and `get_sensor_urls` to fetch sensor data.
        3. It calls the `download` function to download sensor data.
        4. If configured, it uses the `run_reports` function to generate reports.
        5. It uses `dump_config` to save the configuration file to metadata.
        6. If configured, it uses `gcp_upload_from_directory` to upload data to Google Cloud.
        7. Finally, if configured, it removes the run directory.

    Returns:
        None. This function performs operations but does not return any value. It manages the
        web scraping pipeline including data fetching, report generation, data uploading and
        directory cleanup.

    Raises:
        ValueError: If the output directory in config is not valid, it's raised by `file_handler`.
        Various exceptions can also be raised during downloading, report generation, and GCP upload stages.

    Example usage:
        >>> config = configparser.ConfigParser()
        >>> config.read("./config.ini")
        >>> run(config, api_run=False)
    """
    start_time = time.time()

    if api_run:

        def my_ast(*args):
            return args[0]

    else:

        def my_ast(*args):
            return ast.literal_eval(*args)

    start_date = my_ast(config["user_settings"]["start_date"])
    end_date = my_ast(config["user_settings"]["end_date"])

    if not start_date and not end_date:

        # 2-month API data lag (date today minus two months)
        date_object_today = datetime.strptime(time.strftime("%Y-%m"), "%Y-%m")
        minus_two_months = date_object_today - relativedelta(months=2)

        year, month = map(int, minus_two_months.strftime("%Y %m").split())
        last_day_of_month = calendar.monthrange(year, month)[1]

        start_date = f"{year}-{month}-01"
        end_date = f"{year}-{month}-{last_day_of_month}"

    data_path, metadata_path, report_path, run_id_path = file_handler(
        config, api_run, start_date, end_date
    )

    LOGGER.info(f"Using {THREAD_POOL} threads")

    test_run = my_ast(config["user_settings"]["test_run"])
    generate_report = my_ast(config["user_settings"]["generate_report"])

    LOGGER.info("Getting Road Sensor Lookup Table")

    sensor_tables, lookup_df = get_sites_by_sensor()
    lookup_df.to_csv(f"{str(metadata_path)}/road_data_sensor_lookup.csv", index=False)

    midas_metadata, tmu_metadata, tame_metadata = get_sensor_urls(
        sensor_tables, start_date, end_date
    )

    LOGGER.info("Processed Road Sensor Lookup Table")

    if test_run:
        LOGGER.info("Test Run")
        midas_metadata = midas_metadata[1:2]
        tmu_metadata = tmu_metadata[1:2]
        tame_metadata = tame_metadata[1:2]

    download_partial = partial(
        download,
        start_date=start_date,
        end_date=end_date,
        test_run=test_run,
        run_id_path=data_path,
    )

    download_partial(site_name="midas", metadata=midas_metadata)
    download_partial(site_name="tmu", metadata=tmu_metadata)
    download_partial(site_name="tame", metadata=tame_metadata)

    if generate_report:
        run_reports(lookup_df, report_path, start_date, end_date)

    if api_run:
        dump_config(config, metadata_path, api_run=True)
    else:
        dump_config(config, metadata_path, api_run=False)

    LOGGER.info(f"Script Run Time: {round((time.time() - start_time)/60, 2)} minutes")

    log_file_path = f"{metadata_path}/road_data_pipeline.log"
    shutil.copyfile(TMP_LOG_PATH, log_file_path)

    gcp_storage = my_ast(config["user_settings"]["gcp_storage"])
    if gcp_storage:
        gcp_upload_from_directory(
            run_id_path,
            destination_bucket_name=my_ast(config["user_settings"]["gcp_bucket_name"]),
            destination_blob_name=my_ast(config["user_settings"]["gcp_blob_name"]),
            gcp_credentials=my_ast(config["user_settings"]["gcp_credentials"]),
        )

    rm_dir = my_ast(config["user_settings"]["rm_dir"])
    if rm_dir:
        LOGGER.info(
            f"Removing {run_id_path[run_id_path.find('output_data/'):].split('/')[1]} folder"
        )
        shutil.rmtree(Path(run_id_path))


if __name__ == "__main__":

    config = configparser.ConfigParser()
    config.read("./config.ini")

    run(config, api_run=False)
