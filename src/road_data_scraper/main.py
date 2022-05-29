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


def run(config: dict, api_run: bool):
    """
    Runs the Pipeline to Scrape Road Traffic Sensor Data
    from Highways England WebTRIS API.

    Args:
        config (dict): Configuration file for this run.
        api_run (bool): True if using FastAPI for this run.
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
            gcp_bucket_name=my_ast(config["user_settings"]["gcp_bucket_name"]),
            gcp_folder_name=my_ast(config["user_settings"]["gcp_blob_name"]),
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
