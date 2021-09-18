import datetime
import logging
from pathlib import Path


def file_handler():

    run_id = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S.%f")

    run_id_path_data = f"./output_data/{run_id}/data/"
    run_id_path_metadata = f"./output_data/{run_id}/metadata/"
    run_id_path_report = f"./output_data/{run_id}/report/"

    data_path = Path(run_id_path_data)
    metadata_path = Path(run_id_path_metadata)
    report_path = Path(run_id_path_report)

    logging.info(f"Making Data Directory at: {data_path}")
    data_path.mkdir(parents=True, exist_ok=True)

    logging.info(f"Making Metadata Directory at: {metadata_path}")
    metadata_path.mkdir(parents=True, exist_ok=True)

    logging.info(f"Making Report Directory at: {report_path}")
    report_path.mkdir(parents=True, exist_ok=True)

    return data_path, metadata_path, report_path


def dump_config(config, full_path):

    logging.info(f"Dumping config.ini for Run at {full_path}")

    config_dict = {
        section: dict(config.items(section)) for section in config.sections()
    }

    with open(f"{str(full_path)}/config_metadata.txt", "w") as file:
        print(config_dict, file=file)
