# Road Data Scraper

![Tests](https://github.com/dombean/road_data_scraper/actions/workflows/tests.yml/badge.svg)

Scrapes and Cleans WebTRIS Traffic Flow API.

- Python Rewrite of [ONS Road Data Pipeline written in R](https://github.com/datasciencecampus/road-data-dump/tree/r-pipeline).
- Documentation of ONS Road Data Pipeline: https://datasciencecampus.github.io/road-data-pipeline-documentation/
- WebTRIS Traffic Flow API: https://webtris.highwaysengland.co.uk/api/swagger/ui/index

To use:
1) Git clone the repository: `git clone https://github.com/dombean/road_data_scraper.git`
2) Change Directory inside the road_data_scraper folder: `cd road_data_scraper/`
3) Install package in editable mode: `pip install -e .`
4) Change directory into package folder: `cd src/road_data_scraper/`
5) Adjust config.ini file accordingly
6) Run the script: `python main.py` or `python3 main.py`
