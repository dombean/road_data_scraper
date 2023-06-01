"""
File Handler Module
-------------------
This module provides functionalities related to handling files and directories for a data scraping application. It includes utilities 
for creating directories to store scraped data, saving configuration files, and uploading files to Google Cloud Storage (GCP) Buckets.

The `file_handler` function is used to create directories to store the scraped data, metadata, and reports. It takes in the configuration 
file, a boolean flag indicating whether the run is made through FastAPI, start date, and end date as input. The function then creates 
unique directories based on the current date and time and returns these directories as Path objects.

The `dump_config` function dumps the configuration file that was used for a particular run into the metadata directory. This is useful for 
keeping track of what settings were used for a particular run and can be helpful for debugging and reproducibility.

The `gcp_upload_from_directory` function uploads the entire output directory for a Pipeline Run to a Google Cloud Platform (GCP) Bucket. It 
uses the Google Cloud storage client to handle the uploading process. The user has to provide the directory that needs to be uploaded, 
the name of the GCP bucket, the name of the blob in the GCP bucket, and the path to the JSON file containing GCP credentials.

Imported Libraries:
-------------------
- ast: For converting a string representation of dictionary to a dictionary.
- datetime: For getting the current date and time.
- glob: For getting the list of all files in a directory.
- logging: For logging details about the progress and errors.
- os: For setting the GCP credentials in the environment variables.
- pathlib: For handling the file path.
- google.cloud.storage: For uploading files to Google Cloud Storage.

Global Variables:
-----------------
- LOGGER: Logging object for logging progress and errors.
"""
import ast
import datetime
import glob
import logging
import os
from pathlib import Path

from google.cloud import storage

LOGGER = logging.getLogger(__name__)


def file_handler(config: dict, api_run: bool, start_date: str, end_date: str) -> tuple:
    """
    Creates directories to store scraped data and returns newly created directories as Path objects.

    The function makes use of current date and time for the creation of unique directory names. These directories are then used to
    store data, metadata, and report related to the data scraping process. All the paths are then returned as Path objects.

    Args:
        config (dict): Configuration file for this run. Contains various parameters for the scraping process including user settings.
        api_run (bool): Flag indicating whether this run is made through FastAPI. It helps decide how to extract 'output_path' from config.
        start_date (str): The start date for data to be scraped. Format should be '%Y-%m-%d'.
        end_date (str): The end date for data to be scraped. Format should be '%Y-%m-%d'.

    Raises:
        ValueError: If user does not provide a valid output directory in the configuration file.

    Returns:
        tuple: Returns four Path objects. These represent paths to directories where data, metadata, and reports will be stored. The fourth
        path is to the main directory where the above directories reside.
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


def dump_config(config: dict, metadata_path: Path, api_run: bool) -> None:
    """
    Saves the configuration file to the metadata path.

    The function dumps the configuration file that was used for a particular run into the metadata directory. This can help keep a track
    of what settings were used for a particular run and can be helpful in debugging and reproducibility.

    Args:
        config (dict): Configuration file for this run.
        metadata_path (Path): Path object containing path to metadata output directory.
        api_run (bool): Flag indicating whether this run is made through FastAPI. It helps decide how to format the config file.

    Returns:
        None
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
) -> None:
    """
    Uploads the entire output directory for a Pipeline Run to a Google Cloud Platform (GCP) Bucket.

    This function is used to upload all the files in a given directory to a specified GCP bucket. It uses the Google Cloud storage
    client to handle the uploading process.

    Args:
        directory_path (str): The directory that needs to be uploaded. It should contain the path to the directory.
        destination_bucket_name (str): The name of the GCP bucket where the directory will be uploaded.
        destination_blob_name (str): The name of the blob (similar to a folder) in the GCP bucket where the directory will be uploaded.
        gcp_credentials (str): The path to the JSON file containing GCP credentials.

    Returns:
        None
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
