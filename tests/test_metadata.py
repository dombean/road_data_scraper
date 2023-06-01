import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal

from road_data_scraper.steps.metadata import (
    create_sensor_metadata_tuples,
    direction_string_cleaner,
    get_sensor_urls,
    get_sites_by_sensor,
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
            [6304,"TAME",30360220,-0.960508,50.986164,"Active","southbound",473059,121266],
            [6305,"TAME",30360221,-0.961806,50.985430,"Active","northbound",472969,121183],
            [6310,"TAME",30360229,-0.832786,51.298988,"Active","westbound",481472,156187],
            [6311,"TAME",30360230,-1.035767,51.262403,"Active","eastbound",467374,151913],
            [6312,"TAME",30360231,-1.037151,51.262037,"Active","westbound",467278,151871],
        ]

        data_tmu = [
            [7236,"TMU","5607/1",-1.338882,51.100315,"Active","northbound",446387,133654],
            [7237,"TMU","5606/2",-1.341841,51.103119,"Active","southbound",446177,133964],
            [7238,"TMU","5606/1",-1.341654,51.103190,"Active","southbound",446190,133972],
            [7239,"TMU","5601/2",-1.339803,51.173895,"Active","northbound",446249,141836],
            [7240,"TMU","5601/1",-1.340046,51.173915,"Active","northbound",446232,141838],
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
                1,
                "MIDAS",
                "westbound",
                -0.52038,
                51.493012,
                "Inactive",
                502816,
                178156,
            ),
            (
                "https://webtris.highwaysengland.co.uk/api/v1/reports/01012020/to/31012020/daily?sites=2&page=1&page_size=40000",
                2,
                "MIDAS",
                "southbound",
                -0.320275,
                52.535158,
                "Active",
                514029,
                294356,
            ),
            (
                "https://webtris.highwaysengland.co.uk/api/v1/reports/01012020/to/31012020/daily?sites=3&page=1&page_size=40000",
                3,
                "MIDAS",
                "northbound",
                -2.175138,
                52.175652,
                "Active",
                388120,
                253057,
            ),
            (
                "https://webtris.highwaysengland.co.uk/api/v1/reports/01012020/to/31012020/daily?sites=4&page=1&page_size=40000",
                4,
                "MIDAS",
                "westbound",
                -1.392374,
                50.960359,
                "Active",
                442769,
                118058,
            ),
            (
                "https://webtris.highwaysengland.co.uk/api/v1/reports/01012020/to/31012020/daily?sites=5&page=1&page_size=40000",
                5,
                "MIDAS",
                "clockwise",
                0.283162,
                51.575617,
                "Active",
                558308,
                188775,
            ),
        ]

        actual_result_tmu = create_sensor_metadata_tuples(
            self.sensor_tables, start_date, end_date, sensor_name="tmu"
        )

        expected_result_tmu = [
            (
                "https://webtris.highwaysengland.co.uk/api/v1/reports/01012020/to/31012020/daily?sites=7236&page=1&page_size=40000",
                7236,
                "TMU",
                "northbound",
                -1.338882,
                51.100315,
                "Active",
                446387,
                133654,
            ),
            (
                "https://webtris.highwaysengland.co.uk/api/v1/reports/01012020/to/31012020/daily?sites=7237&page=1&page_size=40000",
                7237,
                "TMU",
                "southbound",
                -1.341841,
                51.103119,
                "Active",
                446177,
                133964,
            ),
            (
                "https://webtris.highwaysengland.co.uk/api/v1/reports/01012020/to/31012020/daily?sites=7238&page=1&page_size=40000",
                7238,
                "TMU",
                "southbound",
                -1.341654,
                51.10319,
                "Active",
                446190,
                133972,
            ),
            (
                "https://webtris.highwaysengland.co.uk/api/v1/reports/01012020/to/31012020/daily?sites=7239&page=1&page_size=40000",
                7239,
                "TMU",
                "northbound",
                -1.339803,
                51.173895,
                "Active",
                446249,
                141836,
            ),
            (
                "https://webtris.highwaysengland.co.uk/api/v1/reports/01012020/to/31012020/daily?sites=7240&page=1&page_size=40000",
                7240,
                "TMU",
                "northbound",
                -1.340046,
                51.173915,
                "Active",
                446232,
                141838,
            ),
        ]

        actual_result_tame = create_sensor_metadata_tuples(
            self.sensor_tables, start_date, end_date, sensor_name="tame"
        )

        expected_result_tame = [
            (
                "https://webtris.highwaysengland.co.uk/api/v1/reports/01012020/to/31012020/daily?sites=6304&page=1&page_size=40000",
                6304,
                "TAME",
                "southbound",
                -0.960508,
                50.986164,
                "Active",
                473059,
                121266,
            ),
            (
                "https://webtris.highwaysengland.co.uk/api/v1/reports/01012020/to/31012020/daily?sites=6305&page=1&page_size=40000",
                6305,
                "TAME",
                "northbound",
                -0.961806,
                50.98543,
                "Active",
                472969,
                121183,
            ),
            (
                "https://webtris.highwaysengland.co.uk/api/v1/reports/01012020/to/31012020/daily?sites=6310&page=1&page_size=40000",
                6310,
                "TAME",
                "westbound",
                -0.832786,
                51.298988,
                "Active",
                481472,
                156187,
            ),
            (
                "https://webtris.highwaysengland.co.uk/api/v1/reports/01012020/to/31012020/daily?sites=6311&page=1&page_size=40000",
                6311,
                "TAME",
                "eastbound",
                -1.035767,
                51.262403,
                "Active",
                467374,
                151913,
            ),
            (
                "https://webtris.highwaysengland.co.uk/api/v1/reports/01012020/to/31012020/daily?sites=6312&page=1&page_size=40000",
                6312,
                "TAME",
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
                1,
                "MIDAS",
                "westbound",
                -0.52038,
                51.493012,
                "Inactive",
                502816,
                178156,
            ),
            (
                "https://webtris.highwaysengland.co.uk/api/v1/reports/01012020/to/31012020/daily?sites=2&page=1&page_size=40000",
                2,
                "MIDAS",
                "southbound",
                -0.320275,
                52.535158,
                "Active",
                514029,
                294356,
            ),
            (
                "https://webtris.highwaysengland.co.uk/api/v1/reports/01012020/to/31012020/daily?sites=3&page=1&page_size=40000",
                3,
                "MIDAS",
                "northbound",
                -2.175138,
                52.175652,
                "Active",
                388120,
                253057,
            ),
            (
                "https://webtris.highwaysengland.co.uk/api/v1/reports/01012020/to/31012020/daily?sites=4&page=1&page_size=40000",
                4,
                "MIDAS",
                "westbound",
                -1.392374,
                50.960359,
                "Active",
                442769,
                118058,
            ),
            (
                "https://webtris.highwaysengland.co.uk/api/v1/reports/01012020/to/31012020/daily?sites=5&page=1&page_size=40000",
                5,
                "MIDAS",
                "clockwise",
                0.283162,
                51.575617,
                "Active",
                558308,
                188775,
            ),
        ]

        expected_result_tmu = [
            (
                "https://webtris.highwaysengland.co.uk/api/v1/reports/01012020/to/31012020/daily?sites=7236&page=1&page_size=40000",
                7236,
                "TMU",
                "northbound",
                -1.338882,
                51.100315,
                "Active",
                446387,
                133654,
            ),
            (
                "https://webtris.highwaysengland.co.uk/api/v1/reports/01012020/to/31012020/daily?sites=7237&page=1&page_size=40000",
                7237,
                "TMU",
                "southbound",
                -1.341841,
                51.103119,
                "Active",
                446177,
                133964,
            ),
            (
                "https://webtris.highwaysengland.co.uk/api/v1/reports/01012020/to/31012020/daily?sites=7238&page=1&page_size=40000",
                7238,
                "TMU",
                "southbound",
                -1.341654,
                51.10319,
                "Active",
                446190,
                133972,
            ),
            (
                "https://webtris.highwaysengland.co.uk/api/v1/reports/01012020/to/31012020/daily?sites=7239&page=1&page_size=40000",
                7239,
                "TMU",
                "northbound",
                -1.339803,
                51.173895,
                "Active",
                446249,
                141836,
            ),
            (
                "https://webtris.highwaysengland.co.uk/api/v1/reports/01012020/to/31012020/daily?sites=7240&page=1&page_size=40000",
                7240,
                "TMU",
                "northbound",
                -1.340046,
                51.173915,
                "Active",
                446232,
                141838,
            ),
        ]

        expected_result_tame = [
            (
                "https://webtris.highwaysengland.co.uk/api/v1/reports/01012020/to/31012020/daily?sites=6304&page=1&page_size=40000",
                6304,
                "TAME",
                "southbound",
                -0.960508,
                50.986164,
                "Active",
                473059,
                121266,
            ),
            (
                "https://webtris.highwaysengland.co.uk/api/v1/reports/01012020/to/31012020/daily?sites=6305&page=1&page_size=40000",
                6305,
                "TAME",
                "northbound",
                -0.961806,
                50.98543,
                "Active",
                472969,
                121183,
            ),
            (
                "https://webtris.highwaysengland.co.uk/api/v1/reports/01012020/to/31012020/daily?sites=6310&page=1&page_size=40000",
                6310,
                "TAME",
                "westbound",
                -0.832786,
                51.298988,
                "Active",
                481472,
                156187,
            ),
            (
                "https://webtris.highwaysengland.co.uk/api/v1/reports/01012020/to/31012020/daily?sites=6311&page=1&page_size=40000",
                6311,
                "TAME",
                "eastbound",
                -1.035767,
                51.262403,
                "Active",
                467374,
                151913,
            ),
            (
                "https://webtris.highwaysengland.co.uk/api/v1/reports/01012020/to/31012020/daily?sites=6312&page=1&page_size=40000",
                6312,
                "TAME",
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
                "midas",
                "tame",
                "tmu",
                "Legacy Site",
                "midas",
                "tame",
                "tmu",
                "Legacy Site",
                "midas",
                "tame",
                "tmu",
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

    @patch("road_data_scraper.steps.metadata.requests.get")
    def test_get_sites_by_sensor(self, patched_requests_get):
        """
        Test requests.get() gets called once with https://webtris.highwaysengland.co.uk/api/v1/sites ;
        and above request gets gets preprocessed correctly.
        """

        headers = ["Id", "Name", "Description", "Longitude", "Latitude", "Status"]

        # fmt:off
        data = [
            [10166,"MIDAS site at M62/2255A priority 1 on link 116036502; GPS Ref: 440444;423718; Eastbound","M62/2255A",-1.38877156618287,53.7083453261469,"Active"],
            [17690,"MIDAS site at M6/6700B priority 1 on link 123008301; GPS Ref: 377417;360967; Southbound","M6/6700B",-2.33908529341612,53.145380106213,"Active"],
            [5129,"MIDAS site at A14/2092B priority 1 on link 106050701; GPS Ref: 628493;235331; Westbound","A14/2092B",1.32505738692639,51.9694695205584,"Inactive"],
            [4334,"MIDAS site at M56/8100A priority 1 on link 115002802; GPS Ref: 382223;388743; Westbound","M56/8100A",-2.26879705237723,53.3952314430999,"Active"],
            [1469,"MIDAS site at M4/2604A priority 1 on link 105004401; GPS Ref: 476666;169913; Westbound","M4/2604A",-0.898749416349556,51.4230532115224,"Inactive"],
            [7155,"TAME Site 30361690 on link A66 westbound between B6412 and B6262 Penrith (east); GPS Ref: 356400;528878; Westbound","30361690",-2.677275720372,54.6531108503357,"Active"],
            [6345,"TAME Site 30360279 on link A31 eastbound between B3072 and A348; GPS Ref: 408555;101699; Eastbound","30360279",-1.87992752606348,50.8147683679067,"Active"],
            [6367,"TAME Site 30360308 on link A34 southbound exit for M4; GPS Ref: 448030;173384; Southbound","30360308",-1.3100849050785,51.4574039365199,"Active"],
            [6870,"TAME Site 30361350 on link M606 northbound between J1 and J2; GPS Ref: 417558;427767; Northbound","30361350",-1.73524956512699,53.7460012500777,"Active"],
            [6894,"TAME Site 30360915 on link A49 southbound between A4112 and A44 near Leominster (north); GPS Ref: 350498;259905; Southbound","30360915",-2.72627822817284,52.2351119997405,"Active"],
            [8423,"TMU Site 7560/2 on link A50 eastbound within the A520 junction; GPS Ref: 392893;342374; Eastbound","7560/2",-2.10729218492767,52.9786812071011,"Active"],
            [8664,"TMU Site 9037/1 on link M61 J6 northbound exit; GPS Ref: 364120;408604; Northbound","9037/1",-2.54329844234735,53.57281888294,"Active"],
            [8970,"TMU Site 5897/2 on link A249 northbound within the B2006 junction; GPS Ref: 588672;164799; Northbound","5897/2",0.708073594462995,51.3509418603741,"Active"],
            [8380,"TMU Site 9337/1 on link A19 southbound between A67 and A172; GPS Ref: 444213;503363; Southbound","9337/1",-1.32009723543328,54.4237987227377,"Active"],
            [9333,"TMU Site 9934/2 on link A14 eastbound within J20; GPS Ref: 516148;272061; Eastbound","9934/2",-0.296788367893114,52.3343633966701,"Active"],
            [11254,"","M1/4895M",-1.52994981176279,53.6472227911831,"Inactive"],
            [12340,"","M4/2354A",-0.592400532663463,51.5006778553958,"Inactive"],
            [11448,"","M56/8161A",-2.32320139267286,53.3572993902919,"Inactive"],
            [13374,"","M6/6865A",-2.39514507975795,53.2864040052469,"Inactive"],
            [13294,"","M1/2827A",-0.727727112826888,52.0716491192959,"Inactive"]
        ]
        # fmt:on

        test_df = pd.DataFrame(data, columns=headers)

        with patch(
            "road_data_scraper.steps.metadata.pd.DataFrame.from_dict",
        ) as patched_dataframe_from_dict:
            patched_dataframe_from_dict.return_value = test_df

            actual_sensor_tables_dict, actual_lookup_df = get_sites_by_sensor()

        expected_headers = [
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

        # fmt:off
        expected_midas_data = [
            [10166, "midas", "M62/2255A", -1.38877157, 53.70834533, "Active", "eastbound", "440444", "423718"],
            [17690, "midas", "M6/6700B", -2.33908529, 53.14538011, "Active", "southbound", "377417", "360967"],
            [5129, "midas", "A14/2092B",  1.32505739, 51.96946952, "Inactive", "westbound", "628493", "235331"],
            [4334, "midas", "M56/8100A", -2.26879705, 53.39523144, "Active", "westbound", "382223", "388743"],
            [1469, "midas", "M4/2604A", -0.89874942, 51.42305321, "Inactive", "westbound", "476666", "169913"],
        ]

        expected_tmu_data = [
            [8423, "tmu", "7560/2", -2.10729218, 52.97868121, "Active", "eastbound", "392893", "342374"],
            [8664, "tmu", "9037/1", -2.54329844, 53.57281888, "Active", "northbound", "364120", "408604"],
            [8970, "tmu", "5897/2",  0.70807359, 51.35094186, "Active", "northbound", "588672", "164799"],
            [8380, "tmu", "9337/1", -1.32009724, 54.42379872, "Active", "southbound", "444213", "503363"],
            [9333, "tmu", "9934/2", -0.29678837, 52.3343634 , "Active", "eastbound", "516148", "272061"],
        ]

        expected_tame_data = [
            [7155, "tame", "30361690", -2.67727572, 54.65311085, "Active", "westbound", "356400", "528878"],
            [6345, "tame", "30360279", -1.87992753, 50.81476837, "Active", "eastbound", "408555", "101699"],
            [6367, "tame", "30360308", -1.31008491, 51.45740394, "Active", "southbound", "448030", "173384"],
            [6870, "tame", "30361350", -1.73524957, 53.74600125, "Active", "northbound", "417558", "427767"],
            [6894, "tame", "30360915", -2.72627823, 52.235112  , "Active", "southbound", "350498", "259905"],
        ]

        expected_other_data = [
            [11254, "", "M1/4895M", -1.52994981, 53.64722279, "Inactive", "", np.nan, np.nan],
            [12340, "", "M4/2354A", -0.59240053, 51.50067786, "Inactive", "", np.nan, np.nan],
            [11448, "", "M56/8161A", -2.32320139, 53.35729939, "Inactive", "", np.nan, np.nan],
            [13374, "", "M6/6865A", -2.39514508, 53.28640401, "Inactive", "", np.nan, np.nan],
            [13294, "", "M1/2827A", -0.72772711, 52.07164912, "Inactive", "", np.nan, np.nan],
        ]
        # fmt:on
        expected_other_df = pd.DataFrame(expected_other_data, columns=expected_headers)
        expected_other_df["easting"] = expected_other_df["easting"].astype(object)
        expected_other_df["northing"] = expected_other_df["northing"].astype(object)

        expected_sensor_tables_dict = {
            "midas": pd.DataFrame(expected_midas_data, columns=expected_headers),
            "tmu": pd.DataFrame(expected_tmu_data, columns=expected_headers),
            "tame": pd.DataFrame(expected_tame_data, columns=expected_headers),
            "other": expected_other_df,
        }

        assert_frame_equal(
            actual_sensor_tables_dict["midas"].reset_index(drop=True),
            expected_sensor_tables_dict["midas"].reset_index(drop=True),
        )
        assert_frame_equal(
            actual_sensor_tables_dict["tmu"].reset_index(drop=True),
            expected_sensor_tables_dict["tmu"].reset_index(drop=True),
        )
        assert_frame_equal(
            actual_sensor_tables_dict["tame"].reset_index(drop=True),
            expected_sensor_tables_dict["tame"].reset_index(drop=True),
        )
        assert_frame_equal(
            actual_sensor_tables_dict["other"].reset_index(drop=True),
            expected_sensor_tables_dict["other"].reset_index(drop=True),
        )

        expected_lookup_df = pd.DataFrame(
            expected_midas_data
            + expected_tame_data
            + expected_tmu_data
            + expected_other_data,
            columns=expected_headers,
        )
        assert_frame_equal(actual_lookup_df, expected_lookup_df)

        patched_requests_get.called_once_with(
            "https://webtris.highwaysengland.co.uk/api/v1/sites"
        )


if __name__ == "__main__":
    unittest.main()
