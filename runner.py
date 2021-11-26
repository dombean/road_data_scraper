import configparser

from road_data_scraper.main import run

config = configparser.ConfigParser()
config.read("")

run(config)
