"""
FastAPI Module
--------------
This module provides the FastAPI web service for the Road Data Scraper. The scraper extracts data
from the Highways England WebTRIS Traffic Flow API, cleanses it, and stores it in a Google Cloud Bucket.

The Road Data Scraper API allows users to specify configuration options such as the data's start and end
dates, whether to perform a test run, and whether to generate an HTML report. This report displays the active
and inactive IDs for each type of road sensor: MIDAS, TMU, and TAME.

Modules:
    fastapi: Provides the FastAPI framework to build the web service.
    road_data_scraper: This is the main script to run the data scraping and cleaning process.

Routes:
    /: Redirects to the API documentation.
    /scrape: Takes configuration options as input, performs the data scraping, and returns a success message.

Configuration Options:
    start_date (str): The start date for the data scraping, formatted as %Y-%m-%d. Optional.
    end_date (str): The end date for the data scraping, formatted as %Y-%m-%d. Optional.
    test_run (bool): If True, a test run will be performed on a subset of URLs. If False, the entire dataset
                      will be downloaded. Defaults to True.
    generate_report (bool): If True, an HTML report will be generated. Defaults to True.
    output_path (str): The directory where the output will be saved.
    rm_dir (bool): If True, the output directory will be removed before the data scraping starts.
    gcp_storage (bool): If True, the data will be stored in a Google Cloud Bucket.
    gcp_credentials (str): The path to the Google Cloud credentials file. Optional.
    gcp_bucket_name (str): The name of the Google Cloud Bucket where the data will be stored. Optional.
    gcp_blob_name (str): The name of the blob where the data will be stored in the Google Cloud Bucket.
                         Defaults to 'landing_zone'.
"""
from datetime import date
from typing import Optional

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from road_data_scraper import __version__
from road_data_scraper.main import run

description = """
The Road Data Scraper API is a straightforward tool designed to fetch and sanitize data from
the Highways England WebTRIS Traffic Flow API. This API allows you to tailor the data retrieval
process to your specific needs.

Once processed, the cleaned data can be conveniently stored in a Google Cloud Bucket.
Alternatively, if you're running the API on your local machine, the data can be saved there.

With this API, you can easily define the start and end dates for the data you wish to gather.
You also have the option to execute a test run – an ideal choice for those who want to ensure
everything runs smoothly before committing to a full data download. In addition, the API gives
you the choice to generate an HTML report, offering a comprehensive overview of the status of
each road sensor, including MIDAS, TMU, and TAME.

# How To Use

Using the API is easy. All you need to do is send a GET request to the `/scrape/` endpoint with the configuration parameters you want.

The configuration parameters include:

- __test_run__: True (default) or False. A value of True runs a test scrape on a subset of available URLs, while False will download the entire dataset.
- __generate_report__: True (default) or False. When set to True, the API generates an HTML report showing the Active and Inactive IDs for each road sensor (MIDAS, TMU, and TAME).
- __output_path__: The path where you want the data to be stored.
- __rm_dir__: True or False. Indicates whether you want to remove the directory after scraping the data.
- __gcp_storage__: True or False. Indicates whether you want to store the data in a Google Cloud Bucket.
- __start_date__: The date you want to start scraping data from, formatted as %Y-%m-%d.
- __end_date__: The date you want to stop scraping data at, formatted as %Y-%m-%d.
- __gcp_credentials__: The path to your Google Cloud Platform credentials file.
- __gcp_bucket_name__: The name of your Google Cloud Bucket.
- __gcp_blob_name__: The name of the blob in your Google Cloud Bucket where the data will be stored. The default value is "landing_zone".

There are two ways to interact with the Road Data Scraper API - via a `curl` command in your terminal or directly through the FastAPI interface.

### Curl Command

To use a curl command, simply send a GET request to the `/scrape/` endpoint with the configuration parameters you want. For example:

```bash
curl -X GET "http://localhost:8000/scrape/?test_run=True&generate_report=True&output_path=~/data/&rm_dir=False&gcp_storage=True&start_date=2022-01-01&end_date=2022-01-31&gcp_credentials=~/gcp_credentials.json&gcp_bucket_name=my_bucket&gcp_blob_name=landing_zone"
```

### FastAPI Interface

If you prefer a more interactive approach, you can use the built-in FastAPI interface. Here's how:

1. Open the FastAPI documentation page by navigating to the `/docs` endpoint of your API, such as `http://localhost:8000/docs`.
2. Locate the `/scrape/` endpoint in the list of available endpoints.
3. Click on it to expand the endpoint's details. Here, you'll find information about the expected parameters and their types.
4. Click the __"Try it out"__ button. This will make the parameter fields editable.
5. Fill in the fields with the parameters you wish to use. Remember to stick to the expected format for each field.
6. Once you've filled in all the parameters, click __"Execute"__ to run the request. The API will process the request and return a response in the same window.

# API Response

On successful execution of the scraping pipeline, the API returns a simple text message -
__"WebTRIS Scraping Pipeline Successfully Executed."__. In case of any errors during execution,
the API provides a relevant error message detailing what went wrong.

# Error Handling

The API comes equipped with built-in error handling mechanisms. If an error occurs during
the data scraping process, the API will retry the request. If the error persists, it will be logged,
and the API will move on to the next request. Errors and their corresponding details can be found in the API logs.

# Useful Links

- [WebTRIS Traffic Flow API](https://webtris.highwaysengland.co.uk/api/swagger/ui/index)
- [Road Data Scraper GitHub Repository](https://github.com/dombean/road_data_scraper)
"""
app = FastAPI(
    title="Road Data Scraper API",
    description=description,
    version=__version__,
)


@app.get("/", tags=["Road Data Scraper"])
def read_docs():
    return RedirectResponse("/docs")


@app.get("/scrape/", tags=["Road Data Scraper"])
def scrape_webtris_api(
    test_run: bool,
    generate_report: bool,
    output_path: str,
    rm_dir: bool,
    gcp_storage: bool,
    start_date: Optional[date] = "",
    end_date: Optional[date] = "",
    gcp_credentials: Optional[str] = None,
    gcp_bucket_name: Optional[str] = None,
    gcp_blob_name: Optional[str] = "landing_zone",
):
    config = {
        "user_settings": {
            "start_date": str(start_date),
            "end_date": str(end_date),
            "test_run": test_run,
            "generate_report": generate_report,
            "output_path": output_path,
            "rm_dir": rm_dir,
            "gcp_storage": gcp_storage,
            "gcp_credentials": gcp_credentials,
            "gcp_bucket_name": gcp_bucket_name,
            "gcp_blob_name": gcp_blob_name,
        }
    }

    run(config, api_run=True)

    return "WebTRIS Scraping Pipeline Successfully Executed."
