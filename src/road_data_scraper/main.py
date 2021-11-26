import ast
import configparser
import logging
import shutil
import time
from pathlib import Path

from rich.logging import RichHandler

from road_data_scraper.report.report import run_reports
from road_data_scraper.steps.download import THREAD_POOL, download
from road_data_scraper.steps.file_handler import (
    dump_config,
    file_handler,
    gcp_upload_from_directory,
)
from road_data_scraper.steps.metadata import get_site_urls, get_sites_by_sensor

logging.basicConfig(
    format="%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[RichHandler()],
)


def run(config):

    start_time = time.time()

    logging.info(f"Using {THREAD_POOL} threads")

    data_path, metadata_path, report_path, run_id_path = file_handler(config)

    logging.getLogger().addHandler(
        logging.FileHandler(f"{metadata_path}/road_data_pipeline.log")
    )

    start_date = ast.literal_eval(config["user_settings"]["start_date"])
    end_date = ast.literal_eval(config["user_settings"]["end_date"])
    test_run = ast.literal_eval(config["user_settings"]["test_run"])
    generate_report = ast.literal_eval(config["user_settings"]["generate_report"])

    logging.info("Getting Road Sensor Lookup Table")

    sensor_tables, lookup_df = get_sites_by_sensor()
    lookup_df.to_csv(f"{str(metadata_path)}/road_data_sensor_lookup.csv", index=False)

    midas_metadata, tmu_metadata, tame_metadata = get_site_urls(
        sensor_tables, start_date, end_date
    )

    logging.info("Processed Road Sensor Lookup Table")

    if test_run:
        logging.info("Test Run")
        midas_metadata = midas_metadata[1:2]
        tmu_metadata = tmu_metadata[1:2]
        tame_metadata = tame_metadata[1:2]

    download(
        site_name="midas",
        start_date=start_date,
        end_date=end_date,
        metadata=midas_metadata,
        test_run=test_run,
        run_id_path=data_path,
    )

    download(
        site_name="tmu",
        start_date=start_date,
        end_date=end_date,
        metadata=tmu_metadata,
        test_run=test_run,
        run_id_path=data_path,
    )

    download(
        site_name="tame",
        start_date=start_date,
        end_date=end_date,
        metadata=tame_metadata,
        test_run=test_run,
        run_id_path=data_path,
    )

    if generate_report:
        run_reports(lookup_df, report_path, start_date, end_date)

    dump_config(config, metadata_path)

    gcp_storage = ast.literal_eval(config["user_settings"]["gcp_storage"])

    if gcp_storage:

        gcp_bucket_name = ast.literal_eval(config["user_settings"]["gcp_bucket_name"])
        gcp_folder_name = ast.literal_eval(config["user_settings"]["gcp_blob_name"])
        gcp_credentials = ast.literal_eval(config["user_settings"]["gcp_credentials"])

        gcp_upload_from_directory(
            run_id_path, gcp_bucket_name, gcp_folder_name, gcp_credentials
        )

    rm_dir = ast.literal_eval(config["user_settings"]["rm_dir"])

    if rm_dir:
        logging.info(
            f"Removing {run_id_path[run_id_path.find('output_data/'):].split('/')[1]} folder."
        )
        shutil.rmtree(Path(run_id_path))

    logging.info(f"Script Run Time: {(time.time() - start_time)/60} minutes.")


if __name__ == "__main__":

    config = configparser.ConfigParser()
    config.read("./config.ini")

    run(config)
