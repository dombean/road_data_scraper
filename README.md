# Road Data Scraper

![Tests](https://github.com/dombean/road_data_scraper/actions/workflows/tests.yml/badge.svg)

Scrapes and Cleans WebTRIS Traffic Flow API.

- Python Rewrite of [ONS Road Data Pipeline written in R](https://github.com/datasciencecampus/road-data-dump/tree/r-pipeline).
- Documentation of ONS Road Data Pipeline: https://datasciencecampus.github.io/road-data-pipeline-documentation/
- WebTRIS Traffic Flow API: https://webtris.highwaysengland.co.uk/api/swagger/ui/index

# Usage

Download and Install __Python 3.9__; if using Anaconda or Miniconda, create a virtual environment with __Python 3.9__, e.g., `conda create --name py39 python=3.9`

1) Git clone the repository: `git clone https://github.com/dombean/road_data_scraper.git`
2) Change Directory inside the road_data_scraper folder: `cd road_data_scraper/`
3) Install package in editable mode: `pip install -e .`
4) Change directory into package folder: `cd src/road_data_scraper/`
5) Adjust config.ini file accordingly
6) Run the script: `python main.py` or `python3 main.py`

# Adjusting the Config File (config.ini)

There are 5 configuration options in the config.ini file:
- __start_date__: provide a date in quotes, in the format, __%Y-%m-%d__; e.g, "2021-01-01" -- which is 1st January 2021.
- __end_date__: provide a date in quotes, in the format, __%Y-%m-%d__; e.g, "2021-01-31" -- which is 31st January 2021.
- __test_run__: can take on two values -- __True__ or __False__. Set test_run=False, when you want to download the entire data set. test_run by default is set to True, this is just to check the Pipeline works correctly (this will run the entire Pipeline on a subset of the available URL's).
- __generate_report__: can take on two values -- __True__ or __False__. By default, this is set to True, this will generate a HTML report with tables and graphs, showing the Active and Inactive ID's for each road sensor -- MIDAS, TMU, and TAME.
- __max_threads__: can take on two values -- __True__ or __False__. By default, this this is set to True, this will use all available threads on the computer when running the Pipeline. When, max_threads is set to False, this will use the max available threads on the computer minus 1 thread.
