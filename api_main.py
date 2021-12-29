from datetime import date
from typing import Optional

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from road_data_scraper import __version__
from road_data_scraper.main import run

app = FastAPI(
    title="Road Data Scraper API",
    description="Scrapes and Cleans WebTRIS Traffic Flow API",
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

    return "Success"
