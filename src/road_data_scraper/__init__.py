import logging
import os
import tempfile
from pathlib import Path

from pkg_resources import get_distribution

tmp_log_dir = tempfile.TemporaryDirectory()
TMP_LOG_PATH = Path(f"{tmp_log_dir.name}/road_data_scraper.log")

logging.basicConfig(
    format="%(asctime)s.%(msecs)03d %(module)s %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(
            TMP_LOG_PATH,
        ),
    ],
)

__version__ = get_distribution("road_data_scraper").version

package_path = Path(__file__).parent
os.chdir(package_path)
