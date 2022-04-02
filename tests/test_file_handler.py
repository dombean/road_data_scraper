import configparser
import datetime
import unittest
from io import BytesIO, TextIOWrapper
from pathlib import Path
from unittest.mock import patch

from road_data_scraper.steps.file_handler import dump_config, file_handler


class TestFileHandler(unittest.TestCase):
    def setUp(self):
        self.config = {
            "user_settings": {
                "start_date": "2020-01-01",
                "end_date": "2020-01-31",
                "test_run": True,
                "generate_report": True,
                "output_path": "/tmp/landing_zone",
                "rm_dir": False,
                # GCP
                "gcp_storage": False,
                "gcp_credentials": "./gcp_creds.json",
                "gcp_bucket_name": "road_data_dump",
                "gcp_blob_name": "landing_zone",
            }
        }

        self.start_date = self.config["user_settings"]["start_date"]
        self.end_date = self.config["user_settings"]["end_date"]

    @patch.object(Path, "mkdir")
    def test_file_handler_API_RUN(self, patched_pathlib_mkdir):
        "Test file_handler() with api_run=True"

        expected_datetime = datetime.datetime(2022, 1, 31)

        with patch("datetime.datetime", wraps=datetime.datetime) as patched_datetime:

            patched_datetime.now.return_value = expected_datetime

            (
                actual_run_id_path_data,
                actual_run_id_path_metadata,
                actual_run_id_path_report,
                actual_run_id_path,
            ) = file_handler(
                config=self.config,
                api_run=True,
                start_date=self.start_date,
                end_date=self.end_date,
            )

        assert len(patched_pathlib_mkdir.call_args_list) == 3

        expected_run_id_path_data = Path(
            "/tmp/landing_zone/output_data/2022-01-31-00-00-00.000000_January-01-2020_to_January-31-2020/data"
        )
        expected_run_id_path_metadata = Path(
            "/tmp/landing_zone/output_data/2022-01-31-00-00-00.000000_January-01-2020_to_January-31-2020/metadata"
        )
        expected_run_id_path_report = Path(
            "/tmp/landing_zone/output_data/2022-01-31-00-00-00.000000_January-01-2020_to_January-31-2020/report"
        )
        expected_run_id_path = "/tmp/landing_zone/output_data/2022-01-31-00-00-00.000000_January-01-2020_to_January-31-2020/"

        assert actual_run_id_path_data == expected_run_id_path_data
        assert actual_run_id_path_metadata == expected_run_id_path_metadata
        assert actual_run_id_path_report == expected_run_id_path_report
        assert actual_run_id_path == expected_run_id_path

    @patch("road_data_scraper.steps.file_handler.ast.literal_eval")
    @patch.object(Path, "mkdir")
    def test_file_handler_LOCAL_RUN(
        self, patched_pathlib_mkdir, patched_ast_literal_eval
    ):
        "Test file_handler() with api_run=False"

        patched_ast_literal_eval.return_value = self.config["user_settings"][
            "output_path"
        ]

        expected_datetime = datetime.datetime(2022, 1, 31)
        with patch("datetime.datetime", wraps=datetime.datetime) as patched_datetime:

            patched_datetime.now.return_value = expected_datetime

            (
                actual_run_id_path_data,
                actual_run_id_path_metadata,
                actual_run_id_path_report,
                actual_run_id_path,
            ) = file_handler(
                config=self.config,
                api_run=False,
                start_date=self.start_date,
                end_date=self.end_date,
            )

        assert len(patched_pathlib_mkdir.call_args_list) == 3

        expected_run_id_path_data = Path(
            "/tmp/landing_zone/output_data/2022-01-31-00-00-00.000000_January-01-2020_to_January-31-2020/data"
        )
        expected_run_id_path_metadata = Path(
            "/tmp/landing_zone/output_data/2022-01-31-00-00-00.000000_January-01-2020_to_January-31-2020/metadata"
        )
        expected_run_id_path_report = Path(
            "/tmp/landing_zone/output_data/2022-01-31-00-00-00.000000_January-01-2020_to_January-31-2020/report"
        )
        expected_run_id_path = "/tmp/landing_zone/output_data/2022-01-31-00-00-00.000000_January-01-2020_to_January-31-2020/"

        assert actual_run_id_path_data == expected_run_id_path_data
        assert actual_run_id_path_metadata == expected_run_id_path_metadata
        assert actual_run_id_path_report == expected_run_id_path_report
        assert actual_run_id_path == expected_run_id_path

    @patch("builtins.open", create=True)
    def test_dump_config_API_RUN(self, patched_open):
        "Test dump_config() with api_run=True"

        metadata_path = Path(
            "/tmp/landing_zone/output_data/2022-01-31-00-00-00.000000_January-01-2020_to_January-31-2020/metadata/"
        )

        expected_metadata_config_dump_path = "/tmp/landing_zone/output_data/2022-01-31-00-00-00.000000_January-01-2020_to_January-31-2020/metadata/config_metadata.txt"

        dump_config(config=self.config, metadata_path=metadata_path, api_run=True)

        patched_open.assert_called_with(expected_metadata_config_dump_path, "w")

    @patch("builtins.open", create=True)
    def test_dump_config_LOCAL_RUN(self, patched_open):
        "Test dump_config() with api_run=False"

        metadata_path = Path(
            "/tmp/landing_zone/output_data/2022-01-31-00-00-00.000000_January-01-2020_to_January-31-2020/metadata/"
        )

        expected_metadata_config_dump_path = "/tmp/landing_zone/output_data/2022-01-31-00-00-00.000000_January-01-2020_to_January-31-2020/metadata/config_metadata.txt"

        fake_config_file = TextIOWrapper(
            BytesIO(
                b"[user_settings]\n"
                b"start_date: '2020-01-01'"
                b"end_date: '2020-01-31'"
            )
        )

        config = configparser.ConfigParser()
        config.read(fake_config_file)

        dump_config(config=config, metadata_path=metadata_path, api_run=False)

        patched_open.assert_called_with(expected_metadata_config_dump_path, "w")


if __name__ == "__main__":
    unittest.main()
