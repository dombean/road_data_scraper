import unittest
from unittest import mock
from unittest.mock import patch

import pandas as pd
from pandas.testing import assert_frame_equal

from road_data_scraper.steps.download import _response_to_df, download


class TestDownload(unittest.TestCase):
    def setUp(self):
        pass

    @patch("road_data_scraper.steps.download.pd.DataFrame.from_dict")
    def test_response_to_df(self, mock_response):
        "Test response DataFrame contains correct column headers in a specific order."

        headers = [
            "Site Name",
            "Report Date",
            "Time Period Ending",
            "Time Interval",
            "0 - 520 cm",
            "521 - 660 cm",
            "661 - 1160 cm",
            "1160+ cm",
            "0 - 10 mph",
            "11 - 15 mph",
            "16 - 20 mph",
            "21 - 25 mph",
            "26 - 30 mph",
            "31 - 35 mph",
            "36 - 40 mph",
            "41 - 45 mph",
            "46 - 50 mph",
            "51 - 55 mph",
            "56 - 60 mph",
            "61 - 70 mph",
            "71 - 80 mph",
            "80+ mph",
            "Avg mph",
            "Total Volume",
        ]

        # fmt: off
        data = [
            ['A1M/2259B', '2021-01-01T00:00:00', '00:14:00', '0', '5', '0', '0', '1', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '63', '6'],
            ['A1M/2259B', '2021-01-01T00:00:00', '00:29:00', '1', '3', '0', '1', '2', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '54', '6'],
            ['A1M/2259B', '2021-01-01T00:00:00', '00:44:00', '2', '0', '0', '0', '1', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '50', '1']
        ]
        # fmt:on

        mock_response.return_value = pd.DataFrame(data, columns=headers)

        site_id = "2"
        longitude = "-0.320275"
        latitude = "52.535158"
        status = "Active"
        site_type = "midas"
        direction = "southbound"
        easting = "514029"
        northing = "294356"

        actual_result_df = _response_to_df(
            response=mock_response,
            site_id=site_id,
            longitude=longitude,
            latitude=latitude,
            status=status,
            site_type=site_type,
            direction=direction,
            easting=easting,
            northing=northing,
        )

        headers = [
            "site_id",
            "Site Name",
            "Report Date",
            "Time Period Ending",
            "Time Interval",
            "0 - 520 cm",
            "521 - 660 cm",
            "661 - 1160 cm",
            "1160+ cm",
            "0 - 10 mph",
            "11 - 15 mph",
            "16 - 20 mph",
            "21 - 25 mph",
            "26 - 30 mph",
            "31 - 35 mph",
            "36 - 40 mph",
            "41 - 45 mph",
            "46 - 50 mph",
            "51 - 55 mph",
            "56 - 60 mph",
            "61 - 70 mph",
            "71 - 80 mph",
            "80+ mph",
            "Avg mph",
            "Total Volume",
            "longitude",
            "latitude",
            "sites_status",
            "type",
            "direction",
            "easting",
            "northing",
        ]

        # fmt: off
        data = [
            ['2', 'A1M/2259B', '2021-01-01T00:00:00', '00:14:00', '0', '5', '0', '0', '1', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '63', '6', '-0.320275', '52.535158', 'Active', 'midas', 'southbound', '514029', '294356'],
            ['2', 'A1M/2259B', '2021-01-01T00:00:00', '00:29:00', '1', '3', '0', '1', '2', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '54', '6', '-0.320275', '52.535158', 'Active', 'midas', 'southbound', '514029', '294356'],
            ['2', 'A1M/2259B', '2021-01-01T00:00:00', '00:44:00', '2', '0', '0', '0', '1', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '50', '1', '-0.320275', '52.535158', 'Active', 'midas', 'southbound', '514029', '294356'],
        ]
        # fmt:on

        expected_df = pd.DataFrame(data, columns=headers)

        assert_frame_equal(
            actual_result_df.reset_index(drop=True),
            expected_df.reset_index(drop=True),
        )

    @patch("road_data_scraper.steps.download.open")
    @patch(
        "concurrent.futures.ThreadPoolExecutor",
    )
    @patch("road_data_scraper.steps.download.csv.DictWriter")
    def test_download_CSV_WRITE_HEADER(
        self,
        mock_csv_dictwriter,
        mock_threadpoolexecutor,
        mock_csv_open,
    ):
        """Test csv.DictWriter is called with expected file path and expected fieldnames (headers)."""

        midas_metadata = [
            (
                "https://webtris.highwaysengland.co.uk/api/v1/reports/01012021/to/31012021/daily?sites=2&page=1&page_size=40000",
                2,
                "midas",
                "southbound",
                -0.320275451712423,
                52.5351577963853,
                "Active",
                "514029",
                "294356",
            )
        ]

        download(
            site_name="midas",
            start_date="2021-01-01",
            end_date="2021-01-31",
            metadata=midas_metadata,
            test_run=True,
            run_id_path="/home/user/downloads",
        )

        expected_headers = {
            "fieldnames": [
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
        }

        # Assert CSV DictWriter uses expected_headers in fieldnames argument
        assert mock_csv_dictwriter.call_args_list[0][1] == expected_headers

        # # Assert open is called with correct CSV File Path and Mode
        assert mock_csv_open.call_args_list[0] == mock.call(
            "/home/user/downloads/midas_2021-01-01-2021-01-31_TEST_RUN.csv", "w"
        )


if __name__ == "__main__":
    unittest.main()
