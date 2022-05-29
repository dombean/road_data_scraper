import ast
import datetime
import glob
import logging
import os
from pathlib import Path

from google.cloud import storage

LOGGER = logging.getLogger(__name__)


def file_handler(config: dict, api_run: bool, start_date: str, end_date: str):
    """
    Creates directories to store scraped data and
    returns newly created directories as Path objects.

    Args:
        config (dict): Configuration file for this run.
        api_run (bool): True if using FastAPI for this run.
        start_date (str): Start Date; format: %Y-%m-%d.
        end_date (str): End Date; format: %Y-%m-%d.

    Raises:
        ValueError: If user provides a invalid output directory.

    Returns:
        data_path (Path): Path object to data directory.
        metadata_path (Path): Path object to metadata directory.
        report_path (Path): Path object to report directory.
        run_id_path (Path): Path object to run_id directory.
    """

    run_id = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S.%f")

    start_date_string = datetime.datetime.strptime(start_date, "%Y-%m-%d").strftime(
        "%B-%d-%Y"
    )
    end_date_string = datetime.datetime.strptime(end_date, "%Y-%m-%d").strftime(
        "%B-%d-%Y"
    )

    if api_run:
        user_output_path = config["user_settings"]["output_path"].strip("\"'")
    else:
        user_output_path = ast.literal_eval(config["user_settings"]["output_path"])

    if not user_output_path:
        raise ValueError("Please provide a valid output directory.")

    run_id_path = f"{user_output_path}/output_data/{run_id}_{start_date_string}_to_{end_date_string}/"

    run_id_path_data = Path(f"{run_id_path}data/")
    run_id_path_metadata = Path(f"{run_id_path}metadata/")
    run_id_path_report = Path(f"{run_id_path}report/")

    LOGGER.info(f"Making Data Directory at: {run_id_path_data}")
    run_id_path_data.mkdir(parents=True, exist_ok=True)

    LOGGER.info(f"Making Metadata Directory at: {run_id_path_metadata}")
    run_id_path_metadata.mkdir(parents=True, exist_ok=True)

    LOGGER.info(f"Making Report Directory at: {run_id_path_report}")
    run_id_path_report.mkdir(parents=True, exist_ok=True)

    return run_id_path_data, run_id_path_metadata, run_id_path_report, run_id_path


def dump_config(config: dict, metadata_path: Path, api_run: bool):
    """
    Saves config file to metadata path.

    Args:
        config (dict): Configuration file for this run.
        metadata_path (Path): Path object containing path to metadata output directory.
        api_run (bool): True if using FastAPI for this run.
    """

    LOGGER.info(f"Dumping config.ini for Run at {metadata_path}")

    if api_run:
        config_dict = config
    else:
        config_dict = {
            section: dict(config.items(section)) for section in config.sections()
        }

    with open(f"{str(metadata_path)}/config_metadata.txt", "w") as file:
        print(config_dict, file=file)


def gcp_upload_from_directory(
    directory_path: str,
    destination_bucket_name: str,
    destination_blob_name: str,
    gcp_credentials: str,
):
    """
    Uploads entire output directory for a Pipeline Run
    to a Google Cloud Platform (GCP) Bucket.

    Args:
        directory_path (str): Output directory for Pipeline Run.
        destination_bucket_name (str): GCP Bucket Name.
        destination_blob_name (str): GCP Folder Name.
        gcp_credentials (str): Path pointing to GCP JSON credentials.
    """

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = gcp_credentials.strip("\"'")
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(destination_bucket_name)
    local_paths = glob.glob(directory_path + "/**", recursive=True)

    for local_file in local_paths:

        local_file = Path(local_file)
        remote_path = f"{destination_blob_name}/{str(local_file)[str(local_file).find('output_data/'):]}"

        if local_file.is_file():
            blob = bucket.blob(remote_path)
            blob.upload_from_filename(local_file)
            LOGGER.info(
                f"Uploading {local_file} to Google Cloud Bucket: {destination_bucket_name} \n"
                f"Subfolder {destination_blob_name}"
            )
