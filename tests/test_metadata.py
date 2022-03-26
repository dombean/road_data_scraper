import unittest
from unittest.mock import patch

import pandas as pd
from pandas.testing import assert_frame_equal

from road_data_scraper.steps.metadata import (
    create_sensor_metadata_tuples,
    direction_string_cleaner,
    get_sensor_urls,
    name_string_cleaner,
)


class TestMetadata(unittest.TestCase):
    def setUp(self):

        headers = [
            "id",
            "name",
            "description",
            "longitude",
            "latitude",
            "status",
            "direction",
            "easting",
            "northing",
        ]

        # fmt: off
        data_midas = [
            [1,"MIDAS","M4/2295A2",-0.520380,51.493012,"Inactive","westbound",502816,178156],
            [2,"MIDAS","A1M/2259B",-0.320275,52.535158,"Active","southbound",514029,294356],
            [3,"MIDAS","M5/7482B",-2.175138,52.175652,"Active","northbound",388120,253057],
            [4,"MIDAS","M3/2173A",-1.392374,50.960359,"Active","westbound",442769,118058],
            [5,"MIDAS","M25/5764B",0.283162,51.575617,"Active","clockwise",558308,188775],
        ]

        data_tame = [
            [7236,"TMU","5607/1",-1.338882,51.100315,"Active","northbound",446387,133654],
            [7237,"TMU","5606/2",-1.341841,51.103119,"Active","southbound",446177,133964],
            [7238,"TMU","5606/1",-1.341654,51.103190,"Active","southbound",446190,133972],
            [7239,"TMU","5601/2",-1.339803,51.173895,"Active","northbound",446249,141836],
            [7240,"TMU","5601/1",-1.340046,51.173915,"Active","northbound",446232,141838],
        ]

        data_tmu = [
            [6304,"TAME",30360220,-0.960508,50.986164,"Active","southbound",473059,121266],
            [6305,"TAME",30360221,-0.961806,50.985430,"Active","northbound",472969,121183],
            [6310,"TAME",30360229,-0.832786,51.298988,"Active","westbound",481472,156187],
            [6311,"TAME",30360230,-1.035767,51.262403,"Active","eastbound",467374,151913],
            [6312,"TAME",30360231,-1.037151,51.262037,"Active","westbound",467278,151871],
        ]
        # fmt:on

        self.sensor_tables = {
            "midas": pd.DataFrame(data_midas, columns=headers),
            "tame": pd.DataFrame(data_tame, columns=headers),
            "tmu": pd.DataFrame(data_tmu, columns=headers),
        }

    def test_create_sensor_metadata_tuples(self):

        start_date = "01012020"
        end_date = "31012020"

        actual_result_midas = create_sensor_metadata_tuples(
            self.sensor_tables, start_date, end_date, sensor_name="midas"
        )

        expected_result_midas = [
            (
                "https://webtris.highwaysengland.co.uk/api/v1/reports/01012020/to/31012020/daily?sites=1&page=1&page_size=40000",
                "westbound",
                -0.52038,
                51.493012,
                "Inactive",
                502816,
                178156,
            ),
            (
                "https://webtris.highwaysengland.co.uk/api/v1/reports/01012020/to/31012020/daily?sites=2&page=1&page_size=40000",
                "southbound",
                -0.320275,
                52.535158,
                "Active",
                514029,
                294356,
            ),
            (
                "https://webtris.highwaysengland.co.uk/api/v1/reports/01012020/to/31012020/daily?sites=3&page=1&page_size=40000",
                "northbound",
                -2.175138,
                52.175652,
                "Active",
                388120,
                253057,
            ),
            (
                "https://webtris.highwaysengland.co.uk/api/v1/reports/01012020/to/31012020/daily?sites=4&page=1&page_size=40000",
                "westbound",
                -1.392374,
                50.960359,
                "Active",
                442769,
                118058,
            ),
            (
                "https://webtris.highwaysengland.co.uk/api/v1/reports/01012020/to/31012020/daily?sites=5&page=1&page_size=40000",
                "clockwise",
                0.283162,
                51.575617,
                "Active",
                558308,
                188775,
            ),
        ]

        actual_result_tame = create_sensor_metadata_tuples(
            self.sensor_tables, start_date, end_date, sensor_name="tame"
        )

        expected_result_tame = [
            (
                "https://webtris.highwaysengland.co.uk/api/v1/reports/01012020/to/31012020/daily?sites=7236&page=1&page_size=40000",
                "northbound",
                -1.338882,
                51.100315,
                "Active",
                446387,
                133654,
            ),
            (
                "https://webtris.highwaysengland.co.uk/api/v1/reports/01012020/to/31012020/daily?sites=7237&page=1&page_size=40000",
                "southbound",
                -1.341841,
                51.103119,
                "Active",
                446177,
                133964,
            ),
            (
                "https://webtris.highwaysengland.co.uk/api/v1/reports/01012020/to/31012020/daily?sites=7238&page=1&page_size=40000",
                "southbound",
                -1.341654,
                51.10319,
                "Active",
                446190,
                133972,
            ),
            (
                "https://webtris.highwaysengland.co.uk/api/v1/reports/01012020/to/31012020/daily?sites=7239&page=1&page_size=40000",
                "northbound",
                -1.339803,
                51.173895,
                "Active",
                446249,
                141836,
            ),
            (
                "https://webtris.highwaysengland.co.uk/api/v1/reports/01012020/to/31012020/daily?sites=7240&page=1&page_size=40000",
                "northbound",
                -1.340046,
                51.173915,
                "Active",
                446232,
                141838,
            ),
        ]

        actual_result_tmu = create_sensor_metadata_tuples(
            self.sensor_tables, start_date, end_date, sensor_name="tmu"
        )

        expected_result_tmu = [
            (
                "https://webtris.highwaysengland.co.uk/api/v1/reports/01012020/to/31012020/daily?sites=6304&page=1&page_size=40000",
                "southbound",
                -0.960508,
                50.986164,
                "Active",
                473059,
                121266,
            ),
            (
                "https://webtris.highwaysengland.co.uk/api/v1/reports/01012020/to/31012020/daily?sites=6305&page=1&page_size=40000",
                "northbound",
                -0.961806,
                50.98543,
                "Active",
                472969,
                121183,
            ),
            (
                "https://webtris.highwaysengland.co.uk/api/v1/reports/01012020/to/31012020/daily?sites=6310&page=1&page_size=40000",
                "westbound",
                -0.832786,
                51.298988,
                "Active",
                481472,
                156187,
            ),
            (
                "https://webtris.highwaysengland.co.uk/api/v1/reports/01012020/to/31012020/daily?sites=6311&page=1&page_size=40000",
                "eastbound",
                -1.035767,
                51.262403,
                "Active",
                467374,
                151913,
            ),
            (
                "https://webtris.highwaysengland.co.uk/api/v1/reports/01012020/to/31012020/daily?sites=6312&page=1&page_size=40000",
                "westbound",
                -1.037151,
                51.262037,
                "Active",
                467278,
                151871,
            ),
        ]

        assert actual_result_midas == expected_result_midas
        assert actual_result_tame == expected_result_tame
        assert actual_result_tmu == expected_result_tmu

    def test_get_sensor_urls_ARG_CALLS(self):
        """
        Test create_sensor_metadata_tuples() gets called 3 times by
        get_sensor_urls().
        """

        start_date = "2020-01-01"
        end_date = "2020-01-31"

        with patch(
            "road_data_scraper.steps.metadata.create_sensor_metadata_tuples"
        ) as patched_create_sensor_metadata_tuples:

            get_sensor_urls(self.sensor_tables, start_date, end_date)

            assert len(patched_create_sensor_metadata_tuples.call_args_list) == 3

    def test_get_sensor_urls_DATA(self):

        start_date = "2020-01-01"
        end_date = "2020-01-31"

        actual_result_midas, actual_result_tmu, actual_result_tame = get_sensor_urls(
            self.sensor_tables, start_date=start_date, end_date=end_date
        )

        expected_result_midas = [
            (
                "https://webtris.highwaysengland.co.uk/api/v1/reports/01012020/to/31012020/daily?sites=1&page=1&page_size=40000",
                "westbound",
                -0.52038,
                51.493012,
                "Inactive",
                502816,
                178156,
            ),
            (
                "https://webtris.highwaysengland.co.uk/api/v1/reports/01012020/to/31012020/daily?sites=2&page=1&page_size=40000",
                "southbound",
                -0.320275,
                52.535158,
                "Active",
                514029,
                294356,
            ),
            (
                "https://webtris.highwaysengland.co.uk/api/v1/reports/01012020/to/31012020/daily?sites=3&page=1&page_size=40000",
                "northbound",
                -2.175138,
                52.175652,
                "Active",
                388120,
                253057,
            ),
            (
                "https://webtris.highwaysengland.co.uk/api/v1/reports/01012020/to/31012020/daily?sites=4&page=1&page_size=40000",
                "westbound",
                -1.392374,
                50.960359,
                "Active",
                442769,
                118058,
            ),
            (
                "https://webtris.highwaysengland.co.uk/api/v1/reports/01012020/to/31012020/daily?sites=5&page=1&page_size=40000",
                "clockwise",
                0.283162,
                51.575617,
                "Active",
                558308,
                188775,
            ),
        ]

        expected_result_tame = [
            (
                "https://webtris.highwaysengland.co.uk/api/v1/reports/01012020/to/31012020/daily?sites=7236&page=1&page_size=40000",
                "northbound",
                -1.338882,
                51.100315,
                "Active",
                446387,
                133654,
            ),
            (
                "https://webtris.highwaysengland.co.uk/api/v1/reports/01012020/to/31012020/daily?sites=7237&page=1&page_size=40000",
                "southbound",
                -1.341841,
                51.103119,
                "Active",
                446177,
                133964,
            ),
            (
                "https://webtris.highwaysengland.co.uk/api/v1/reports/01012020/to/31012020/daily?sites=7238&page=1&page_size=40000",
                "southbound",
                -1.341654,
                51.10319,
                "Active",
                446190,
                133972,
            ),
            (
                "https://webtris.highwaysengland.co.uk/api/v1/reports/01012020/to/31012020/daily?sites=7239&page=1&page_size=40000",
                "northbound",
                -1.339803,
                51.173895,
                "Active",
                446249,
                141836,
            ),
            (
                "https://webtris.highwaysengland.co.uk/api/v1/reports/01012020/to/31012020/daily?sites=7240&page=1&page_size=40000",
                "northbound",
                -1.340046,
                51.173915,
                "Active",
                446232,
                141838,
            ),
        ]

        expected_result_tmu = [
            (
                "https://webtris.highwaysengland.co.uk/api/v1/reports/01012020/to/31012020/daily?sites=6304&page=1&page_size=40000",
                "southbound",
                -0.960508,
                50.986164,
                "Active",
                473059,
                121266,
            ),
            (
                "https://webtris.highwaysengland.co.uk/api/v1/reports/01012020/to/31012020/daily?sites=6305&page=1&page_size=40000",
                "northbound",
                -0.961806,
                50.98543,
                "Active",
                472969,
                121183,
            ),
            (
                "https://webtris.highwaysengland.co.uk/api/v1/reports/01012020/to/31012020/daily?sites=6310&page=1&page_size=40000",
                "westbound",
                -0.832786,
                51.298988,
                "Active",
                481472,
                156187,
            ),
            (
                "https://webtris.highwaysengland.co.uk/api/v1/reports/01012020/to/31012020/daily?sites=6311&page=1&page_size=40000",
                "eastbound",
                -1.035767,
                51.262403,
                "Active",
                467374,
                151913,
            ),
            (
                "https://webtris.highwaysengland.co.uk/api/v1/reports/01012020/to/31012020/daily?sites=6312&page=1&page_size=40000",
                "westbound",
                -1.037151,
                51.262037,
                "Active",
                467278,
                151871,
            ),
        ]

        assert actual_result_midas == expected_result_midas
        assert actual_result_tmu == expected_result_tmu
        assert actual_result_tame == expected_result_tame

    def test_name_string_cleaner(self):
        test_df = pd.DataFrame(
            [
                "MIDAS",
                "TAME",
                "TMU",
                "Legacy Site",
                "xx MIDAS",
                "xx TAME",
                "xx TMU",
                "xx Legacy Site",
                "xx MIDAS 00",
                "xx TAME 00",
                "xx TMU 00",
                "xx Legacy Site 00",
                "OTHER",
            ],
            columns=["name"],
        )

        actual_df = pd.DataFrame(test_df["name"].apply(name_string_cleaner))

        expected_df = pd.DataFrame(
            [
                "MIDAS",
                "TAME",
                "TMU",
                "Legacy Site",
                "MIDAS",
                "TAME",
                "TMU",
                "Legacy Site",
                "MIDAS",
                "TAME",
                "TMU",
                "Legacy Site",
                "OTHER",
            ],
            columns=["name"],
        )

        assert_frame_equal(actual_df, expected_df)

    def test_status_string_cleaner(self):

        test_df = pd.DataFrame(
            [
                "eastbound",
                "northbound",
                "southbound",
                "westbound",
                "clockwise",
                "anti-clockwise",
                "legacy site",
                "on connector",
                "OTHER",
                "xx eastbound",
                "xx northbound",
                "xx southbound",
                "xx westbound",
                "xx clockwise",
                "xx anti-clockwise",
                "xx legacy site",
                "xx on connector",
                "OTHER",
                "xx eastbound 00",
                "xx northbound 00",
                "xx southbound 00",
                "xx westbound 00",
                "xx clockwise 00",
                "xx anti-clockwise 00",
                "xx legacy site 00",
                "xx on connector 00",
                "OTHER",
            ],
            columns=["direction"],
        )

        actual_df = pd.DataFrame(test_df["direction"].apply(direction_string_cleaner))

        expected_df = pd.DataFrame(
            [
                "eastbound",
                "northbound",
                "southbound",
                "westbound",
                "clockwise",
                "clockwise",
                "legacy site",
                "carriageway connector",
                "OTHER",
                "eastbound",
                "northbound",
                "southbound",
                "westbound",
                "clockwise",
                "clockwise",
                "legacy site",
                "carriageway connector",
                "OTHER",
                "eastbound",
                "northbound",
                "southbound",
                "westbound",
                "clockwise",
                "clockwise",
                "legacy site",
                "carriageway connector",
                "OTHER",
            ],
            columns=["direction"],
        )

        assert_frame_equal(actual_df, expected_df)

    def test_get_sites_by_sensor(self):
        pass


if __name__ == "__main__":
    unittest.main()
