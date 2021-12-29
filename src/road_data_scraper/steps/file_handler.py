import ast
import datetime
import glob
import logging
import os
from pathlib import Path

from google.cloud import storage


def file_handler(config, api_run):

    run_id = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S.%f")

    if api_run:
        user_output_path = config["user_settings"]["output_path"].strip("\"'")
    else:
        user_output_path = ast.literal_eval(config["user_settings"]["output_path"])

    if not user_output_path:
        raise ValueError("Please provide a valid output directory.")

    run_id_path_data = f"{user_output_path}/output_data/{run_id}/data/"
    run_id_path_metadata = f"{user_output_path}/output_data/{run_id}/metadata/"
    run_id_path_report = f"{user_output_path}/output_data/{run_id}/report/"
    run_id_path = f"{user_output_path}/output_data/{run_id}/"

    data_path = Path(run_id_path_data)
    metadata_path = Path(run_id_path_metadata)
    report_path = Path(run_id_path_report)

    logging.info(f"Making Data Directory at: {data_path}")
    data_path.mkdir(parents=True, exist_ok=True)

    logging.info(f"Making Metadata Directory at: {metadata_path}")
    metadata_path.mkdir(parents=True, exist_ok=True)

    logging.info(f"Making Report Directory at: {report_path}")
    report_path.mkdir(parents=True, exist_ok=True)

    return data_path, metadata_path, report_path, run_id_path


def dump_config(config, full_path, api_run):

    logging.info(f"Dumping config.ini for Run at {full_path}")

    if api_run:
        config_dict = config
    else:
        config_dict = {
            section: dict(config.items(section)) for section in config.sections()
        }

    with open(f"{str(full_path)}/config_metadata.txt", "w") as file:
        print(config_dict, file=file)


def gcp_upload_from_directory(
    directory_path: str,
    destination_bucket_name: str,
    destination_blob_name: str,
    gcp_credentials: str,
):

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
            logging.info(
                f"Uploading {local_file} to Google Cloud Bucket: {destination_bucket_name} \n"
                f"Subfolder {destination_blob_name}"
            )
